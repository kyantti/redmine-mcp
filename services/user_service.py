"""
User service for Redmine Users.
"""

from typing import Dict, Any, Union
from models.models import OperationResult, safe_getattr
from .base_service import RedmineService


class UserService(RedmineService):
    """Service class for User operations (Read-only)"""
    
    def get_by_id(self, id: Union[int, str]) -> OperationResult:
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
