def format_tool_result(tool_name: str, result: dict) -> str:
    """
    Formats the structured tool output into a string that can be fed back into Gemini
    as part of the ongoing prompt.

    Args:
        tool_name (str): The tool that was called.
        result (dict): The output returned by the tool.

    Returns:
        str: Formatted summary to re-inject into the LLM.
    """
    if tool_name == "compare_net_income":
        lines = ["Comparison of Net Income:"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "cash_flow":
        comparison = result.get("comparison", {})
        lines = ["Comparison of Cash Flow:"]
        
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            for year, data in yearly_data.items():
                lines.append(f"  {year}:")
                 
                # 🔁 Case 1: Full cash flow dict is present (user asked for "cash flow")
                if isinstance(data, dict) and all(key in data for key in [
                    "cash from operating activities", "cash from investing activities",
                    "cash from financing activities", "net cash flow"
                ]):
                    lines.append(f"    Cash from Operating Activities: {data.get('cash from operating activities', 'N/A')}")
                    lines.append(f"    Cash from Investing Activities: {data.get('cash from investing activities', 'N/A')}")
                    lines.append(f"    Cash from Financing Activities: {data.get('cash from financing activities', 'N/A')}")
                    lines.append(f"    Net Cash Flow: {data.get('net cash flow', 'N/A')}")

                # 🔁 Case 2: Only partial/individual fields requested
                elif isinstance(data, dict):
                    for label, value in data.items():
                        lines.append(f"    {label.title()}: {value}")

                else:
                    lines.append("    No data available.")

        return "\n".join(lines)

    elif tool_name == "summarize_balance_sheet":
        
        comparison = result.get("comparison", {})
        lines = ["Comparison of Balance Sheet:"]

        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            for year, data in yearly_data.items():
                lines.append(f"  {year}:")
                
                if isinstance(data, dict):
                    for label, value in data.items():
                        lines.append(f"    {label.title()}: {value}")

                else:
                    lines.append("    No data available.")

        return "\n".join(lines)
    

    elif tool_name == "compare_quarterly_income":
        lines = ["Comparison of Quarterly Income:"]
        comparison = result.get("comparison", {})
        
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    else:
        return "No context available for the requested tool."


def build_context(tool_name: str, tool_result: dict) -> str:
    """
    Prepares a formatted string that represents the context derived from tool results,
    to be inserted into the next Gemini prompt.

    Args:
        tool_name (str): The name of the tool that was used.
        tool_result (dict): The output dictionary returned by the tool.

    Returns:
        str: Context string to be added to LLM prompt.
    """
    formatted = format_tool_result(tool_name, tool_result)
    return f"\n\n[Context based on tool result]\n{formatted}"




