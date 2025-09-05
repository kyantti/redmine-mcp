"""
Project service implementing for Redmine Projects.
"""

from typing import Dict, Any
from models.models import OperationResult, safe_getattr, get_resource_name
from .base_service import RedmineService


class ProjectService(RedmineService):
    """Service class for Project operations (Read-only)"""
    
    def get_by_id(self, id: int) -> OperationResult:
        try:
            project = self.redmine.project.get(id)
            
            # Extract custom fields information, especially hours data
            custom_fields_data = {}
            allocated_hours = None
            
            cfs = getattr(project, 'custom_fields', None) or []
            for cf in cfs:
                cf_name = getattr(cf, 'name', '')
                cf_value = getattr(cf, 'value', None)
                cf_id = getattr(cf, 'id', '')
                custom_fields_data[cf_name] = {"id": cf_id, "value": cf_value}
                
                if 'horas presupuestadas' in cf_name.lower():
                    if cf_value and isinstance(cf_value, str) and cf_value.replace('.', '', 1).isdigit():
                        allocated_hours = float(cf_value)
            
            # Calculate spent hours for the project
            spent_hours = 0
            try:
                time_entries = self.redmine.time_entry.filter(project_id=id)
                spent_hours = sum(entry.hours for entry in time_entries)
            except Exception:
                # Could not retrieve time entries, but don't fail the whole operation
                pass
            
            # Calculate remaining hours
            remaining_hours = None
            if allocated_hours is not None and spent_hours is not None:
                if isinstance(allocated_hours, (int, float)):
                    remaining_hours = allocated_hours - spent_hours
            
            # Get project memberships
            members_data = []
            try:
                memberships = self.redmine.project_membership.filter(project_id=id)
                for member in memberships:
                    user = getattr(member, 'user', None)
                    roles = getattr(member, 'roles', [])
                    members_data.append({
                        "user": get_resource_name(user),
                        "roles": [get_resource_name(role) for role in roles]
                    })
            except Exception:
                # Could not retrieve memberships, but don't fail the whole operation
                pass

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
                    "custom_fields": custom_fields_data,
                    "members": members_data
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
            # only_billable = kwargs.pop('only_billable', True)

            projects = self.redmine.project.all()

            # classifier uses allocated hours from custom fields; no keyword heuristics

            # Use 'Horas Presupuestadas' custom field exclusively as the classifier.
            # Assumption: projects with numeric allocated hours > 0 are billable;
            # projects with missing, empty, zero or non-positive allocated hours are
            # considered non-billable. This is the deterministic rule requested.

            # Allow callers to override sentinel threshold for placeholder hours
            # via kwargs (useful for tests/edge cases). Default sentinel value
            # considers values larger than 1e9 as placeholders.
            # hours_sentinel_threshold = kwargs.pop('hours_sentinel_threshold', 1e9)

            # def _classify(project):
            #     """Deterministic classification using only 'Horas Presupuestadas'.

            #     Returns (is_billable: bool, score: int, reasons: list[str]).
            #     """
            #     reasons = []

            #     cfs = getattr(project, 'custom_fields', None) or []
            #     horas_val = None
            #     for cf in cfs:
            #         if isinstance(cf, dict):
            #             cf_name = cf.get('name') or cf.get('field') or ''
            #             cf_value = cf.get('value')
            #         else:
            #             cf_name = getattr(cf, 'name', None) or getattr(cf, 'field', None) or ''
            #             cf_value = getattr(cf, 'value', None)

            #         name_l = (cf_name or '').lower()
            #         if 'hora' in name_l or 'presupuest' in name_l:
            #             horas_val = str(cf_value or '').strip()
            #             break

            #     if horas_val is None:
            #         reasons.append("Horas Presupuestadas not present -> treated as non-billable")
            #         return False, 0, reasons

            #     if horas_val in ('', '-', '0'):
            #         reasons.append(f"Horas Presupuestadas='{horas_val}' -> non-billable")
            #         return False, 0, reasons

            #     # normalize decimal/comma and try parse
            #     try:
            #         num = float(horas_val.replace(',', '.'))
            #     except Exception:
            #         reasons.append(f"Horas Presupuestadas='{horas_val}' (non-numeric) -> non-billable")
            #         return False, 0, reasons

            #     # Treat extremely large numbers as placeholders -> non-billable
            #     if num > float(hours_sentinel_threshold):
            #         reasons.append(f"Horas Presupuestadas={num} (>{hours_sentinel_threshold}) -> treated as placeholder/non-billable")
            #         return False, 0, reasons

            #     if num > 0:
            #         reasons.append(f"Horas Presupuestadas={num} -> billable")
            #         return True, 0, reasons

            #     reasons.append(f"Horas Presupuestadas={num} (<=0) -> non-billable")
            #     return False, 0, reasons

            projects_data = []
            for project in projects:
                # is_billable, score, reasons = _classify(project)
                # if only_billable and not is_billable:
                #     # skip non-billable projects
                #     continue

                # Get project memberships
                members_data = []
                try:
                    memberships = self.redmine.project_membership.filter(project_id=project.id)
                    for member in memberships:
                        user = getattr(member, 'user', None)
                        roles = getattr(member, 'roles', [])
                        members_data.append({
                            "user": get_resource_name(user),
                            "roles": [get_resource_name(role) for role in roles]
                        })
                except Exception:
                    # Could not retrieve memberships, but don't fail the whole operation
                    pass

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
                    "members": members_data,
                    # Add classification metadata so callers can inspect why a project
                    # was considered billable/non-billable.
                    # "_classification": {"billable": is_billable, "score": score, "reasons": reasons}
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
