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

    elif tool_name == "summarize_balance_sheet":
        company = result.get("company", "")
        year = result.get("year", "")
        summary = result.get("summary", {})
        lines = [f"Balance Sheet Summary for {company} ({year}):"]
        for item, value in summary.items():
            lines.append(f"  {item}: {value}")
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
