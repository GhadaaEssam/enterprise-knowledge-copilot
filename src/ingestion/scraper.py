import os
import re
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Configuration
START_URL = "https://engineering.hmn.md/"
BASE_DOMAIN = urlparse(START_URL).netloc
OUTPUT_DIR = "./hmn_engineering_docs"

# Track visited URLs
visited_urls = set()
urls_to_visit = [START_URL]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_filename(url_path):
    """Generate a clean file name based on the URL path."""
    path = url_path.strip("/")
    if not path:
        return "index.md"
    # Replace slashes and invalid filename characters with underscores
    filename = re.sub(r'[\/\\:\*\?"<>\|]', '_', path)
    return f"{filename}.md"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Author/Researcher"
}

print(f"Starting crawl of {START_URL}...")

while urls_to_visit:
    current_url = urls_to_visit.pop(0)
    
    # Normalize URL (strip fragments/anchors)
    current_url = current_url.split('#')[0]
    
    if current_url in visited_urls:
        continue
    
    visited_urls.add(current_url)
    print(f"Scraping: {current_url}")
    
    try:
        response = requests.get(current_url, headers=headers, timeout=10)
        if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Discover internal links to crawl further
        for link in soup.find_all('a', href=True):
            full_url = urljoin(current_url, link['href']).split('#')[0]
            parsed_full = urlparse(full_url)
            
            # Stay within the target domain
            if parsed_full.netloc == BASE_DOMAIN and full_url not in visited_urls:
                urls_to_visit.append(full_url)
        
        # Target the primary content container (fallback to <body> if specific tag not found)
        main_content = (
            soup.find('main') 
            or soup.find('article') 
            or soup.find('div', class_=re.compile(r'content|main|article', re.I))
            or soup.body
        )
        
        if main_content:
            # Convert HTML to Markdown
            markdown_text = md(str(main_content), heading_style="ATX")
            
            # Save file
            parsed_url = urlparse(current_url)
            filename = sanitize_filename(parsed_url.path)
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Source: {current_url}\n\n")
                f.write(markdown_text)
                
    except Exception as e:
        print(f"Failed to process {current_url}: {e}")

print(f"\nDone! Scraped {len(visited_urls)} pages to `{OUTPUT_DIR}`.")