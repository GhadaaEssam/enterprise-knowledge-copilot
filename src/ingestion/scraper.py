"""Small, dependency-free-to-call web scraper used by the ingestion pipeline."""

from __future__ import annotations

import re
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as markdownify


DEFAULT_START_URL = "https://engineering.hmn.md/"
DEFAULT_HEADERS = {"User-Agent": "Enterprise Knowledge Copilot ingestion bot"}


def sanitize_filename(url_path: str) -> str:
    """Return a stable, filesystem-safe Markdown filename for a URL path."""
    path = url_path.strip("/")
    if not path:
        return "index.md"
    return f"{re.sub(r'[\\/\\\\:\\*\\?\"<>\\|]', '_', path)}.md"


def scrape_site(
    start_url: str,
    output_dir: str | Path,
    *,
    timeout: int = 10,
    session: requests.Session | None = None,
) -> list[Path]:
    """Crawl same-domain HTML pages and write their main content as Markdown.

    Returns the files written.  Network failures on individual pages are skipped so
    one unavailable page does not discard the rest of an ingestion run.
    """
    parsed_start = urlparse(start_url)
    if parsed_start.scheme not in {"http", "https"} or not parsed_start.netloc:
        raise ValueError("start_url must be an absolute HTTP(S) URL")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    client = session or requests.Session()
    base_domain = parsed_start.netloc
    visited: set[str] = set()
    pending = deque([start_url])
    written: list[Path] = []

    while pending:
        current_url = pending.popleft().split("#", 1)[0]
        if current_url in visited:
            continue
        visited.add(current_url)

        try:
            response = client.get(current_url, headers=DEFAULT_HEADERS, timeout=timeout)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                continue
        except requests.RequestException:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            candidate = urljoin(current_url, link["href"])
            parsed = urlparse(candidate)
            if parsed.netloc == base_domain and parsed.scheme in {"http", "https"}:
                normalized = urlunparse(parsed._replace(fragment=""))
                if normalized not in visited:
                    pending.append(normalized)

        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=re.compile(r"content|main|article", re.I))
            or soup.body
        )
        if not main_content:
            continue

        output_file = destination / sanitize_filename(urlparse(current_url).path)
        output_file.write_text(
            f"# Source: {current_url}\n\n{markdownify(str(main_content), heading_style='ATX')}",
            encoding="utf-8",
        )
        written.append(output_file)

    return written


if __name__ == "__main__":
    files = scrape_site(DEFAULT_START_URL, "data/raw/hmn_engineering_docs")
    print(f"Scraped {len(files)} pages.")