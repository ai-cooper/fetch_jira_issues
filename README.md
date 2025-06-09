# fetch_jira_issues

# 🐛 fetch_jira_issues.py

A Python script that connects to a Jira Cloud instance (e.g. Red Hat's Jira), fetches recent high-priority issues related to key components like `glibc` and `kernel`, and stores them into a local SQLite database for further analysis.

---

## 📦 Features

- Authenticates with Jira using credentials from a `.env` file
- Fetches issues from the last 30 days, filtered by component and priority
- Extracts metadata: key, summary, description, status, assignee, etc.
- Saves data into an SQLite database
- Prints summary statistics by issue priority

---

## 🛠️ Prerequisites

- Python 3.6+
- `jira` and `python-dotenv` packages:

```bash
pip install jira python-dotenv
```

## 📁 Environment File (.env)

Create a file named .jira_env in your home directory with the following:

```
JIRA_EMAIL=your-email@example.com
JIRA_TOKEN=your-api-token
JIRA_DB_PATH=/Users/yourname/path/to/jira.db
```
Make sure to secure it:
```
chmod 600 ~/.jira_env
```

## ▶️ Usage

Run the script:
```
python fetch_jira_issues.py
```
Expected output:
	•	Authenticates to Jira
	•	Fetches recent issues
	•	Saves to SQLite database
	•	Shows issue counts and priority stats

 ## 🗃️ SQLite Schema

The database includes a table named jira_issues with the following structure:
```
CREATE TABLE jira_issues (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_key TEXT UNIQUE NOT NULL,
  summary TEXT NOT NULL,
  description TEXT,
  priority TEXT,
  status TEXT,
  assignee TEXT,
  created_date TEXT,
  updated_date TEXT,
  component TEXT,
  issue_type TEXT,
  project TEXT,
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🤖 Claude Desktop + MCP Tips: Summarize Jira Issues

You can use Claude Desktop with MCP and the SQLite MCP server to ask AI for analysis and summarization.

🔧 Setup MCP SQLite Server

In your Claude Desktop config (mcpServers), add (e.g. /Users/you/Library/Application Support/Claude/claude_desktop_config.json for Mac users):
```
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "/Users/You/your_database.db"]
    }
    
}
```
This exposes your SQLite database to Claude via the MCP protocol.

## 💬 Ask Claude

Here are some example prompts to use in Claude Desktop:
```
•List all issue keys
“Connect SQLite, and analyze JIRA issues from jira_issues table and provide a concise summary
for all issues: Issue Key: {issue_key} Summary: {summary} Component: {component} Priority:
{priority} Description: {description} Please provide:
1. Root Cause Analysis: What seems to be the underlying problem?
2. Impact Assessment: How severe is this issue?
3. Technical Summary: Key technical details in plain language
4. Recommended Actions: Suggested next steps
5. Keywords: 3-5 relevant tags for categorization”

```
Claude can then read from the SQLite backend, analyze descriptions, and generate insights.

⚠️ Tip: Avoid asking for summaries of issues with restricted security levels such as Red Hat Employee only.

⸻

## 📄 License

This project is licensed under the MIT License.

⸻

## ✉️ Feedback / Questions

Feel free to open an issue or contribute improvements via pull request.
