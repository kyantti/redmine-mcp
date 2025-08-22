"""
Tracker and Status-related MCP tools for Redmine operations.
"""

from services import TrackerService, IssueStatusService
from .base_tools import format_error


def register_tracker_tools(mcp, tracker_service: TrackerService, issue_status_service: IssueStatusService, redmine):
    """Register tracker and status-related MCP tools with the FastMCP server"""
    
    @mcp.tool()
    def get_trackers() -> str:
        """Get a list of all available trackers."""
        result = tracker_service.get_all()
        
        if result.success:
            trackers_data = result.data.get("trackers", []) if result.data else []
            if not trackers_data:
                return "No trackers found."
            
            output = ["Available Trackers:"]
            for tracker in trackers_data:
                tracker_info = f"ID: {tracker['id']} - Name: {tracker['name']}"
                if tracker.get('description') and tracker['description'] != "No description":
                    tracker_info += f" - Description: {tracker['description']}"
                output.append(tracker_info)
            
            return "\n".join(output)
        else:
            return format_error(result)

    @mcp.tool()
    def get_issue_statuses() -> str:
        """Get all available issue statuses."""
        try:
            statuses = redmine.issue_status.all()
            result = ["Available Issue Statuses:"]
            
            for status in statuses:
                result.append(f"ID: {status.id} - Name: {status.name}")
            
            return "\n".join(result)
        except Exception as e:
            return f"Error retrieving issue statuses: {str(e)}"

    @mcp.tool()
    def get_issue_priorities() -> str:
        """Get all available issue priorities."""
        try:
            priorities = redmine.issue_priority.all()
            result = ["Available Issue Priorities:"]
            
            for priority in priorities:
                result.append(f"ID: {priority.id} - Name: {priority.name}")
            
            return "\n".join(result)
        except Exception as e:
            return f"Error retrieving issue priorities: {str(e)}"
