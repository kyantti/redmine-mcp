"""
Project-related MCP tools for Redmine operations.
"""

from typing import Optional
from services import ProjectService, ProjectMembershipService, IssueService
from .base_tools import format_error


def register_project_tools(mcp, project_service: ProjectService, membership_service: ProjectMembershipService, issue_service: IssueService):
    """Register project-related MCP tools with the FastMCP server"""
    
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
            return format_error(result)

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
            
            # Add time tracking information
            output.append("\n📊 Time Tracking:")
            
            # Allocated hours information
            allocated_hours = project.get('allocated_hours')
            if allocated_hours is not None:
                if isinstance(allocated_hours, (int, float)) and allocated_hours > 0:
                    output.append(f"  Allocated Hours: {allocated_hours}")
                elif allocated_hours == 0:
                    output.append("  Allocated Hours: 0 (not set or non-billable)")
                else:
                    output.append(f"  Allocated Hours: {allocated_hours} (non-numeric)")
            else:
                output.append("  Allocated Hours: Not configured")
            
            # Spent hours information
            spent_hours = project.get('spent_hours')
            if spent_hours is not None:
                output.append(f"  Spent Hours: {spent_hours}")
            else:
                output.append("  Spent Hours: Could not retrieve")
            
            # Remaining hours information
            remaining_hours = project.get('remaining_hours')
            if remaining_hours is not None:
                if remaining_hours >= 0:
                    output.append(f"  Remaining Hours: {remaining_hours}")
                else:
                    output.append(f"  Remaining Hours: {remaining_hours} (over budget by {abs(remaining_hours)} hours)")
            else:
                output.append("  Remaining Hours: Cannot calculate")
            
            # Add progress information if possible
            if (allocated_hours is not None and spent_hours is not None and 
                isinstance(allocated_hours, (int, float)) and allocated_hours > 0):
                progress_percent = (spent_hours / allocated_hours) * 100
                output.append(f"  Progress: {progress_percent:.1f}% complete")
            
            # Add custom fields information
            custom_fields = project.get('custom_fields', {})
            if custom_fields:
                output.append("\n🔧 Custom Fields:")
                for field_name, field_data in custom_fields.items():
                    value = field_data.get('value', 'Not set')
                    field_id = field_data.get('id', '')
                    if value and value != 'Not set':
                        output.append(f"  {field_name}: {value}" + (f" (ID: {field_id})" if field_id else ""))
                    else:
                        output.append(f"  {field_name}: Not set" + (f" (ID: {field_id})" if field_id else ""))
            
            return "\n".join(output)
        else:
            return format_error(result)

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
            return format_error(result)

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
            return format_error(result)
