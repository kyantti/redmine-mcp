"""
MCP tools for Redmine operations.
"""

from typing import Optional, Dict, Any
from services import IssueService, TimeEntryService, ProjectService, UserService, TrackerService, IssueStatusService, ProjectMembershipService


def register_tools(mcp, issue_service: IssueService, time_entry_service: TimeEntryService, 
                  project_service: ProjectService, user_service: UserService, 
                  tracker_service: TrackerService, issue_status_service: IssueStatusService,
                  membership_service: ProjectMembershipService, redmine):
    """Register all MCP tools with the FastMCP server"""
    
    @mcp.tool()
    def get_issue(issue_id: int) -> str:
        """Get detailed information about a specific issue.
        
        Args:
            issue_id: The ID of the issue to retrieve
        """
        result = issue_service.get_by_id(issue_id)
        
        if result.success:
            issue = result.data
            if not issue:
                return "❌ No issue data returned"
                
            output = [f"Issue #{issue['id']}: {issue['subject']}"]
            output.append(f"Description: {issue['description']}")
            output.append(f"Status: {issue['status']}")
            output.append(f"Priority: {issue['priority']}")
            output.append(f"Tracker: {issue['tracker']}")
            output.append(f"Project: {issue['project']}")
            output.append(f"Author: {issue['author']}")
            output.append(f"Assigned to: {issue['assigned_to']}")
            
            if issue.get('category') and issue['category'] != "Not assigned":
                output.append(f"Category: {issue['category']}")
            if issue.get('fixed_version') and issue['fixed_version'] != "Not assigned":
                output.append(f"Target version: {issue['fixed_version']}")
            
            output.append(f"Start date: {issue['start_date']}")
            output.append(f"Due date: {issue['due_date']}")
            output.append(f"Progress: {issue['done_ratio']}%")
            output.append(f"Estimated hours: {issue['estimated_hours']}")
            output.append(f"Spent hours: {issue['spent_hours']}")
            output.append(f"Created: {issue['created_on']}")
            output.append(f"Updated: {issue['updated_on']}")
            
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"

    @mcp.tool()
    def get_users() -> str:
        """Get a list of all users."""
        result = user_service.get_all()
        
        if result.success:
            users_data = result.data.get("users", []) if result.data else []
            if not users_data:
                return "No users found."
            
            output = ["Available Users:"]
            for user in users_data:
                user_info = f"ID: {user['id']} - {user['firstname']} {user['lastname']}"
                if user.get('login'):
                    user_info += f" (Login: {user['login']})"
                if user.get('mail'):
                    user_info += f" - Email: {user['mail']}"
                output.append(user_info)
            
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"

    @mcp.tool()
    def get_user(user_id: int) -> str:
        """Get detailed information about a specific user.
        
        Args:
            user_id: The ID of the user to retrieve
        """
        result = user_service.get_by_id(user_id)
        
        if result.success:
            user = result.data
            if not user:
                return "❌ No user data returned"
                
            output = [f"User #{user['id']}: {user['firstname']} {user['lastname']}"]
            output.append(f"Login: {user['login']}")
            output.append(f"Email: {user['mail']}")
            output.append(f"Status: {user['status']}")
            output.append(f"Created: {user['created_on']}")
            output.append(f"Last login: {user['last_login_on']}")
            
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"

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
            return f"❌ {result.message}\nError: {result.error}"

    @mcp.tool()
    def create_issue(
        project_id: int,
        tracker_id: int,
        subject: str,
        description: Optional[str] = None,
        status_id: Optional[int] = None,
        priority_id: Optional[int] = None,
        assigned_to_id: Optional[int] = None,
        due_date: Optional[str] = None
    ) -> str:
        """Create a new issue.
        
        Args:
            project_id: The ID of the project
            tracker_id: The ID of the tracker
            subject: The subject/title of the issue
            description: Description of the issue (optional)
            status_id: Status ID (optional)
            priority_id: Priority ID (optional)
            assigned_to_id: ID of user to assign to (optional)
            due_date: Due date in YYYY-MM-DD format (optional)
        """
        issue_data = {
            "project_id": project_id,
            "tracker_id": tracker_id,
            "subject": subject
        }
        
        if description is not None:
            issue_data["description"] = description
        if status_id is not None:
            issue_data["status_id"] = status_id
        if priority_id is not None:
            issue_data["priority_id"] = priority_id
        if assigned_to_id is not None:
            issue_data["assigned_to_id"] = assigned_to_id
        if due_date is not None:
            issue_data["due_date"] = due_date
        
        result = issue_service.create(issue_data)
        
        if result.success:
            return f"✅ {result.message}"
        else:
            return f"❌ {result.message}\nError: {result.error}"

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
            updated_fields = result.data.get('updated_fields', []) if result.data else []
            return f"✅ {result.message}\nUpdated fields: {', '.join(updated_fields)}"
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
            updated_fields = result.data.get('updated_fields', []) if result.data else []
            return f"✅ {result.message}\nUpdated fields: {', '.join(updated_fields)}"
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
        result = membership_service.get_by_project(project_id)
        
        if result.success:
            memberships_data = result.data.get("memberships", []) if result.data else []
            
            if not memberships_data:
                # Get project name for better error message
                project_result = project_service.get_by_id(project_id)
                project_name = project_result.data.get("name", f"Project {project_id}") if project_result.success and project_result.data else f"Project {project_id}"
                return f"No members found for project '{project_name}' (ID: {project_id})"
            
            # Get project name for display
            project_result = project_service.get_by_id(project_id)
            project_name = project_result.data.get("name", f"Project {project_id}") if project_result.success and project_result.data else f"Project {project_id}"
            
            output = [f"Members of Project '{project_name}' (ID: {project_id}):"]
            
            for membership in memberships_data:
                user_info = f"ID: {membership['user_id']} - Name: {membership['user']}"
                if membership.get('roles'):
                    user_info += f" - Roles: {', '.join(membership['roles'])}"
                output.append(user_info)
            
            output.append(f"\nTotal members: {len(memberships_data)}")
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"

    @mcp.tool()
    def get_projects() -> str:
        """Get a list of all available projects.
        
        Returns:
            A formatted list of all projects with their basic information
        """
        result = project_service.get_all()
        
        if result.success:
            projects_data = result.data.get("projects", []) if result.data else []
            if not projects_data:
                return "No projects found."
            
            output = ["Available Projects:"]
            for project in projects_data:
                project_info = f"ID: {project['id']} - Name: {project['name']}"
                if project.get('identifier'):
                    project_info += f" (Identifier: {project['identifier']})"
                if project.get('description') and project['description'] != "No description":
                    # Truncate long descriptions
                    desc = project['description'][:100] + "..." if len(project['description']) > 100 else project['description']
                    project_info += f" - Description: {desc}"
                if project.get('status') and project['status'] != "Unknown":
                    project_info += f" - Status: {project['status']}"
                
                output.append(project_info)
            
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"

    @mcp.tool()
    def get_project_issues(project_id: int, limit: int = 25, status_id: Optional[int] = None) -> str:
        """Get issues for a specific project using the service layer.
        
        Args:
            project_id: The ID of the project
            limit: Maximum number of issues to retrieve (default: 25)
            status_id: Filter by status ID (optional)
        """
        # Build filter parameters
        filter_params = {"project_id": project_id, "limit": limit}
        if status_id is not None:
            filter_params["status_id"] = status_id
        
        # Get issues using the service
        result = issue_service.get_all(**filter_params)
        
        if result.success:
            issues_data = result.data.get("issues", []) if result.data else []
            
            # Get project name for display
            project_result = project_service.get_by_id(project_id)
            project_name = project_result.data.get("name", f"Project {project_id}") if project_result.success and project_result.data else f"Project {project_id}"
            
            output = [f"Issues for Project '{project_name}' (ID: {project_id}):"]
            if status_id:
                output[0] += f" - Filtered by Status ID: {status_id}"
            
            if not issues_data:
                output.append("No issues found for this project.")
                return "\n".join(output)
            
            for issue in issues_data:
                issue_info = f"\n#{issue['id']}: {issue['subject']}"
                issue_info += f"\n  Status: {issue['status']}"
                issue_info += f"\n  Priority: {issue['priority']}"
                issue_info += f"\n  Tracker: {issue['tracker']}"
                issue_info += f"\n  Assigned to: {issue['assigned_to']}"
                issue_info += f"\n  Created: {issue['created_on']}"
                issue_info += f"\n  Updated: {issue['updated_on']}"
                
                if issue.get('due_date') and issue['due_date'] != "Not set":
                    issue_info += f"\n  Due date: {issue['due_date']}"
                
                output.append(issue_info)
            
            output.append(f"\nShowing {len(issues_data)} issue(s)")
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"

    @mcp.tool()
    def get_issues_by_subject(subject: str, project_id: Optional[int] = None, limit: int = 25) -> str:
        """Search for issues by subject/name.
        
        Args:
            subject: The subject text to search for (case-insensitive partial match)
            project_id: Optional project ID to limit search to specific project
            limit: Maximum number of issues to search through (default: 25)
        """
        result = issue_service.get_by_subject(subject, project_id, limit)
        
        if result.success:
            issues_data = result.data.get("issues", []) if result.data else []
            
            if not issues_data:
                project_info = f" in project {project_id}" if project_id else ""
                return f"No issues found matching '{subject}'{project_info}."
            
            output = [f"Issues matching '{subject}':"]
            if project_id:
                output[0] += f" (Project ID: {project_id})"
            
            for issue in issues_data:
                issue_info = f"\n#{issue['id']}: {issue['subject']}"
                issue_info += f"\n  Project: {issue['project']}"
                issue_info += f"\n  Status: {issue['status']}"
                issue_info += f"\n  Priority: {issue['priority']}"
                issue_info += f"\n  Tracker: {issue['tracker']}"
                issue_info += f"\n  Assigned to: {issue['assigned_to']}"
                issue_info += f"\n  Created: {issue['created_on']}"
                issue_info += f"\n  Updated: {issue['updated_on']}"
                
                if issue.get('due_date') and issue['due_date'] != "Not set":
                    issue_info += f"\n  Due date: {issue['due_date']}"
                
                output.append(issue_info)
            
            output.append(f"\nFound {len(issues_data)} matching issue(s)")
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"

    @mcp.tool()
    def search_issues(
        subject: Optional[str] = None,
        project_id: Optional[int] = None,
        status_id: Optional[int] = None,
        assigned_to_id: Optional[int] = None,
        limit: int = 25
    ) -> str:
        """Advanced search for issues with multiple filters.
        
        Args:
            subject: Search text in issue subject (optional)
            project_id: Filter by project ID (optional)
            status_id: Filter by status ID (optional)
            assigned_to_id: Filter by assigned user ID (optional)
            limit: Maximum number of issues to retrieve (default: 25)
        """
        # Build filter parameters (excluding subject which is handled separately)
        filter_params: Dict[str, Any] = {"limit": limit}
        if project_id is not None:
            filter_params["project_id"] = project_id
        if status_id is not None:
            filter_params["status_id"] = status_id
        if assigned_to_id is not None:
            filter_params["assigned_to_id"] = assigned_to_id
        
        # Add subject separately since it's handled as a string filter
        if subject is not None:
            filter_params["subject"] = subject
        
        result = issue_service.get_all(**filter_params)
        
        if result.success:
            issues_data = result.data.get("issues", []) if result.data else []
            
            if not issues_data:
                return "No issues found matching the specified criteria."
            
            # Build header with applied filters
            filters = []
            if subject:
                filters.append(f"Subject contains '{subject}'")
            if project_id:
                filters.append(f"Project ID: {project_id}")
            if status_id:
                filters.append(f"Status ID: {status_id}")
            if assigned_to_id:
                filters.append(f"Assigned to ID: {assigned_to_id}")
            
            header = "Search Results"
            if filters:
                header += f" (Filters: {', '.join(filters)})"
            
            output = [header + ":"]
            
            for issue in issues_data:
                issue_info = f"\n#{issue['id']}: {issue['subject']}"
                issue_info += f"\n  Project: {issue['project']}"
                issue_info += f"\n  Status: {issue['status']}"
                issue_info += f"\n  Priority: {issue['priority']}"
                issue_info += f"\n  Tracker: {issue['tracker']}"
                issue_info += f"\n  Assigned to: {issue['assigned_to']}"
                issue_info += f"\n  Created: {issue['created_on']}"
                issue_info += f"\n  Updated: {issue['updated_on']}"
                
                if issue.get('due_date') and issue['due_date'] != "Not set":
                    issue_info += f"\n  Due date: {issue['due_date']}"
                
                output.append(issue_info)
            
            output.append(f"\nFound {len(issues_data)} matching issue(s)")
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"

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
            return f"❌ {result.message}\nError: {result.error}"

    @mcp.tool()
    def get_project_details(project_id: int) -> str:
        """Get detailed information about a specific project.
        
        Args:
            project_id: The ID of the project to retrieve
        """
        result = project_service.get_by_id(project_id)
        
        if result.success:
            project = result.data
            if not project:
                return "❌ No project data returned"
                
            output = [f"Project #{project['id']}: {project['name']}"]
            output.append(f"Identifier: {project['identifier']}")
            output.append(f"Description: {project['description']}")
            output.append(f"Status: {project['status']}")
            output.append(f"Public: {'Yes' if project.get('is_public') else 'No'}")
            
            if project.get('parent') and project['parent'] != "Not assigned":
                output.append(f"Parent project: {project['parent']}")
            if project.get('homepage'):
                output.append(f"Homepage: {project['homepage']}")
                
            output.append(f"Created: {project['created_on']}")
            output.append(f"Updated: {project['updated_on']}")
            
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"

    @mcp.tool()
    def get_my_issues(assigned_to_id: int, limit: int = 25) -> str:
        """Get issues assigned to a specific user.
        
        Args:
            assigned_to_id: The ID of the user
            limit: Maximum number of issues to retrieve (default: 25)
        """
        result = issue_service.get_all(assigned_to_id=assigned_to_id, limit=limit)
        
        if result.success:
            issues_data = result.data.get("issues", []) if result.data else []
            
            if not issues_data:
                return f"No issues assigned to user #{assigned_to_id}."
            
            output = [f"Issues assigned to user #{assigned_to_id}:"]
            
            for issue in issues_data:
                issue_info = f"\n#{issue['id']}: {issue['subject']}"
                issue_info += f"\n  Project: {issue['project']}"
                issue_info += f"\n  Status: {issue['status']}"
                issue_info += f"\n  Priority: {issue['priority']}"
                issue_info += f"\n  Tracker: {issue['tracker']}"
                issue_info += f"\n  Created: {issue['created_on']}"
                issue_info += f"\n  Updated: {issue['updated_on']}"
                
                if issue.get('due_date') and issue['due_date'] != "Not set":
                    issue_info += f"\n  Due date: {issue['due_date']}"
                
                output.append(issue_info)
            
            output.append(f"\nFound {len(issues_data)} assigned issue(s)")
            return "\n".join(output)
        else:
            return f"❌ {result.message}\nError: {result.error}"
        