"""
Issue service implementing for Redmine Issues.
"""

from typing import Dict, Any, Optional
from models.models import OperationResult, safe_getattr, get_resource_name
from .base_service import RedmineService


class IssueService(RedmineService):
    """Service class for Issue operations"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            # Get issue with journals included
            issue = self.redmine.issue.get(id, include=['journals'])
            
            # Extract journals (notes and changes)
            journals_data = []
            journals = getattr(issue, 'journals', [])
            
            for journal in journals:
                journal_data = {
                    "id": journal.id,
                    "user": get_resource_name(getattr(journal, "user", None)),
                    "notes": safe_getattr(journal, "notes", ""),
                    "created_on": str(getattr(journal, "created_on", "")),
                    "details": getattr(journal, "details", [])
                }
                journals_data.append(journal_data)
            
            # Get all statuses to enrich the issue's status field
            all_statuses = self.redmine.issue_status.all()
            status_map = {status.id: status for status in all_statuses}
            
            issue_status_obj = getattr(issue, "status", None)
            status_details = None
            if issue_status_obj and issue_status_obj.id in status_map:
                status_resource = status_map[issue_status_obj.id]
                status_details = {
                    "id": status_resource.id,
                    "name": safe_getattr(status_resource, "name", "No name"),
                    "is_closed": getattr(status_resource, "is_closed", False),
                }

            return OperationResult(
                success=True,
                message=f"Issue {id} retrieved successfully",
                data={
                    "id": issue.id,
                    "subject": safe_getattr(issue, "subject", "No subject"),
                    "description": safe_getattr(issue, "description", "No description"),
                    "status": status_details,
                    "priority": get_resource_name(getattr(issue, "priority", None)),
                    "tracker": get_resource_name(getattr(issue, "tracker", None)),
                    "project": get_resource_name(getattr(issue, "project", None)),
                    "author": get_resource_name(getattr(issue, "author", None)),
                    "assigned_to": get_resource_name(getattr(issue, "assigned_to", None)),
                    "category": get_resource_name(getattr(issue, "category", None)),
                    "fixed_version": get_resource_name(getattr(issue, "fixed_version", None)),
                    "created_on": str(getattr(issue, "created_on", "")),
                    "updated_on": str(getattr(issue, "updated_on", "")),
                    "due_date": str(getattr(issue, "due_date", "")) if getattr(issue, "due_date", None) else "Not set",
                    "start_date": str(getattr(issue, "start_date", "")) if getattr(issue, "start_date", None) else "Not set",
                    "done_ratio": getattr(issue, "done_ratio", 0),
                    "estimated_hours": getattr(issue, "estimated_hours", None) or "Not set",
                    "spent_hours": getattr(issue, "spent_hours", 0),
                    "journals": journals_data
                }
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve issue {id}",
                error=str(e)
            )
    
    def get_all(self, **kwargs) -> OperationResult:
        try:
            # Handle subject search separately since Redmine API doesn't directly support it
            subject_filter = kwargs.pop('subject', None)
            # Handle include_journals option for getting activity history
            include_journals = kwargs.pop('include_journals', False)
            
            issues = self.redmine.issue.filter(**kwargs)
            issue_list = list(issues)
            
            # Apply subject filtering if specified
            if subject_filter:
                issue_list = [issue for issue in issue_list 
                            if subject_filter.lower() in safe_getattr(issue, 'subject', '').lower()]
            
            # Get all statuses to enrich the issue's status field
            all_statuses = self.redmine.issue_status.all()
            status_map = {status.id: status for status in all_statuses}
            
            issues_data = []
            for issue in issue_list:
                issue_status_obj = getattr(issue, "status", None)
                status_details = None
                if issue_status_obj and issue_status_obj.id in status_map:
                    status_resource = status_map[issue_status_obj.id]
                    status_details = {
                        "id": status_resource.id,
                        "name": safe_getattr(status_resource, "name", "No name"),
                        "is_closed": getattr(status_resource, "is_closed", False),
                    }
                
                issue_data = {
                    "id": issue.id,
                    "subject": safe_getattr(issue, "subject", "No subject"),
                    "description": safe_getattr(issue, "description", "No description"),
                    "status": status_details,
                    "priority": get_resource_name(getattr(issue, "priority", None)),
                    "tracker": get_resource_name(getattr(issue, "tracker", None)),
                    "project": get_resource_name(getattr(issue, "project", None)),
                    "author": get_resource_name(getattr(issue, "author", None)),
                    "assigned_to": get_resource_name(getattr(issue, "assigned_to", None)),
                    "category": get_resource_name(getattr(issue, "category", None)),
                    "fixed_version": get_resource_name(getattr(issue, "fixed_version", None)),
                    "created_on": str(getattr(issue, "created_on", "")),
                    "updated_on": str(getattr(issue, "updated_on", "")),
                    "due_date": str(getattr(issue, "due_date", "")) if getattr(issue, "due_date", None) else "Not set",
                    "start_date": str(getattr(issue, "start_date", "")) if getattr(issue, "start_date", None) else "Not set",
                    "done_ratio": getattr(issue, "done_ratio", 0),
                    "estimated_hours": getattr(issue, "estimated_hours", None) or "Not set",
                    "spent_hours": getattr(issue, "spent_hours", 0)
                }
                
                # Include journals if requested
                if include_journals:
                    journals_data = []
                    journals = getattr(self.redmine.issue.get(issue.id, include=['journals']), 'journals', [])
                    for journal in journals:
                        journals_data.append({
                            "id": journal.id,
                            "user": get_resource_name(getattr(journal, "user", None)),
                            "notes": safe_getattr(journal, "notes", ""),
                            "created_on": str(getattr(journal, "created_on", "")),
                            "details": getattr(journal, "details", [])
                        })
                    issue_data["journals"] = journals_data
                    
                issues_data.append(issue_data)
            
            return OperationResult(
                success=True,
                message=f"Retrieved {len(issues_data)} issue(s) successfully",
                data={"issues": issues_data, "count": len(issues_data)}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message="Failed to retrieve issues",
                error=str(e)
            )
    
    def get_by_subject(self, subject: str, project_id: Optional[int] = None, limit: int = 25) -> OperationResult:
        """Get issues by subject (name) with optional project filtering"""
        try:
            filter_params = {"limit": limit}
            if project_id:
                filter_params["project_id"] = project_id
            
            try:
                issues = self.redmine.issue.filter(**filter_params)
            except Exception:
                # Fallback to all issues if filter fails
                issues = self.redmine.issue.all()
            
            # Convert to list and filter by subject
            matching_issues = []
            for issue in issues:
                if subject.lower() in safe_getattr(issue, 'subject', '').lower():
                    matching_issues.append(issue)
                if len(matching_issues) >= limit:
                    break

            # Get all statuses to enrich the issue's status field
            all_statuses = self.redmine.issue_status.all()
            status_map = {status.id: status for status in all_statuses}

            issues_data = []
            for issue in matching_issues:
                issue_status_obj = getattr(issue, "status", None)
                status_details = None
                if issue_status_obj and issue_status_obj.id in status_map:
                    status_resource = status_map[issue_status_obj.id]
                    status_details = {
                        "id": status_resource.id,
                        "name": safe_getattr(status_resource, "name", "No name"),
                        "is_closed": getattr(status_resource, "is_closed", False),
                    }

                issue_data = {
                    "id": issue.id,
                    "subject": safe_getattr(issue, "subject", "No subject"),
                    "description": safe_getattr(issue, "description", "No description"),
                    "status": status_details,
                    "priority": get_resource_name(getattr(issue, "priority", None)),
                    "tracker": get_resource_name(getattr(issue, "tracker", None)),
                    "project": get_resource_name(getattr(issue, "project", None)),
                    "author": get_resource_name(getattr(issue, "author", None)),
                    "assigned_to": get_resource_name(getattr(issue, "assigned_to", None)),
                    "category": get_resource_name(getattr(issue, "category", None)),
                    "fixed_version": get_resource_name(getattr(issue, "fixed_version", None)),
                    "created_on": str(getattr(issue, "created_on", "")),
                    "updated_on": str(getattr(issue, "updated_on", "")),
                    "due_date": str(getattr(issue, "due_date", "")) if getattr(issue, "due_date", None) else "Not set",
                    "start_date": str(getattr(issue, "start_date", "")) if getattr(issue, "start_date", None) else "Not set",
                    "done_ratio": getattr(issue, "done_ratio", 0),
                    "estimated_hours": getattr(issue, "estimated_hours", None) or "Not set",
                    "spent_hours": getattr(issue, "spent_hours", 0)
                }
                issues_data.append(issue_data)
            
            return OperationResult(
                success=True,
                message=f"Found {len(issues_data)} issue(s) matching '{subject}'",
                data={"issues": issues_data, "count": len(issues_data)}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to search issues by subject '{subject}'",
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

