"""
Time Entry-related MCP tools for Redmine operations.
"""

from typing import Optional
from services import TimeEntryService
from .base_tools import format_error


def register_time_entry_tools(mcp, time_entry_service: TimeEntryService, redmine):
    """Register time entry-related MCP tools with the FastMCP server"""
    
    @mcp.tool()
    def create_time_entry(
        issue_id: int,
        hours: float,
        comments: str,
        spent_on: str,
        activity_id: Optional[int] = None
    ) -> str:
        """Create a new time entry.
        
        Args:
            issue_id: The ID of the issue to log time for
            hours: Hours to log
            comments: Comments for the time entry
            spent_on: Date in YYYY-MM-DD format
            activity_id: Activity ID (optional, will use default if not provided)
        """
        time_data = {
            "issue_id": issue_id,
            "hours": hours,
            "comments": comments,
            "spent_on": spent_on
        }
        
        if activity_id is not None:
            time_data["activity_id"] = activity_id
        
        result = time_entry_service.create(time_data)
        
        if result.success:
            return f"✅ {result.message}"
        else:
            return format_error(result)

    @mcp.tool()
    def update_time_entry(
        time_entry_id: int,
        hours: Optional[float] = None,
        comments: Optional[str] = None,
        spent_on: Optional[str] = None,
        activity_id: Optional[int] = None
    ) -> str:
        """Update an existing time entry.
        
        Args:
            time_entry_id: The ID of the time entry to update
            hours: New hours value (optional)
            comments: New comments (optional)
            spent_on: New date in YYYY-MM-DD format (optional)
            activity_id: New activity ID (optional)
        """
        update_data = {}
        
        if hours is not None:
            update_data["hours"] = hours
        if comments is not None:
            update_data["comments"] = comments
        if spent_on is not None:
            update_data["spent_on"] = spent_on
        if activity_id is not None:
            update_data["activity_id"] = activity_id
        
        if not update_data:
            return "Error: No fields provided to update"
        
        result = time_entry_service.update(time_entry_id, update_data)
        
        if result.success:
            updated_fields = result.data.get('updated_fields', []) if result.data else []
            return f"✅ {result.message}\nUpdated fields: {', '.join(updated_fields)}"
        else:
            return format_error(result)

    @mcp.tool()
    def get_time_activities() -> str:
        """Get all available time tracking activities."""
        try:
            activities = redmine.time_entry_activity.all()
            result = ["Available Time Entry Activities:"]
            
            for activity in activities:
                result.append(f"ID: {activity.id} - Name: {activity.name}")
            
            return "\n".join(result)
        except Exception as e:
            return f"Error retrieving time entry activities: {str(e)}"

    @mcp.tool()
    def get_time_entries_by_issue(issue_id: int) -> str:
        """Get all time entries for a specific issue.
        
        Args:
            issue_id: The ID of the issue
        """
        result = time_entry_service.get_all(issue_id=issue_id)
        
        if result.success:
            entries_data = result.data.get("time_entries", []) if result.data else []
            
            if not entries_data:
                return f"No time entries found for issue #{issue_id}."
            
            output = [f"Time entries for Issue #{issue_id}:"]
            total_hours = 0
            
            for entry in entries_data:
                entry_info = f"\n#{entry['id']}: {entry['hours']} hours"
                entry_info += f"\n  User: {entry['user']}"
                entry_info += f"\n  Activity: {entry['activity']}"
                entry_info += f"\n  Date: {entry['spent_on']}"
                if entry.get('comments'):
                    entry_info += f"\n  Comments: {entry['comments']}"
                
                output.append(entry_info)
                total_hours += float(entry['hours']) if entry['hours'] else 0
            
            output.append(f"\nTotal hours logged: {total_hours}")
            return "\n".join(output)
        else:
            return format_error(result)

    @mcp.tool()
    def delete_time_entry(time_entry_id: int) -> str:
        """Delete a time entry.
        
        Args:
            time_entry_id: The ID of the time entry to delete
        """
        result = time_entry_service.delete(time_entry_id)
        
        if result.success:
            return f"✅ {result.message}"
        else:
            return format_error(result)
