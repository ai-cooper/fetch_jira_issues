from jira import JIRA
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env file from current directory or home directory
load_dotenv(os.path.expanduser("~/.jira_env"))

# Read from environment variables
jira_token = os.getenv("JIRA_TOKEN")
db_path = os.getenv("JIRA_DB_PATH")

# Jira Cloud URL
jira_url = "https://issues.redhat.com/"

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS jira_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_key TEXT UNIQUE NOT NULL,
    summary TEXT NOT NULL,
    description TEXT,
    priority TEXT,
    status TEXT,
    assignee TEXT,
    security_level TEXT,
    created_date TEXT,
    updated_date TEXT,
    component TEXT,
    issue_type TEXT,
    project TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

try:
    jira = JIRA(server=jira_url, token_auth=jira_token)
    myself = jira.myself()
    print(f"Authenticated as: {myself['displayName']}")

    issues = jira.search_issues(
        'project = RHEL AND issuetype = bug AND created > -30d AND Priority in (Undefined, Major, Critical, Blocker) AND component in componentMatch("^(glibc|kernel|kernel-rt|kernel-automotive)($|/ .*$)")', 
        maxResults=1000
    )

    print(f"Found {len(issues)} issues")

    for issue in issues:
        issue_key = issue.key
        summary = issue.fields.summary
        description = issue.fields.description or "No description available"
        priority = issue.fields.priority.name if issue.fields.priority else "Undefined"
        status = issue.fields.status.name if issue.fields.status else "Unknown"
        assignee = issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned"
        security_level = issue.fields.security.name if hasattr(issue.fields, "security") and issue.fields.security else None
        created_date = issue.fields.created
        updated_date = issue.fields.updated
        issue_type = issue.fields.issuetype.name if issue.fields.issuetype else "Unknown"
        project = issue.fields.project.key if issue.fields.project else "Unknown"
        components = [comp.name for comp in issue.fields.components] if issue.fields.components else []
        component_str = ", ".join(components) if components else "No component"

        print(f'\nIssue: {issue_key}')
        print(f'Summary: {summary}')
        print(f'Priority: {priority}')
        print(f'Status: {status}')
        print(f'Assignee: {assignee}')
        print(f'Components: {component_str}')
        print(f'Security: {security_level}')

	
        cursor.execute('''
            INSERT OR REPLACE INTO jira_issues 
            (issue_key, summary, description, priority, status, assignee, 
             created_date, updated_date, component, issue_type, project, fetched_at, security_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            issue_key, summary, description, priority, status, assignee,
            created_date, updated_date, component_str, issue_type, project,
            datetime.now().isoformat(), security_level
        ))

    conn.commit()
    print(f"\nSuccessfully stored {len(issues)} issues in the database")

    cursor.execute("SELECT COUNT(*) FROM jira_issues")
    print(f"Total issues in database: {cursor.fetchone()[0]}")

    cursor.execute("SELECT priority, COUNT(*) FROM jira_issues GROUP BY priority")
    for priority, count in cursor.fetchall():
        print(f"  {priority}: {count}")

except Exception as e:
    print(f"Error occurred: {str(e)}")
    conn.rollback()

finally:
    conn.close()
    print("\nDatabase connection closed")
