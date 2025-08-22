"""
Main tools module that registers all MCP tools with the FastMCP server.
"""

from services import (
    IssueService, 
    TimeEntryService, 
    ProjectService, 
    UserService, 
    TrackerService, 
    IssueStatusService, 
    ProjectMembershipService
)

from .issue_tools import register_issue_tools
from .user_tools import register_user_tools
from .time_entry_tools import register_time_entry_tools
from .tracker_tools import register_tracker_tools
from .project_tools import register_project_tools


def register_tools(mcp, issue_service: IssueService, time_entry_service: TimeEntryService, 
                  project_service: ProjectService, user_service: UserService, 
                  tracker_service: TrackerService, issue_status_service: IssueStatusService,
                  membership_service: ProjectMembershipService, redmine):
    """Register all MCP tools with the FastMCP server"""
    
    # Register issue-related tools
    register_issue_tools(mcp, issue_service)
    
    # Register user-related tools
    register_user_tools(mcp, user_service)
    
    # Register time entry-related tools
    register_time_entry_tools(mcp, time_entry_service, redmine)
    
    # Register tracker and status-related tools
    register_tracker_tools(mcp, tracker_service, issue_status_service, redmine)
    
    # Register project-related tools
    register_project_tools(mcp, project_service, membership_service, issue_service)
