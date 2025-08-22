"""
User-related MCP tools for Redmine operations.
"""

from services import UserService
from .base_tools import format_error


def register_user_tools(mcp, user_service: UserService):
    """Register user-related MCP tools with the FastMCP server"""
    
    @mcp.tool()
    def get_users() -> str:
        """Get a list of all users."""
        result = user_service.get_all()
        
        if result.success:
            users_data = result.data.get("users", []) if result.data else []
            if not users_data:
                return "No users found."
            
            output = ["Available Users:"]
            for user in users_data:
                user_info = f"ID: {user['id']} - {user['firstname']} {user['lastname']}"
                if user.get('login'):
                    user_info += f" (Login: {user['login']})"
                if user.get('mail'):
                    user_info += f" - Email: {user['mail']}"
                output.append(user_info)
            
            return "\n".join(output)
        else:
            return format_error(result)

    @mcp.tool()
    def get_user(user_id: int) -> str:
        """Get detailed information about a specific user.
        
        Args:
            user_id: The ID of the user to retrieve
        """
        result = user_service.get_by_id(user_id)
        
        if result.success:
            user = result.data
            if not user:
                return "❌ No user data returned"
                
            output = [f"User #{user['id']}: {user['firstname']} {user['lastname']}"]
            output.append(f"Login: {user['login']}")
            output.append(f"Email: {user['mail']}")
            output.append(f"Status: {user['status']}")
            output.append(f"Created: {user['created_on']}")
            output.append(f"Last login: {user['last_login_on']}")
            
            return "\n".join(output)
        else:
            return format_error(result)
