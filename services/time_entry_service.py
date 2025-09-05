"""
Time Entry service for Redmine Time Entries.
"""

from typing import Dict, Any
from models.models import OperationResult, safe_getattr, get_resource_name
from .base_service import RedmineService


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
