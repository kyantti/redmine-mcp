"""
Service layer implementing the Repository pattern for Redmine entities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.models import OperationResult, safe_getattr, get_resource_name


class RedmineService(ABC):
    """Abstract base class for Redmine services"""
    
    def __init__(self, redmine_client):
        self.redmine = redmine_client
    
    @abstractmethod
    def get_by_id(self, id: int) -> OperationResult:
        pass
    
    @abstractmethod
    def get_all(self, **kwargs) -> OperationResult:
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
    """Service class for Issue operations"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            issue = self.redmine.issue.get(id)
            return OperationResult(
                success=True,
                message=f"Issue {id} retrieved successfully",
                data={
                    "id": issue.id,
                    "subject": safe_getattr(issue, "subject", "No subject"),
                    "description": safe_getattr(issue, "description", "No description"),
                    "status": get_resource_name(getattr(issue, "status", None)),
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
            
            issues = self.redmine.issue.filter(**kwargs)
            issue_list = list(issues)
            
            # Apply subject filtering if specified
            if subject_filter:
                issue_list = [issue for issue in issue_list 
                            if subject_filter.lower() in safe_getattr(issue, 'subject', '').lower()]
            
            issues_data = []
            for issue in issue_list:
                issue_data = {
                    "id": issue.id,
                    "subject": safe_getattr(issue, "subject", "No subject"),
                    "description": safe_getattr(issue, "description", "No description"),
                    "status": get_resource_name(getattr(issue, "status", None)),
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
            
            issues_data = []
            for issue in matching_issues:
                issue_data = {
                    "id": issue.id,
                    "subject": safe_getattr(issue, "subject", "No subject"),
                    "description": safe_getattr(issue, "description", "No description"),
                    "status": get_resource_name(getattr(issue, "status", None)),
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


class TimeEntryService(RedmineService):
    """Service class for Time Entry operations"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            entry = self.redmine.time_entry.get(id)
            return OperationResult(
                success=True,
                message=f"Time entry {id} retrieved successfully",
                data={
                    "id": entry.id,
                    "hours": getattr(entry, "hours", 0),
                    "comments": safe_getattr(entry, "comments", ""),
                    "spent_on": str(getattr(entry, "spent_on", "")),
                    "user": get_resource_name(getattr(entry, "user", None)),
                    "activity": get_resource_name(getattr(entry, "activity", None)),
                    "project": get_resource_name(getattr(entry, "project", None)),
                    "issue": get_resource_name(getattr(entry, "issue", None)),
                    "created_on": str(getattr(entry, "created_on", "")),
                    "updated_on": str(getattr(entry, "updated_on", ""))
                }
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve time entry {id}",
                error=str(e)
            )
    
    def get_all(self, **kwargs) -> OperationResult:
        try:
            entries = self.redmine.time_entry.filter(**kwargs)
            entry_list = list(entries)
            
            entries_data = []
            for entry in entry_list:
                entry_data = {
                    "id": entry.id,
                    "hours": getattr(entry, "hours", 0),
                    "comments": safe_getattr(entry, "comments", ""),
                    "spent_on": str(getattr(entry, "spent_on", "")),
                    "user": get_resource_name(getattr(entry, "user", None)),
                    "activity": get_resource_name(getattr(entry, "activity", None)),
                    "project": get_resource_name(getattr(entry, "project", None)),
                    "issue": get_resource_name(getattr(entry, "issue", None)),
                    "created_on": str(getattr(entry, "created_on", "")),
                    "updated_on": str(getattr(entry, "updated_on", ""))
                }
                entries_data.append(entry_data)
            
            return OperationResult(
                success=True,
                message=f"Retrieved {len(entries_data)} time entry(ies) successfully",
                data={"time_entries": entries_data, "count": len(entries_data)}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message="Failed to retrieve time entries",
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


class ProjectService(RedmineService):
    """Service class for Project operations following Repository pattern (Read-only)"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            project = self.redmine.project.get(id)
            return OperationResult(
                success=True,
                message=f"Project {id} retrieved successfully",
                data={
                    "id": project.id,
                    "name": safe_getattr(project, "name", "No name"),
                    "identifier": safe_getattr(project, "identifier", ""),
                    "description": safe_getattr(project, "description", "No description"),
                    "status": getattr(project, "status", "Unknown"),
                    "is_public": getattr(project, "is_public", False),
                    "parent": get_resource_name(getattr(project, "parent", None)),
                    "created_on": str(getattr(project, "created_on", "")),
                    "updated_on": str(getattr(project, "updated_on", "")),
                    "homepage": safe_getattr(project, "homepage", "")
                }
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve project {id}",
                error=str(e)
            )
    
    def get_all(self, **kwargs) -> OperationResult:
        try:
            # By default return only billable projects. Callers can override
            # by passing only_billable=False in kwargs.
            only_billable = kwargs.pop('only_billable', True)

            projects = self.redmine.project.all()

            # classifier uses allocated hours from custom fields; no keyword heuristics

            # Use 'Horas Presupuestadas' custom field exclusively as the classifier.
            # Assumption: projects with numeric allocated hours > 0 are billable;
            # projects with missing, empty, zero or non-positive allocated hours are
            # considered non-billable. This is the deterministic rule requested.

            # Allow callers to override sentinel threshold for placeholder hours
            # via kwargs (useful for tests/edge cases). Default sentinel value
            # considers values larger than 1e9 as placeholders.
            hours_sentinel_threshold = kwargs.pop('hours_sentinel_threshold', 1e9)

            def _classify(project):
                """Deterministic classification using only 'Horas Presupuestadas'.

                Returns (is_billable: bool, score: int, reasons: list[str]).
                """
                reasons = []

                cfs = getattr(project, 'custom_fields', None) or []
                horas_val = None
                for cf in cfs:
                    if isinstance(cf, dict):
                        cf_name = cf.get('name') or cf.get('field') or ''
                        cf_value = cf.get('value')
                    else:
                        cf_name = getattr(cf, 'name', None) or getattr(cf, 'field', None) or ''
                        cf_value = getattr(cf, 'value', None)

                    name_l = (cf_name or '').lower()
                    if 'hora' in name_l or 'presupuest' in name_l:
                        horas_val = str(cf_value or '').strip()
                        break

                if horas_val is None:
                    reasons.append("Horas Presupuestadas not present -> treated as non-billable")
                    return False, 0, reasons

                if horas_val in ('', '-', '0'):
                    reasons.append(f"Horas Presupuestadas='{horas_val}' -> non-billable")
                    return False, 0, reasons

                # normalize decimal/comma and try parse
                try:
                    num = float(horas_val.replace(',', '.'))
                except Exception:
                    reasons.append(f"Horas Presupuestadas='{horas_val}' (non-numeric) -> non-billable")
                    return False, 0, reasons

                # Treat extremely large numbers as placeholders -> non-billable
                if num > float(hours_sentinel_threshold):
                    reasons.append(f"Horas Presupuestadas={num} (>{hours_sentinel_threshold}) -> treated as placeholder/non-billable")
                    return False, 0, reasons

                if num > 0:
                    reasons.append(f"Horas Presupuestadas={num} -> billable")
                    return True, 0, reasons

                reasons.append(f"Horas Presupuestadas={num} (<=0) -> non-billable")
                return False, 0, reasons

            projects_data = []
            for project in projects:
                is_billable, score, reasons = _classify(project)
                if only_billable and not is_billable:
                    # skip non-billable projects
                    continue

                project_data = {
                    "id": project.id,
                    "name": safe_getattr(project, "name", "No name"),
                    "identifier": safe_getattr(project, "identifier", ""),
                    "description": safe_getattr(project, "description", "No description"),
                    "status": getattr(project, "status", "Unknown"),
                    "is_public": getattr(project, "is_public", False),
                    "parent": get_resource_name(getattr(project, "parent", None)),
                    "created_on": str(getattr(project, "created_on", "")),
                    "updated_on": str(getattr(project, "updated_on", "")),
                    "homepage": safe_getattr(project, "homepage", ""),
                    # Add classification metadata so callers can inspect why a project
                    # was considered billable/non-billable.
                    "_classification": {"billable": is_billable, "score": score, "reasons": reasons}
                }
                projects_data.append(project_data)

            return OperationResult(
                success=True,
                message=f"Retrieved {len(projects_data)} project(s) successfully",
                data={"projects": projects_data, "count": len(projects_data)}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message="Failed to retrieve projects",
                error=str(e)
            )
    
    def create(self, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="Project creation is not supported through this service",
            error="Operation not permitted"
        )
    
    def update(self, id: int, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="Project updates are not supported through this service",
            error="Operation not permitted"
        )
    
    def delete(self, id: int) -> OperationResult:
        return OperationResult(
            success=False,
            message="Project deletion is not supported through this service",
            error="Operation not permitted"
        )


class UserService(RedmineService):
    """Service class for User operations (Read-only)"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            user = self.redmine.user.get(id)
            return OperationResult(
                success=True,
                message=f"User {id} retrieved successfully",
                data={
                    "id": user.id,
                    "login": safe_getattr(user, "login", ""),
                    "firstname": safe_getattr(user, "firstname", ""),
                    "lastname": safe_getattr(user, "lastname", ""),
                    "mail": safe_getattr(user, "mail", ""),
                    "status": getattr(user, "status", "Unknown"),
                    "created_on": str(getattr(user, "created_on", "")),
                    "last_login_on": str(getattr(user, "last_login_on", "")) if getattr(user, "last_login_on", None) else "Never",
                    "api_key": safe_getattr(user, "api_key", "Not available")
                }
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve user {id}",
                error=str(e)
            )
    
    def get_all(self, **kwargs) -> OperationResult:
        try:
            users = self.redmine.user.all()
            
            users_data = []
            for user in users:
                user_data = {
                    "id": user.id,
                    "login": safe_getattr(user, "login", ""),
                    "firstname": safe_getattr(user, "firstname", ""),
                    "lastname": safe_getattr(user, "lastname", ""),
                    "mail": safe_getattr(user, "mail", ""),
                    "status": getattr(user, "status", "Unknown"),
                    "created_on": str(getattr(user, "created_on", "")),
                    "last_login_on": str(getattr(user, "last_login_on", "")) if getattr(user, "last_login_on", None) else "Never"
                }
                users_data.append(user_data)
            
            return OperationResult(
                success=True,
                message=f"Retrieved {len(users_data)} user(s) successfully",
                data={"users": users_data, "count": len(users_data)}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message="Failed to retrieve users",
                error=str(e)
            )
    
    def create(self, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="User creation is not supported through this service",
            error="Operation not permitted"
        )
    
    def update(self, id: int, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="User updates are not supported through this service",
            error="Operation not permitted"
        )
    
    def delete(self, id: int) -> OperationResult:
        return OperationResult(
            success=False,
            message="User deletion is not supported through this service",
            error="Operation not permitted"
        )


class TrackerService(RedmineService):
    """Service class for Tracker operations (Read-only)"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            trackers = self.redmine.tracker.all()
            tracker = next((t for t in trackers if t.id == id), None)
            if not tracker:
                return OperationResult(
                    success=False,
                    message=f"Tracker {id} not found",
                    error="Tracker not found"
                )
            
            return OperationResult(
                success=True,
                message=f"Tracker {id} retrieved successfully",
                data={
                    "id": tracker.id,
                    "name": safe_getattr(tracker, "name", "No name"),
                    "default_status": get_resource_name(getattr(tracker, "default_status", None)),
                    "description": safe_getattr(tracker, "description", "No description")
                }
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve tracker {id}",
                error=str(e)
            )
    
    def get_all(self, **kwargs) -> OperationResult:
        try:
            trackers = self.redmine.tracker.all()
            
            trackers_data = []
            for tracker in trackers:
                tracker_data = {
                    "id": tracker.id,
                    "name": safe_getattr(tracker, "name", "No name"),
                    "default_status": get_resource_name(getattr(tracker, "default_status", None)),
                    "description": safe_getattr(tracker, "description", "No description")
                }
                trackers_data.append(tracker_data)
            
            return OperationResult(
                success=True,
                message=f"Retrieved {len(trackers_data)} tracker(s) successfully",
                data={"trackers": trackers_data, "count": len(trackers_data)}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message="Failed to retrieve trackers",
                error=str(e)
            )
    
    def create(self, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="Tracker creation is not supported through this service",
            error="Operation not permitted"
        )
    
    def update(self, id: int, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="Tracker updates are not supported through this service",
            error="Operation not permitted"
        )
    
    def delete(self, id: int) -> OperationResult:
        return OperationResult(
            success=False,
            message="Tracker deletion is not supported through this service",
            error="Operation not permitted"
        )


class IssueStatusService(RedmineService):
    """Service class for Issue Status operations (Read-only)"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            statuses = self.redmine.issue_status.all()
            status = next((s for s in statuses if s.id == id), None)
            if not status:
                return OperationResult(
                    success=False,
                    message=f"Issue status {id} not found",
                    error="Issue status not found"
                )
            
            return OperationResult(
                success=True,
                message=f"Issue status {id} retrieved successfully",
                data={
                    "id": status.id,
                    "name": safe_getattr(status, "name", "No name"),
                    "is_closed": getattr(status, "is_closed", False),
                    "is_default": getattr(status, "is_default", False)
                }
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve issue status {id}",
                error=str(e)
            )
    
    def get_all(self, **kwargs) -> OperationResult:
        try:
            statuses = self.redmine.issue_status.all()
            
            statuses_data = []
            for status in statuses:
                status_data = {
                    "id": status.id,
                    "name": safe_getattr(status, "name", "No name"),
                    "is_closed": getattr(status, "is_closed", False),
                    "is_default": getattr(status, "is_default", False)
                }
                statuses_data.append(status_data)
            
            return OperationResult(
                success=True,
                message=f"Retrieved {len(statuses_data)} issue status(es) successfully",
                data={"issue_statuses": statuses_data, "count": len(statuses_data)}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message="Failed to retrieve issue statuses",
                error=str(e)
            )
    
    def create(self, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="Issue status creation is not supported through this service",
            error="Operation not permitted"
        )
    
    def update(self, id: int, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="Issue status updates are not supported through this service",
            error="Operation not permitted"
        )
    
    def delete(self, id: int) -> OperationResult:
            return OperationResult(
                success=False,
                message="Issue status deletion is not supported through this service",
                error="Operation not permitted"
            )


class ProjectMembershipService(RedmineService):
    """Service class for Project Membership operations (Read-only)"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            membership = self.redmine.project_membership.get(id)
            return OperationResult(
                success=True,
                message=f"Project membership {id} retrieved successfully",
                data={
                    "id": membership.id,
                    "user": get_resource_name(getattr(membership, "user", None)),
                    "user_id": getattr(membership.user, "id", None) if hasattr(membership, "user") else None,
                    "project": get_resource_name(getattr(membership, "project", None)),
                    "project_id": getattr(membership.project, "id", None) if hasattr(membership, "project") else None,
                    "roles": [role.name for role in membership.roles] if hasattr(membership, "roles") and membership.roles else []
                }
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve project membership {id}",
                error=str(e)
            )
    
    def get_all(self, **kwargs) -> OperationResult:
        try:
            # Filter by project_id if provided
            if 'project_id' in kwargs:
                memberships = self.redmine.project_membership.filter(project_id=kwargs['project_id'])
            else:
                # This might not be supported by all Redmine instances
                memberships = self.redmine.project_membership.all()
            
            membership_list = list(memberships)
            
            memberships_data = []
            for membership in membership_list:
                membership_data = {
                    "id": membership.id,
                    "user": get_resource_name(getattr(membership, "user", None)),
                    "user_id": getattr(membership.user, "id", None) if hasattr(membership, "user") else None,
                    "project": get_resource_name(getattr(membership, "project", None)),
                    "project_id": getattr(membership.project, "id", None) if hasattr(membership, "project") else None,
                    "roles": [role.name for role in membership.roles] if hasattr(membership, "roles") and membership.roles else []
                }
                memberships_data.append(membership_data)
            
            return OperationResult(
                success=True,
                message=f"Retrieved {len(memberships_data)} project membership(s) successfully",
                data={"memberships": memberships_data, "count": len(memberships_data)}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message="Failed to retrieve project memberships",
                error=str(e)
            )
    
    def get_by_project(self, project_id: int) -> OperationResult:
        """Get all memberships for a specific project"""
        try:
            memberships = self.redmine.project_membership.filter(project_id=project_id)
            membership_list = list(memberships)
            
            memberships_data = []
            for membership in membership_list:
                membership_data = {
                    "id": membership.id,
                    "user": get_resource_name(getattr(membership, "user", None)),
                    "user_id": getattr(membership.user, "id", None) if hasattr(membership, "user") else None,
                    "project": get_resource_name(getattr(membership, "project", None)),
                    "project_id": getattr(membership.project, "id", None) if hasattr(membership, "project") else None,
                    "roles": [role.name for role in membership.roles] if hasattr(membership, "roles") and membership.roles else []
                }
                memberships_data.append(membership_data)
            
            return OperationResult(
                success=True,
                message=f"Retrieved {len(memberships_data)} project membership(s) for project {project_id}",
                data={"memberships": memberships_data, "count": len(memberships_data)}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to retrieve project memberships for project {project_id}",
                error=str(e)
            )
    
    def create(self, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="Project membership creation is not supported through this service",
            error="Operation not permitted"
        )
    
    def update(self, id: int, data: Dict[str, Any]) -> OperationResult:
        return OperationResult(
            success=False,
            message="Project membership updates are not supported through this service",
            error="Operation not permitted"
        )
    
    def delete(self, id: int) -> OperationResult:
        return OperationResult(
            success=False,
            message="Project membership deletion is not supported through this service",
            error="Operation not permitted"
        )