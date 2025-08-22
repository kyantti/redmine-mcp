"""
Base functionality for MCP tools.
"""


def format_error(result) -> str:
    """Format error message from operation result"""
    return f"❌ {result.message}\nError: {result.error}"


def safe_format_field(value, default="Not assigned") -> str:
    """Safely format a field value, handling None and empty values"""
    if value is None or value == "" or value == default:
        return default
    return str(value)
