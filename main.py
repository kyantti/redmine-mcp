import os
from redminelib import Redmine
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("redmine")

# Redmine configuration from environment variables
REDMINE_URL = os.getenv("REDMINE_URL")
API_KEY = os.getenv("REDMINE_API_KEY")
USERNAME = os.getenv("REDMINE_USERNAME")
PASSWORD = os.getenv("REDMINE_PASSWORD")

# Validate required environment variables
if not all([REDMINE_URL, USERNAME, PASSWORD]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Initialize the Redmine client
redmine = Redmine(url=REDMINE_URL, username=USERNAME, password=PASSWORD)


@mcp.tool()
def get_all_projects() -> str:
    """Get information about all Redmine projects.

    Returns a formatted list of all projects with their details.
    """
    try:
        projects = redmine.project.all()
        result = []
        for project in projects:
            project_info = f"""Project ID: {project.id}
Name: {project.name}
Description: {project.description if hasattr(project, "description") else "No description"}
Created On: {project.created_on}
Updated On: {project.updated_on}"""
            result.append(project_info)

        return "\n" + "-" * 40 + "\n".join(result) + "\n" + "-" * 40
    except Exception as e:
        return f"Error retrieving projects: {str(e)}"


@mcp.tool()
def get_project_details(project_id: int) -> str:
    """Get detailed information about a specific project.

    Args:
        project_id: The ID of the project to retrieve
    """
    try:
        project = redmine.project.get(project_id)
        details = f"""Project Details:
ID: {project.id}
Name: {project.name}
Identifier: {project.identifier}
Description: {project.description if hasattr(project, "description") else "No description"}
Status: {project.status if hasattr(project, "status") else "Unknown"}
Created On: {project.created_on}
Updated On: {project.updated_on}"""

        # Add custom fields if they exist
        if hasattr(project, "custom_fields"):
            details += "\n\nCustom Fields:"
            for field in project.custom_fields:
                details += f"\n- {field.name}: {field.value}"

        return details
    except Exception as e:
        return f"Error retrieving project {project_id}: {str(e)}"


@mcp.tool()
def get_project_issues(project_id: int, limit: int = 10) -> str:
    """Get issues for a specific project.

    Args:
        project_id: The ID of the project
        limit: Maximum number of issues to retrieve (default: 10)
    """
    try:
        issues = redmine.issue.filter(project_id=project_id, limit=limit)
        result = [f"Issues for Project {project_id}:"]

        for issue in issues:
            issue_info = f"""
Issue #{issue.id}: {issue.subject}
Status: {issue.status.name}
Priority: {issue.priority.name}
Assigned to: {issue.assigned_to.name if hasattr(issue, "assigned_to") else "Unassigned"}
Created: {issue.created_on}
Updated: {issue.updated_on}"""
            result.append(issue_info)

        if not list(issues):
            result.append("\nNo issues found for this project.")

        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving issues for project {project_id}: {str(e)}"


@mcp.tool()
def get_issue_details(issue_id: int) -> str:
    """Get detailed information about a specific issue.

    Args:
        issue_id: The ID of the issue to retrieve
    """
    try:
        issue = redmine.issue.get(issue_id)
        details = f"""Issue Details:
ID: {issue.id}
Subject: {issue.subject}
Description: {issue.description if hasattr(issue, "description") else "No description"}
Status: {issue.status.name}
Priority: {issue.priority.name}
Tracker: {issue.tracker.name}
Project: {issue.project.name}
Author: {issue.author.name}
Assigned to: {issue.assigned_to.name if hasattr(issue, "assigned_to") else "Unassigned"}
Created: {issue.created_on}
Updated: {issue.updated_on}
Due Date: {issue.due_date if hasattr(issue, "due_date") else "Not set"}"""

        # Add custom fields if they exist
        if hasattr(issue, "custom_fields"):
            details += "\n\nCustom Fields:"
            for field in issue.custom_fields:
                details += f"\n- {field.name}: {field.value}"

        return details
    except Exception as e:
        return f"Error retrieving issue {issue_id}: {str(e)}"


@mcp.tool()
def create_issue(
    project_id: int, subject: str, description: str = "", priority_id: int = 2
) -> str:
    """Create a new issue in a project.

    Args:
        project_id: The ID of the project to create the issue in
        subject: The subject/title of the issue
        description: The description of the issue (optional)
        priority_id: The priority ID (default: 2 for Normal)
    """
    try:
        new_issue = redmine.issue.create(
            project_id=project_id,
            subject=subject,
            description=description,
            priority_id=priority_id,
        )
        return f"Issue created successfully!\nIssue ID: {new_issue.id}\nSubject: {subject}\nProject ID: {project_id}"
    except Exception as e:
        return f"Error creating issue: {str(e)}"


@mcp.tool()
def search_issues(query: str, limit: int = 10) -> str:
    """Search for issues across all projects.

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10)
    """
    try:
        # Note: Redmine API search might be limited depending on server configuration
        issues = redmine.issue.filter(limit=limit)
        result = [f"Search results for '{query}':"]
        matching_issues = []

        for issue in issues:
            if query.lower() in issue.subject.lower() or (
                hasattr(issue, "description")
                and issue.description
                and query.lower() in issue.description.lower()
            ):
                issue_info = f"""
Issue #{issue.id}: {issue.subject}
Project: {issue.project.name}
Status: {issue.status.name}
Priority: {issue.priority.name}"""
                matching_issues.append(issue_info)

        if not matching_issues:
            result.append(f"\nNo issues found matching '{query}'")
        else:
            result.extend(matching_issues[:limit])

        return "\n".join(result)
    except Exception as e:
        return f"Error searching issues: {str(e)}"


@mcp.tool()
def get_my_issues(limit: int = 10) -> str:
    """Get issues assigned to the current user.

    Args:
        limit: Maximum number of issues to retrieve (default: 10)
    """
    try:
        # Get current user info
        current_user = redmine.user.get("current")
        issues = redmine.issue.filter(assigned_to_id=current_user.id, limit=limit)

        result = [
            f"Issues assigned to {current_user.firstname} {current_user.lastname}:"
        ]

        for issue in issues:
            issue_info = f"""
Issue #{issue.id}: {issue.subject}
Project: {issue.project.name}
Status: {issue.status.name}
Priority: {issue.priority.name}
Due Date: {issue.due_date if hasattr(issue, "due_date") else "Not set"}"""
            result.append(issue_info)

        if not list(issues):
            result.append("\nNo issues assigned to you.")

        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving your issues: {str(e)}"


@mcp.tool()
def get_project_time_entries(project_id: int, limit: int = 50) -> str:
    """Get time entries for a specific project.

    Args:
        project_id: The ID of the project
        limit: Maximum number of time entries to retrieve (default: 50)
    """
    try:
        time_entries = redmine.time_entry.filter(project_id=project_id, limit=limit)
        result = [f"Time entries for Project {project_id}:"]
        total_hours = 0

        for entry in time_entries:
            entry_info = f"""
Time Entry ID: {entry.id}
Date: {entry.spent_on}
User: {entry.user.name}
Activity: {entry.activity.name}
Hours: {entry.hours}
Comments: {entry.comments if hasattr(entry, 'comments') else 'No comments'}"""
            result.append(entry_info)
            total_hours += float(entry.hours)

        result.append(f"\nTotal hours: {total_hours}")
        
        if not list(time_entries):
            result.append("\nNo time entries found for this project.")

        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving time entries for project {project_id}: {str(e)}"


@mcp.tool()
def create_time_entry(
    issue_id: int = None,
    project_id: int = None, 
    spent_on: str = None,
    hours: float = 7.0,
    activity_id: int = None,
    comments: str = ""
) -> str:
    """Create a new time entry.

    Args:
        issue_id: The ID of the issue (optional, can use project_id instead)
        project_id: The ID of the project (optional if issue_id is provided)
        spent_on: Date in YYYY-MM-DD format (optional, defaults to today)
        hours: Number of hours to log (default: 7.0)
        activity_id: The activity ID (optional, will use default if not specified)
        comments: Comments for the time entry (optional)
    """
    try:
        from datetime import datetime
        
        # Prepare the time entry data
        time_entry_data = {
            'hours': hours,
            'comments': comments
        }
        
        # Add issue or project
        if issue_id:
            time_entry_data['issue_id'] = issue_id
        elif project_id:
            time_entry_data['project_id'] = project_id
        else:
            return "Error: Either issue_id or project_id must be provided"
        
        # Add date (use today if not specified)
        if spent_on:
            time_entry_data['spent_on'] = spent_on
        else:
            time_entry_data['spent_on'] = datetime.now().strftime('%Y-%m-%d')
        
        # Add activity if specified, otherwise let Redmine use default
        if activity_id:
            time_entry_data['activity_id'] = activity_id
        
        # Create the time entry
        new_time_entry = redmine.time_entry.create(**time_entry_data)
        
        return f"""Time entry created successfully!
Time Entry ID: {new_time_entry.id}
Date: {time_entry_data['spent_on']}
Hours: {hours}
Comments: {comments}
{"Issue ID: " + str(issue_id) if issue_id else "Project ID: " + str(project_id)}"""
        
    except Exception as e:
        return f"Error creating time entry: {str(e)}"


@mcp.tool()
def get_activities() -> str:
    """Get all available time tracking activities.
    
    Returns a list of activities that can be used when creating time entries.
    """
    try:
        activities = redmine.enumeration.filter(resource='time_entry_activities')
        result = ["Available Time Entry Activities:"]
        
        for activity in activities:
            activity_info = f"ID: {activity.id} - Name: {activity.name}"
            result.append(activity_info)
            
        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving activities: {str(e)}"


@mcp.tool()
def create_time_entries_bulk(entries: str) -> str:
    """Create multiple time entries at once.
    
    Args:
        entries: JSON string with array of time entries. Each entry should have:
                project_id, spent_on, hours, comments, activity_id (optional)
                
    Example entries format:
    [
        {"project_id": 63547, "spent_on": "2025-08-18", "hours": 7.0, "comments": "bloqueo"},
        {"project_id": 63547, "spent_on": "2025-08-19", "hours": 7.0, "comments": "bloqueo"}
    ]
    """
    try:
        import json
        
        entries_data = json.loads(entries)
        results = []
        
        for entry_data in entries_data:
            try:
                new_time_entry = redmine.time_entry.create(**entry_data)
                results.append(f"✓ Created time entry {new_time_entry.id} for {entry_data['spent_on']} - {entry_data['hours']}h")
            except Exception as e:
                results.append(f"✗ Error creating entry for {entry_data.get('spent_on', 'unknown date')}: {str(e)}")
        
        return "Bulk time entries creation results:\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error processing bulk time entries: {str(e)}"


@mcp.tool()
def delete_time_entry(time_entry_id: int) -> str:
    """Delete a time entry.

    Args:
        time_entry_id: The ID of the time entry to delete
    """
    try:
        redmine.time_entry.delete(time_entry_id)
        return f"Time entry {time_entry_id} deleted successfully!"
    except Exception as e:
        return f"Error deleting time entry {time_entry_id}: {str(e)}"


@mcp.tool()
def find_issue_by_name(project_id: int, issue_subject: str) -> str:
    """Find an issue by its subject/name within a specific project.

    Args:
        project_id: The ID of the project to search in
        issue_subject: The subject/name of the issue to find
    """
    try:
        issues = redmine.issue.filter(project_id=project_id, limit=100)
        matching_issues = []
        
        for issue in issues:
            if issue_subject.lower() in issue.subject.lower():
                issue_info = f"""
Issue #{issue.id}: {issue.subject}
Status: {issue.status.name}
Priority: {issue.priority.name}
Assigned to: {issue.assigned_to.name if hasattr(issue, "assigned_to") else "Unassigned"}"""
                matching_issues.append(issue_info)
        
        if not matching_issues:
            return f"No issues found with subject containing '{issue_subject}' in project {project_id}"
        else:
            result = [f"Issues found with subject containing '{issue_subject}':"]
            result.extend(matching_issues)
            return "\n".join(result)
            
    except Exception as e:
        return f"Error searching for issue: {str(e)}"


@mcp.tool()
def create_time_entry_with_validation(
    project_id: int,
    issue_subject: str,
    spent_on: str,
    hours: float = 7.0,
    comments: str = "",
    activity_id: int = None
) -> str:
    """Create a time entry with validation that the issue exists.

    Args:
        project_id: The ID of the project
        issue_subject: The subject/name of the issue to find and associate time with
        spent_on: Date in YYYY-MM-DD format
        hours: Number of hours to log (default: 7.0)
        comments: Comments for the time entry (optional)
        activity_id: The activity ID (optional)
    """
    try:
        # First, find the issue by subject
        issues = redmine.issue.filter(project_id=project_id, limit=100)
        target_issue = None
        
        for issue in issues:
            if issue_subject.lower() == issue.subject.lower():
                target_issue = issue
                break
        
        if not target_issue:
            return f"Error: No issue found with exact subject '{issue_subject}' in project {project_id}. Use find_issue_by_name to search for similar issues."
        
        # Create time entry for the found issue
        time_entry_data = {
            'issue_id': target_issue.id,
            'spent_on': spent_on,
            'hours': hours,
            'comments': comments
        }
        
        if activity_id:
            time_entry_data['activity_id'] = activity_id
        
        new_time_entry = redmine.time_entry.create(**time_entry_data)
        
        return f"""Time entry created successfully!
Time Entry ID: {new_time_entry.id}
Issue: #{target_issue.id} - {target_issue.subject}
Date: {spent_on}
Hours: {hours}
Comments: {comments}"""
        
    except Exception as e:
        return f"Error creating time entry with validation: {str(e)}"


@mcp.tool()
def get_my_time_entries_today() -> str:
    """Get time entries for the current user for today.
    """
    try:
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get current user
        current_user = redmine.user.get("current")
        
        # Get time entries for today
        time_entries = redmine.time_entry.filter(user_id=current_user.id, spent_on=today, limit=50)
        
        result = [f"Time entries for {current_user.firstname} {current_user.lastname} on {today}:"]
        
        for entry in time_entries:
            entry_info = f"""
Time Entry ID: {entry.id}
Date: {entry.spent_on}
{"Issue: #" + str(entry.issue.id) + " - " + entry.issue.subject if hasattr(entry, 'issue') else "Project: " + entry.project.name}
Hours: {entry.hours}
Activity: {entry.activity.name}
Comments: {entry.comments if hasattr(entry, 'comments') else 'No comments'}"""
            result.append(entry_info)
        
        if not list(time_entries):
            result.append(f"\nNo time entries found for today ({today}).")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error retrieving today's time entries: {str(e)}"


@mcp.tool()
def get_my_time_entries_date(date: str) -> str:
    """Get time entries for the current user for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
    """
    try:
        # Get current user
        current_user = redmine.user.get("current")
        
        # Get time entries for the specified date
        time_entries = redmine.time_entry.filter(user_id=current_user.id, spent_on=date, limit=50)
        
        result = [f"Time entries for {current_user.firstname} {current_user.lastname} on {date}:"]
        
        for entry in time_entries:
            entry_info = f"""
Time Entry ID: {entry.id}
Date: {entry.spent_on}
{"Issue: #" + str(entry.issue.id) + " - " + entry.issue.subject if hasattr(entry, 'issue') else "Project: " + entry.project.name}
Hours: {entry.hours}
Activity: {entry.activity.name}
Comments: {entry.comments if hasattr(entry, 'comments') else 'No comments'}"""
            result.append(entry_info)
        
        if not list(time_entries):
            result.append(f"\nNo time entries found for {date}.")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error retrieving time entries for {date}: {str(e)}"


@mcp.tool()
def get_my_time_entries_range(start_date: str, end_date: str) -> str:
    """Get time entries for the current user within a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    try:
        # Get current user
        current_user = redmine.user.get("current")
        
        # Get time entries for the date range - filter by each date individually
        # since Redmine API range filtering can be inconsistent
        from datetime import datetime, timedelta
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        all_entries = []
        current = start
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            try:
                day_entries = redmine.time_entry.filter(user_id=current_user.id, spent_on=date_str, limit=50)
                all_entries.extend(list(day_entries))
            except:
                pass  # Continue if a specific date fails
            current += timedelta(days=1)
        
        result = [f"Time entries for {current_user.firstname} {current_user.lastname} from {start_date} to {end_date}:"]
        
        # Sort entries by date (most recent first)
        all_entries.sort(key=lambda x: x.spent_on, reverse=True)
        
        for entry in all_entries:
            entry_info = f"""
Time Entry ID: {entry.id}
Date: {entry.spent_on}
{"Issue: #" + str(entry.issue.id) + " - " + entry.issue.subject if hasattr(entry, 'issue') else "Project: " + entry.project.name}
Hours: {entry.hours}
Activity: {entry.activity.name}
Comments: {entry.comments if hasattr(entry, 'comments') else 'No comments'}"""
            result.append(entry_info)
        
        if not all_entries:
            result.append(f"\nNo time entries found for the specified date range.")
        else:
            total_hours = sum(float(entry.hours) for entry in all_entries)
            result.append(f"\nTotal hours in range: {total_hours}")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error retrieving time entries for date range: {str(e)}"


@mcp.tool()
def delete_time_entries_bulk(time_entry_ids: str) -> str:
    """Delete multiple time entries at once.
    
    Args:
        time_entry_ids: JSON string with array of time entry IDs to delete
                       
    Example format: "[123, 124, 125]"
    """
    try:
        import json
        
        ids = json.loads(time_entry_ids)
        results = []
        
        for entry_id in ids:
            try:
                redmine.time_entry.delete(entry_id)
                results.append(f"✓ Deleted time entry {entry_id}")
            except Exception as e:
                results.append(f"✗ Error deleting entry {entry_id}: {str(e)}")
        
        return "Bulk time entries deletion results:\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error processing bulk deletion: {str(e)}"


@mcp.tool()
def replace_time_entries_for_dates(project_id: int, dates_and_hours: str) -> str:
    """Replace all existing time entries for specific dates with new ones.
    
    This function will:
    1. Find all existing time entries for the user on the specified dates
    2. Delete them
    3. Create new time entries with the specified hours
    
    Args:
        project_id: The ID of the project
        dates_and_hours: JSON string with array of objects containing date and hours
                        
    Example format:
    [
        {"date": "2025-08-18", "hours": 7.0, "comments": "desarrollo"},
        {"date": "2025-08-19", "hours": 7.0, "comments": "desarrollo"}
    ]
    """
    try:
        import json
        from datetime import datetime
        
        dates_data = json.loads(dates_and_hours)
        results = []
        
        # Get current user
        current_user = redmine.user.get("current")
        
        for date_entry in dates_data:
            date = date_entry['date']
            hours = date_entry.get('hours', 7.0)
            comments = date_entry.get('comments', '')
            
            results.append(f"\n--- Processing date: {date} ---")
            
            # Step 1: Find existing entries for this date
            try:
                existing_entries = redmine.time_entry.filter(
                    user_id=current_user.id, 
                    spent_on=date, 
                    limit=50
                )
                existing_list = list(existing_entries)
                
                # Step 2: Delete existing entries
                deleted_count = 0
                for entry in existing_list:
                    try:
                        redmine.time_entry.delete(entry.id)
                        results.append(f"✓ Deleted existing entry {entry.id} ({entry.hours}h)")
                        deleted_count += 1
                    except Exception as e:
                        results.append(f"✗ Error deleting entry {entry.id}: {str(e)}")
                
                if deleted_count == 0:
                    results.append("No existing entries found to delete")
                
            except Exception as e:
                results.append(f"Error finding existing entries: {str(e)}")
            
            # Step 3: Create new entry
            try:
                new_time_entry = redmine.time_entry.create(
                    project_id=project_id,
                    spent_on=date,
                    hours=hours,
                    comments=comments
                )
                results.append(f"✓ Created new entry {new_time_entry.id} - {hours}h - '{comments}'")
                
            except Exception as e:
                results.append(f"✗ Error creating new entry: {str(e)}")
        
        return "Replace time entries results:\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error processing replace operation: {str(e)}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")