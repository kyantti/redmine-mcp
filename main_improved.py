import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from redminelib import Redmine
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("redmine")

# Redmine configuration from environment variables
REDMINE_URL = os.getenv("REDMINE_URL")
API_KEY = os.getenv("REDMINE_API_KEY")
USERNAME = os.getenv("REDMINE_USERNAME")
PASSWORD = os.getenv("REDMINE_PASSWORD")

# Validate required environment variables
if not all([REDMINE_URL, USERNAME, PASSWORD]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Initialize the Redmine client
redmine = Redmine(url=REDMINE_URL, username=USERNAME, password=PASSWORD)


# ============================================================================
# DESIGN PATTERNS IMPLEMENTATION
# ============================================================================

@dataclass
class OperationResult:
    """Data class to standardize operation results"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RedmineService(ABC):
    """Abstract base class for Redmine services following Repository pattern"""
    
    def __init__(self, redmine_client):
        self.redmine = redmine_client
    
    @abstractmethod
    def get_by_id(self, id: int) -> OperationResult:
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> OperationResult:
        pass
    
    @abstractmethod
    def update(self, id: int, data: Dict[str, Any]) -> OperationResult:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> OperationResult:
        pass


class IssueService(RedmineService):
    """Service class for Issue operations following Repository pattern"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            issue = self.redmine.issue.get(id)
            return OperationResult(
                success=True,
                message=f"Issue {id} retrieved successfully",
                data={
                    "id": issue.id,
                    "subject": issue.subject,
                    "description": getattr(issue, "description", "No description"),
                    "status": issue.status.name,
                    "priority": issue.priority.name,
                    "tracker": issue.tracker.name,
                    "project": issue.project.name,
                    "author": issue.author.name,
                    "assigned_to": getattr(issue, "assigned_to", {}).get("name", "Unassigned"),
                    "created_on": str(issue.created_on),
                    "updated_on": str(issue.updated_on),
                    "due_date": getattr(issue, "due_date", "Not set")
                }
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve issue {id}",
                error=str(e)
            )
    
    def create(self, data: Dict[str, Any]) -> OperationResult:
        try:
            new_issue = self.redmine.issue.create(**data)
            return OperationResult(
                success=True,
                message=f"Issue created successfully with ID {new_issue.id}",
                data={"id": new_issue.id, "subject": data.get("subject")}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message="Failed to create issue",
                error=str(e)
            )
    
    def update(self, id: int, data: Dict[str, Any]) -> OperationResult:
        try:
            self.redmine.issue.update(id, **data)
            return OperationResult(
                success=True,
                message=f"Issue {id} updated successfully",
                data={"id": id, "updated_fields": list(data.keys())}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to update issue {id}",
                error=str(e)
            )
    
    def delete(self, id: int) -> OperationResult:
        try:
            self.redmine.issue.delete(id)
            return OperationResult(
                success=True,
                message=f"Issue {id} deleted successfully"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to delete issue {id}",
                error=str(e)
            )


class TimeEntryService(RedmineService):
    """Service class for Time Entry operations following Repository pattern"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            entry = self.redmine.time_entry.get(id)
            return OperationResult(
                success=True,
                message=f"Time entry {id} retrieved successfully",
                data={
                    "id": entry.id,
                    "hours": entry.hours,
                    "comments": getattr(entry, "comments", ""),
                    "spent_on": str(entry.spent_on),
                    "user": entry.user.name,
                    "activity": entry.activity.name,
                    "project": entry.project.name,
                    "issue": getattr(entry, "issue", {}).get("id", "No issue")
                }
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve time entry {id}",
                error=str(e)
            )
    
    def create(self, data: Dict[str, Any]) -> OperationResult:
        try:
            new_entry = self.redmine.time_entry.create(**data)
            return OperationResult(
                success=True,
                message=f"Time entry created successfully with ID {new_entry.id}",
                data={"id": new_entry.id, "hours": data.get("hours")}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message="Failed to create time entry",
                error=str(e)
            )
    
    def update(self, id: int, data: Dict[str, Any]) -> OperationResult:
        try:
            self.redmine.time_entry.update(id, **data)
            return OperationResult(
                success=True,
                message=f"Time entry {id} updated successfully",
                data={"id": id, "updated_fields": list(data.keys())}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to update time entry {id}",
                error=str(e)
            )
    
    def delete(self, id: int) -> OperationResult:
        try:
            self.redmine.time_entry.delete(id)
            return OperationResult(
                success=True,
                message=f"Time entry {id} deleted successfully"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to delete time entry {id}",
                error=str(e)
            )


# Initialize services (Dependency Injection pattern)
issue_service = IssueService(redmine)
time_entry_service = TimeEntryService(redmine)


# ============================================================================
# ENHANCED MCP TOOLS WITH CRUD OPERATIONS
# ============================================================================

@mcp.tool()
def update_issue(
    issue_id: int,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    status_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
    due_date: Optional[str] = None
) -> str:
    """Update an existing issue.
    
    Args:
        issue_id: The ID of the issue to update
        subject: New subject (optional)
        description: New description (optional)
        status_id: New status ID (optional)
        priority_id: New priority ID (optional)
        assigned_to_id: ID of user to assign to (optional)
        due_date: Due date in YYYY-MM-DD format (optional)
    """
    update_data = {}
    
    if subject is not None:
        update_data["subject"] = subject
    if description is not None:
        update_data["description"] = description
    if status_id is not None:
        update_data["status_id"] = status_id
    if priority_id is not None:
        update_data["priority_id"] = priority_id
    if assigned_to_id is not None:
        update_data["assigned_to_id"] = assigned_to_id
    if due_date is not None:
        update_data["due_date"] = due_date
    
    if not update_data:
        return "Error: No fields provided to update"
    
    result = issue_service.update(issue_id, update_data)
    
    if result.success:
        return f"✅ {result.message}\nUpdated fields: {', '.join(result.data['updated_fields'])}"
    else:
        return f"❌ {result.message}\nError: {result.error}"


@mcp.tool()
def delete_issue(issue_id: int) -> str:
    """Delete an issue.
    
    Args:
        issue_id: The ID of the issue to delete
    """
    result = issue_service.delete(issue_id)
    
    if result.success:
        return f"✅ {result.message}"
    else:
        return f"❌ {result.message}\nError: {result.error}"


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
        return f"✅ {result.message}\nUpdated fields: {', '.join(result.data['updated_fields'])}"
    else:
        return f"❌ {result.message}\nError: {result.error}"


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


@mcp.tool()
def get_project_members(project_id: int) -> str:
    """Get all members of a project.
    
    Args:
        project_id: The ID of the project
    """
    try:
        project = redmine.project.get(project_id)
        memberships = redmine.project_membership.filter(project_id=project_id)
        
        result = [f"Members of Project '{project.name}' (ID: {project_id}):"]
        
        for member in memberships:
            user_info = f"ID: {member.user.id} - Name: {member.user.name}"
            if hasattr(member, 'roles'):
                roles = [role.name for role in member.roles]
                user_info += f" - Roles: {', '.join(roles)}"
            result.append(user_info)
        
        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving project members: {str(e)}"


# Include all the original functions from the current main.py
# (The rest of the existing functions would go here...)

if __name__ == "__main__":
    mcp.run(transport="stdio")
