"""
Issue Status service implementing the Repository pattern for Redmine Issue Statuses.
"""

from typing import Dict, Any
from models.models import OperationResult, safe_getattr
from .base_service import RedmineService


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
