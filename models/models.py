"""
Data models and common utilities for the Redmine MCP server.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class OperationResult:
    """Data class to standardize operation results"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def safe_getattr(obj, attr, default=""):
    """Safely get attribute from object, handling missing attributes"""
    try:
        value = getattr(obj, attr, None)
        if value is None:
            return default
        # Handle nested attributes like assigned_to.name
        if hasattr(value, 'name'):
            return value.name
        # Handle id attributes
        if hasattr(value, 'id'):
            return f"{value.name} (ID: {value.id})" if hasattr(value, 'name') else str(value.id)
        return str(value) if value else default
    except (AttributeError, TypeError):
        return default


def format_date(date_obj):
    """Format date object to string safely"""
    if date_obj is None:
        return "Not set"
    try:
        return str(date_obj)
    except Exception:
        return "Not set"


def get_resource_name(resource):
    """Get the name of a resource object safely"""
    if resource is None:
        return "Not assigned"
    try:
        if hasattr(resource, 'name'):
            return resource.name
        elif hasattr(resource, 'firstname') and hasattr(resource, 'lastname'):
            return f"{resource.firstname} {resource.lastname}"
        elif hasattr(resource, 'id'):
            return f"ID: {resource.id}"
        return str(resource)
    except Exception:
        return "Unknown"
