import html
import os
import requests
import re

from typing import List

import html2text

from bs4 import BeautifulSoup
from dotenv import load_dotenv

def get_page_children(base_url: str, page_id: str, auth: tuple) -> List[dict]:
    url = f"{base_url}/rest/api/content/{page_id}/child/page?limit=100"
    children = []
    while url:
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        data = resp.json()
        children.extend(data.get('results', []))
        url = data.get('_links', {}).get('next')
        if url and not url.startswith('http'):
            url = base_url + url
    return children

def get_page_content(base_url: str, page_id: str, auth: tuple) -> dict:
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage,title"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    return resp.json()

def save_page_content(page: dict, page_dir: str, base_url: str = None, auth: tuple = None):
    title = page['title'].replace('/', '_')
    html_content = page['body']['storage']['value']
    # Download images if requested
    if base_url and auth:
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')
        ac_images = soup.find_all('ac:image')
        img_dir = os.path.join(page_dir, "images")
        if img_tags or ac_images:
            os.makedirs(img_dir, exist_ok=True)
        # Handle normal <img> tags
        for img in img_tags:
            src = img.get('src')
            if src:
                if src.startswith('/wiki'):
                    img_url = base_url.rstrip('/') + src
                elif src.startswith('http'):
                    img_url = src
                else:
                    continue
                img_name = os.path.basename(src.split('?')[0])
                img_path = os.path.join(img_dir, img_name)
                try:
                    resp = requests.get(img_url, auth=auth, headers={"X-Atlassian-Token": "no-check"})
                    resp.raise_for_status()
                    with open(img_path, 'wb') as f:
                        f.write(resp.content)
                    img['src'] = os.path.relpath(img_path, page_dir)
                except Exception as e:
                    print(f"Failed to download image {img_url}: {e}")
        # Handle <ac:image> tags
        for ac_img in ac_images:
            ri_attachment = ac_img.find('ri:attachment')
            if ri_attachment and ri_attachment.has_attr('ri:filename'):
                filename = ri_attachment['ri:filename']
                page_id = page['id']
                # Get attachment download link from REST API
                attachment_api = f"{base_url}/rest/api/content/{page_id}/child/attachment?filename={filename}"
                try:
                    resp = requests.get(attachment_api, auth=auth)
                    resp.raise_for_status()
                    results = resp.json().get('results', [])
                    if results and '_links' in results[0] and 'download' in results[0]['_links']:
                        download_link = results[0]['_links']['download']
                        if download_link.startswith('/'):
                            download_url = base_url.rstrip('/') + download_link
                        else:
                            download_url = download_link
                        img_path = os.path.join(img_dir, filename)
                        img_resp = requests.get(download_url, auth=auth, headers={"X-Atlassian-Token": "no-check"})
                        img_resp.raise_for_status()
                        with open(img_path, 'wb') as f:
                            f.write(img_resp.content)
                        new_img_tag = soup.new_tag('img', src=os.path.relpath(img_path, page_dir))
                        ac_img.replace_with(new_img_tag)
                    else:
                        print(f"Attachment not found for {filename} on page {page_id}")
                except Exception as e:
                    print(f"Failed to download attachment image for {filename}: {e}")
        html_content = str(soup)
    markdown_content = html2text.html2text(html_content)
    # Replace 2 consecutive new lines with one line
    markdown_content = markdown_content.replace('\n\n', '\n')
    # Add H1 title at the top
    h1_title = f"# {page['title']}\n\n"
    markdown_content = h1_title + markdown_content
    filename = os.path.join(page_dir, f"{title}_{page['id']}.md")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def backup_confluence(base_url: str, root_page_id: str, email: str, api_key: str, output_dir: str = 'confluence_backup'):
    os.makedirs(output_dir, exist_ok=True)
    auth = (email, api_key)  # Use email for username
    def recurse(page_id, parent_dir):
        page = get_page_content(base_url, page_id, auth)
        title = page['title'].replace('/', '_')
        page_dir = os.path.join(parent_dir, f"{title}_{page['id']}")
        os.makedirs(page_dir, exist_ok=True)
        print(f"Saving: {page['title']} (ID: {page['id']}) ...")
        save_page_content(page, page_dir, base_url, auth)
        children = get_page_children(base_url, page_id, auth)
        for child in children:
            recurse(child['id'], page_dir)
    recurse(root_page_id, output_dir)

if __name__ == "__main__":
    load_dotenv()  # load environment variables from .env file
    BASE_URL = os.getenv('CONFLUENCE_BASE_URL', 'https://your-domain.atlassian.net/wiki')
    ROOT_PAGE_ID = os.getenv('CONFLUENCE_ROOT_PAGE_ID', '123456')
    API_KEY = os.getenv('CONFLUENCE_API_KEY', 'your-api-key')
    EMAIL = os.getenv('CONFLUENCE_EMAIL', 'your-email@domain.com')
    OUTPUT_DIR = os.getenv('CONFLUENCE_OUTPUT_DIR', 'confluence_backup')
    backup_confluence(BASE_URL, ROOT_PAGE_ID, EMAIL, API_KEY, OUTPUT_DIR)
