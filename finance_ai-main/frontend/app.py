import streamlit as st
import sys
import os
from datetime import datetime

# Add root directory to path for local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.prompt_builder import build_prompt
from llm.gemini_client import run_gemini_prompt
from llm.tool_router import extract_tool_call
from llm.context_manager import build_context
from mcp_server.tools import call_tool

st.set_page_config(page_title="💹 Finance AI Assistant", layout="centered")

# ---------- GLOBAL STATE ----------
if "users" not in st.session_state:
    st.session_state.users = {}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ---------- CUSTOM STYLES ----------
st.markdown("""
    <style>
        body {
            background-color: #f9f9f9;
        }
        div.stButton > button {
            background-color: #3498DB;
            color: white;
            padding: 8px 20px;
            border-radius: 5px;
            font-weight: bold;
        }
        div.stTextInput > label {
            font-weight: bold;
            color: #2C3E50;
        }
        .main-title {
            background-color:#2C3E50;
            padding:10px;
            border-radius:10px;
            text-align:center;
            color:white;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="main-title"><h1>💹 Finance AI Assistant</h1><p>Ask questions about 3i Infotech, 20 Microns or others.</p></div>', unsafe_allow_html=True)

import json
import os

USER_DB_FILE = "user_db.json"

# Load user database
def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {}

# Save user database
def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

# ---------- signup ----------
def signup():
    users = load_users()
    st.markdown("<h3 style='color:#2C3E50;'>🆕 Sign Up</h3>", unsafe_allow_html=True)
    new_username = st.text_input("Create Username")
    new_password = st.text_input("Create Password", type="password")
    if st.button("Sign Up"):
        if new_username in users:
            st.warning("🚫 Username already exists.")
        elif new_username and new_password:
            users[new_username] = new_password
            save_users(users)
            st.success("✅ Signup successful! Please log in.")
        else:
            st.error("❗ Enter both username and password.")

# ---------- login ----------
def login():
    users = load_users()
    st.markdown("<h3 style='color:#2C3E50;'>🔐 Login</h3>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.authenticated = True
            st.session_state.current_user = username
            st.success(f"✅ Welcome, {username}!")
        else:
            st.error("❗ Invalid username or password.")



# ---------- LOGOUT ----------
def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.success("🚪 Logged out successfully!")


# ---------- FINANCE ASSISTANT ----------
def finance_assistant():
    st.markdown(f"<h3 style='color:#34495E;'>👋 Hello, {st.session_state.current_user}!</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color:#FDEBD0;padding:20px;border-radius:10px;margin-top:20px;">
            <h4 style="color:#D35400;">📊 Ask a Financial Question</h4>
        </div>
    """, unsafe_allow_html=True)

    user_query = st.text_input("Enter your question")
    if st.button("Submit") and user_query.strip():
        try:
            st.markdown("#### ✅ Step 1: Building Prompt")
            st.info(f"**User question**: {user_query}")
            initial_prompt = build_prompt(user_query)

            st.markdown("#### 🔍 Step 2: Detecting Tool Call")
            tool_call = extract_tool_call(initial_prompt)

            if tool_call:
                tool_name = tool_call["tool_name"]
                parameters = tool_call["parameters"]
                st.success(f"**Tool**: `{tool_name}`")
                st.json(parameters)

                st.markdown("#### 🛠 Step 3: Calling Tool")
                tool_result = call_tool(tool_name, parameters)
                if tool_result == "Unknown tool":
                    st.json("🔴 Data Not Found")

                else:
                    st.json(tool_result)
                    context = build_context(tool_name, tool_result)
                    final_prompt = f"{initial_prompt}\n\nTool Output:\n{context}"
                    final_response = run_gemini_prompt(final_prompt)

                    st.markdown("#### 🧠 Final Answer:")
                    st.write(final_response)
            else:
                st.warning("⚠️ No tool was detected for this query.")
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

    if st.button("Logout"):
        logout()


# ---------- APP ROUTING ----------
st.sidebar.title("🔑 Authentication")
auth_choice = st.sidebar.radio("Choose Option", ("Login", "Sign Up"))

if not st.session_state.authenticated:
    if auth_choice == "Sign Up":
        signup()
    else:
        login()
else:
    finance_assistant()
