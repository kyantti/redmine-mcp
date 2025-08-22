"""
Tracker service implementing the Repository pattern for Redmine Trackers.
"""

from typing import Dict, Any
from models.models import OperationResult, safe_getattr, get_resource_name
from .base_service import RedmineService


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
