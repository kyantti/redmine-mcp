"""
Base service implementing the Repository pattern for Redmine entities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from models.models import OperationResult


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
