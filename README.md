# Redmine MCP Server

A Model Context Protocol (MCP) server for interacting with Redmine project management system.

## Features

This MCP server provides the following tools:

- **get_all_projects**: Get information about all Redmine projects
- **get_project_details**: Get detailed information about a specific project
- **get_project_issues**: Get issues for a specific project
- **get_issue_details**: Get detailed information about a specific issue
- **create_issue**: Create a new issue in a project
- **search_issues**: Search for issues across all projects
- **get_my_issues**: Get issues assigned to the current user

## Installation

1. Install dependencies:
   ```bash
   uv install
   ```

2. Configure your Redmine credentials:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your actual Redmine credentials:
     ```
     REDMINE_URL=https://your-redmine-instance.com
     REDMINE_API_KEY=your_api_key_here
     REDMINE_USERNAME=your_username_here
     REDMINE_PASSWORD=your_password_here
     ```

**Important**: Never commit your `.env` file to version control. It contains sensitive credentials.

## Usage

### Running the MCP Server

```bash
uv run main.py
```

### Available Tools

#### get_all_projects()
Returns a formatted list of all projects with their details.

#### get_project_details(project_id: int)
Get detailed information about a specific project.
- `project_id`: The ID of the project to retrieve

#### get_project_issues(project_id: int, limit: int = 10)
Get issues for a specific project.
- `project_id`: The ID of the project
- `limit`: Maximum number of issues to retrieve (default: 10)

#### get_issue_details(issue_id: int)
Get detailed information about a specific issue.
- `issue_id`: The ID of the issue to retrieve

#### create_issue(project_id: int, subject: str, description: str = "", priority_id: int = 2)
Create a new issue in a project.
- `project_id`: The ID of the project to create the issue in
- `subject`: The subject/title of the issue
- `description`: The description of the issue (optional)
- `priority_id`: The priority ID (default: 2 for Normal)

#### search_issues(query: str, limit: int = 10)
Search for issues across all projects.
- `query`: Search query string
- `limit`: Maximum number of results to return (default: 10)

#### get_my_issues(limit: int = 10)
Get issues assigned to the current user.
- `limit`: Maximum number of issues to retrieve (default: 10)

## Configuration

Make sure to update the configuration section in `main.py` with your Redmine server details:

```python
REDMINE_URL = 'https://your-redmine-server.com'
USERNAME = 'your-username'
PASSWORD = 'your-password'
# OR use API key instead:
# API_KEY = 'your-api-key'
```

## Security Note

⚠️ **Important**: The current configuration includes hardcoded credentials. For production use, consider:
- Using environment variables for sensitive data
- Using API keys instead of passwords
- Implementing proper authentication mechanisms

## Example Usage with MCP Client

Once the server is running, you can use any MCP client to interact with it. The server provides tools for managing Redmine projects and issues programmatically.
