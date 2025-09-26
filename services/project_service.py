"""
Project service implementing the Repository pattern for Redmine Projects.
"""

from typing import Dict, Any
from models.models import OperationResult, safe_getattr, get_resource_name
from .base_service import RedmineService


class ProjectService(RedmineService):
    """Service class for Project operations following Repository pattern (Read-only)"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            project = self.redmine.project.get(id)
            
            # Extract custom fields information, especially hours data
            custom_fields_data = {}
            allocated_hours = None
            
            cfs = getattr(project, 'custom_fields', None) or []
            for cf in cfs:
                if isinstance(cf, dict):
                    cf_name = cf.get('name') or cf.get('field') or ''
                    cf_value = cf.get('value')
                    cf_id = cf.get('id')
                else:
                    cf_name = getattr(cf, 'name', None) or getattr(cf, 'field', None) or ''
                    cf_value = getattr(cf, 'value', None)
                    cf_id = getattr(cf, 'id', None)
                
                # Store all custom fields
                if cf_name:
                    custom_fields_data[cf_name] = {
                        'id': cf_id,
                        'value': cf_value
                    }
                
                # Special handling for hours field
                name_l = (cf_name or '').lower()
                if 'hora' in name_l or 'presupuest' in name_l:
                    horas_val = str(cf_value or '').strip()
                    if horas_val and horas_val not in ('', '-', '0'):
                        try:
                            allocated_hours = float(horas_val.replace(',', '.'))
                        except ValueError:
                            allocated_hours = horas_val  # Keep as string if not numeric
                    else:
                        allocated_hours = 0
            
            # Calculate spent hours for the project
            spent_hours = 0
            try:
                time_entries = list(self.redmine.time_entry.filter(project_id=id))
                spent_hours = sum(getattr(entry, 'hours', 0) for entry in time_entries)
            except Exception:
                spent_hours = None  # Could not retrieve time entries
            
            # Calculate remaining hours
            remaining_hours = None
            if allocated_hours is not None and spent_hours is not None:
                if isinstance(allocated_hours, (int, float)):
                    remaining_hours = allocated_hours - spent_hours

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
                    "homepage": safe_getattr(project, "homepage", ""),
                    "allocated_hours": allocated_hours,
                    "spent_hours": spent_hours,
                    "remaining_hours": remaining_hours,
                    "custom_fields": custom_fields_data
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
            projects = self.redmine.project.all()
            projects_data = []
            for project in projects:
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
                    "homepage": safe_getattr(project, "homepage", "")
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
