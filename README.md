# Confluence Markdown Download

## Setup
1. Edit the `template.env` file with your own environment values, then rename it to `.env`.
2. Install dependencies using the `uv sync` command.

## .env Example
```
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_ROOT_PAGE_ID=123456
CONFLUENCE_API_KEY=your-api-key
CONFLUENCE_OUTPUT_DIR=confluence_backup
```

## Usage
1. With the `.env` file ready, run the backup script:
   ```bash
   python confluence_backup.py
   ```
2. All pages will be saved as HTML files in the specified OUTPUT_DIR (default: confluence_backup).

## Features
- Recursively backs up all pages under the specified root page ID
- Saves each page's HTML content as a file
- Supports configuration via environment variables

## Notes
- Use an API Key (token) issued by Atlassian.
- If you need additional features (e.g., markdown conversion), let me know.
