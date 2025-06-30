import streamlit as st
import sys
import os

# Add root directory to path for local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.prompt_builder import build_prompt
from llm.gemini_client import run_gemini_prompt
from llm.tool_router import extract_tool_call
from llm.context_manager import build_context
from mcp_server.tools import call_tool

st.set_page_config(page_title="Finance AI Assistant")

st.title("Ask a financial question about HDFC, ICICI, or other companies.")

user_query = st.text_input("Enter your question")

if st.button("Submit") and user_query.strip():
    try:
        # Step 1: Build prompt
        st.markdown("#### Step 1: Building Prompt")
        st.write(f"User question: {user_query}")
        initial_prompt = build_prompt(user_query)

        # Step 2: Run Gemini prompt to detect tool call
        tool_response = run_gemini_prompt(initial_prompt)
        tool_call = extract_tool_call(tool_response)

        if tool_call:
            # Tool call detected
            tool_name = tool_call["tool_name"]
            parameters = tool_call["parameters"]

            st.markdown("#### Step 2: Tool Detected")
            st.write(f"**Tool**: `{tool_name}`")
            st.write(f"**Parameters**: {parameters}")

            # Step 3: Call tool and get result
            tool_result = call_tool(tool_name, parameters)

            st.markdown("#### Step 3: Tool Output")
            st.json(tool_result)

            # Step 4: Build new prompt with context
            context = build_context(tool_name, tool_result)
            final_prompt = f"{initial_prompt}\n\nTool Output:\n{context}"
            final_response = run_gemini_prompt(final_prompt)

            st.markdown("#### Final Answer:")
            st.write(final_response)

        else:
            # No tool detected – fallback to generic Gemini output
            st.markdown("#### Gemini Answer:")
            st.write(tool_response)

    except Exception as e:
        st.error(f"An error occurred: {e}")
