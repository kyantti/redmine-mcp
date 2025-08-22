"""
Issue-related MCP tools for Redmine operations.
"""

from typing import Optional, Dict, Any
from services import IssueService
from .base_tools import format_error


def register_issue_tools(mcp, issue_service: IssueService):
    """Register issue-related MCP tools with the FastMCP server"""
    
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
            
            # Add notes and changes section
            journals = issue.get('journals', [])
            if journals:
                output.append("\n📝 Notes and Changes:")
                
                for i, journal in enumerate(journals, 1):
                    journal_output = f"\n  #{i} - {journal['user']} on {journal['created_on']}"
                    
                    # Add notes if present
                    if journal['notes'] and journal['notes'].strip():
                        journal_output += f"\n    📝 Note: {journal['notes']}"
                    
                    # Add field changes if present
                    if journal['details']:
                        journal_output += "\n    🔄 Changes:"
                        for detail in journal['details']:
                            property_name = detail['property']
                            field_name = detail['name']
                            old_value = detail['old_value'] or "(empty)"
                            new_value = detail['new_value'] or "(empty)"
                            
                            if property_name == 'attr':
                                # Standard field change
                                journal_output += f"\n      • {field_name}: {old_value} → {new_value}"
                            elif property_name == 'cf':
                                # Custom field change
                                journal_output += f"\n      • Custom field {field_name}: {old_value} → {new_value}"
                            elif property_name == 'attachment':
                                # Attachment changes
                                if old_value == "" and new_value != "":
                                    journal_output += f"\n      • Added attachment: {new_value}"
                                elif old_value != "" and new_value == "":
                                    journal_output += f"\n      • Removed attachment: {old_value}"
                            else:
                                # Other property changes
                                journal_output += f"\n      • {property_name} {field_name}: {old_value} → {new_value}"
                    
                    output.append(journal_output)
                
                output.append(f"\nTotal activity entries: {len(journals)}")
            else:
                output.append("\n📝 Notes and Changes: No activity history found")
            
            return "\n".join(output)
        else:
            return format_error(result)

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
            return format_error(result)

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
            return format_error(result)

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
            return format_error(result)

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
            return format_error(result)

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
            return format_error(result)

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
            return format_error(result)

    @mcp.tool()
    def get_issue_activity(issue_id: int) -> str:
        """Get the activity history (notes and changes) for a specific issue.
        
        Args:
            issue_id: The ID of the issue to retrieve activity for
        """
        result = issue_service.get_by_id(issue_id)
        
        if result.success:
            issue = result.data
            if not issue:
                return "❌ No issue data returned"
            
            # Extract journals for activity
            journals = issue.get('journals', [])
            
            if not journals:
                return f"📝 Issue #{issue_id}: No activity history found"
            
            output = [f"📝 Activity History for Issue #{issue_id}: {issue['subject']}"]
            output.append(f"Total activity entries: {len(journals)}\n")
            
            for i, journal in enumerate(journals, 1):
                journal_output = f"#{i} - {journal['user']} on {journal['created_on']}"
                
                # Add notes if present
                if journal['notes'] and journal['notes'].strip():
                    journal_output += f"\n  📝 Note: {journal['notes']}"
                
                # Add field changes if present
                if journal['details']:
                    journal_output += "\n  🔄 Changes:"
                    for detail in journal['details']:
                        property_name = detail['property']
                        field_name = detail['name']
                        old_value = detail['old_value'] or "(empty)"
                        new_value = detail['new_value'] or "(empty)"
                        
                        if property_name == 'attr':
                            # Standard field change
                            journal_output += f"\n    • {field_name}: {old_value} → {new_value}"
                        elif property_name == 'cf':
                            # Custom field change
                            journal_output += f"\n    • Custom field {field_name}: {old_value} → {new_value}"
                        elif property_name == 'attachment':
                            # Attachment changes
                            if old_value == "" and new_value != "":
                                journal_output += f"\n    • Added attachment: {new_value}"
                            elif old_value != "" and new_value == "":
                                journal_output += f"\n    • Removed attachment: {old_value}"
                        else:
                            # Other property changes
                            journal_output += f"\n    • {property_name} {field_name}: {old_value} → {new_value}"
                
                # If neither notes nor changes, indicate it's an empty entry
                if not journal['notes'].strip() and not journal['details']:
                    journal_output += "\n  (No notes or changes)"
                
                output.append(journal_output)
                
                # Add separator between entries except for the last one
                if i < len(journals):
                    output.append("")
            
            return "\n".join(output)
        else:
            return format_error(result)

    @mcp.tool()
    def get_issues_with_activity(
        project_id: int,
        limit: int = 10,
        status_id: Optional[int] = None
    ) -> str:
        """Get issues for a project with their activity history (notes and changes).
        
        Args:
            project_id: The ID of the project
            limit: Maximum number of issues to retrieve (default: 10)
            status_id: Filter by status ID (optional)
        """
        # Build filter parameters
        filter_params = {"project_id": project_id, "limit": limit, "include_journals": True}
        if status_id is not None:
            filter_params["status_id"] = status_id
        
        # Get issues with journals using the service
        result = issue_service.get_all(**filter_params)
        
        if result.success:
            issues_data = result.data.get("issues", []) if result.data else []
            
            if not issues_data:
                return f"No issues found for project {project_id}."
            
            output = [f"Issues with Activity History for Project {project_id}:"]
            if status_id:
                output[0] += f" (Status ID: {status_id})"
            
            for issue in issues_data:
                issue_info = f"\n🎫 Issue #{issue['id']}: {issue['subject']}"
                issue_info += f"\n   Status: {issue['status']} | Priority: {issue['priority']}"
                issue_info += f"\n   Assigned to: {issue['assigned_to']}"
                issue_info += f"\n   Updated: {issue['updated_on']}"
                
                # Add activity summary
                journals = issue.get('journals', [])
                if journals:
                    notes_count = sum(1 for j in journals if j.get('notes', '').strip())
                    changes_count = sum(1 for j in journals if j.get('details'))
                    issue_info += f"\n   📝 Activity: {len(journals)} total entries ({notes_count} notes, {changes_count} with changes)"
                    
                    # Show latest activity
                    if journals:
                        latest = journals[-1]
                        issue_info += f"\n   🕒 Latest: {latest['user']} on {latest['created_on']}"
                        if latest.get('notes', '').strip():
                            note_preview = latest['notes'][:100] + "..." if len(latest['notes']) > 100 else latest['notes']
                            issue_info += f"\n       Note: {note_preview}"
                else:
                    issue_info += "\n   📝 Activity: No history"
                
                output.append(issue_info)
            
            output.append(f"\nShowing {len(issues_data)} issue(s) with activity")
            return "\n".join(output)
        else:
            return format_error(result)
