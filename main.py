"""
Main entry point for the Redmine MCP server.
"""

from mcp.server.fastmcp import FastMCP
from config.config import config
from services import IssueService, TimeEntryService, ProjectService, UserService, TrackerService, IssueStatusService, ProjectMembershipService
from tools import register_tools

# Initialize FastMCP server
mcp = FastMCP("redmine")

# Initialize the Redmine client
redmine = config.create_client()

# Initialize services (Dependency Injection pattern)
issue_service = IssueService(redmine)
time_entry_service = TimeEntryService(redmine)
project_service = ProjectService(redmine)
user_service = UserService(redmine)
tracker_service = TrackerService(redmine)
issue_status_service = IssueStatusService(redmine)
membership_service = ProjectMembershipService(redmine)

# Register all MCP tools
register_tools(mcp, issue_service, time_entry_service, project_service, 
               user_service, tracker_service, issue_status_service, membership_service, redmine)

if __name__ == "__main__":
    mcp.run(transport="stdio")
