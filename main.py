"""
Main entry point for the Redmine MCP server.
"""

from mcp.server.fastmcp import FastMCP
from config.config import config
from services import (
    IssueService,
    TimeEntryService,
    ProjectService,
    UserService,
    TrackerService,
)
from tools.issue_tools import register_issue_tools
from tools.project_tools import register_project_tools
from tools.time_entry_tools import register_time_entry_tools
from tools.tracker_tools import register_tracker_tools
from tools.user_tools import register_user_tools

# Initialize FastMCP server
mcp = FastMCP("redmine")

# Initialize the Redmine client
redmine = config.create_client()

# Initialize services (Dependency Injection pattern)
issue_service = IssueService(redmine)
project_service = ProjectService(redmine)
time_entry_service = TimeEntryService(redmine)
user_service = UserService(redmine)
tracker_service = TrackerService(redmine)

# Register all MCP tools
register_issue_tools(mcp, issue_service)
register_project_tools(mcp, project_service, issue_service)
register_time_entry_tools(mcp, time_entry_service, redmine)
register_tracker_tools(mcp, tracker_service, redmine)
register_user_tools(mcp, user_service)

if __name__ == "__main__":
    mcp.run(transport="stdio")
