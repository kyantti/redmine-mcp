"""
Configuration and environment setup for the Redmine MCP server.
"""

import os
from redminelib import Redmine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RedmineConfig:
    """Configuration class for Redmine connection"""
    
    def __init__(self):
        self.url = os.getenv("REDMINE_URL")
        self.api_key = os.getenv("REDMINE_API_KEY")
        self.username = os.getenv("REDMINE_USERNAME")
        self.password = os.getenv("REDMINE_PASSWORD")
        
        # Validate required environment variables
        if not all([self.url, self.username, self.password]):
            raise ValueError("Missing required environment variables. Please check your .env file.")
    
    def create_client(self) -> Redmine:
        """Create and return a Redmine client instance"""
        return Redmine(url=self.url, username=self.username, password=self.password)


# Global configuration instance
config = RedmineConfig()
