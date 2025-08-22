"""
Project Membership service implementing the Repository pattern for Redmine Project Memberships.
"""

from typing import Dict, Any
from models.models import OperationResult, get_resource_name
from .base_service import RedmineService


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
