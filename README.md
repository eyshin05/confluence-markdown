# Confluence Markdown Download

## Setup
1. Edit the `template.env` file with your own environment values, then rename it to `.env`.
2. Install dependencies using the `uv sync` command.

## .env Example
```
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_ROOT_PAGE_ID=123456
CONFLUENCE_API_KEY=your-api-key
CONFLUENCE_EMAIL=your-email@domain.com
CONFLUENCE_OUTPUT_DIR=confluence_backup
```

## Usage
1. With the `.env` file ready, run the backup script:
   ```bash
   python confluence_backup.py
   ```
2. All pages will be saved as Markdown files in a tree structure under the specified OUTPUT_DIR (default: confluence_backup). Each page will have its own folder, with images downloaded to an `images/` subfolder and attached files to a `files/` subfolder. The page title will appear as an H1 at the top of each markdown file.

## Features
- Recursively backs up all pages under the specified root page ID
- Saves each page's content as a Markdown file (`.md`)
- Downloads all images (including Confluence attachments and macros) and updates image links
- Downloads all attached files and updates file links in the markdown
- Preserves the Confluence page tree as a folder structure
- Adds the page title as an H1 at the top of each markdown file
- Supports configuration via environment variables

## Notes
- Use an API Key (token) issued by Atlassian and your Atlassian email address.
- If you need additional features or encounter issues, let me know.
