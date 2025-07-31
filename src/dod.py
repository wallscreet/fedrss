from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
from pathlib import Path
from feeds import Feed, BaseRSS
from dataclasses import dataclass, field
import feedparser


def sanitize_filename(name: str) -> str:
    # replace spaces with underscores, strip forbidden filesystem chars
    name = name.strip().replace(" ", "_")
    # remove anything that's not alphanumeric, underscore, hyphen, or dot
    return re.sub(r"[^\w\-.]", "", name)


@dataclass
class DOD_RSS(BaseRSS):
    """
    RSS feeds for the United States Department of Defense (DOD).
    """
    feeds: list[Feed] = field(default_factory=lambda: [
            Feed(
                name="Feature Stories",
                content_type="800",
                base_url= "https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx",
                site="945",
                max=10,
                description="Feature stories from the Department of Defense."
            ),
            Feed(
                name="News",
                content_type="1",
                base_url="https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx",
                site="945",
                max=10,
                description="News from the Department of Defense."
            ),
            Feed(
                name="Releases",
                content_type="9",
                base_url="https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx",
                site="945",
                max=10,
                description="Press releases from the Department of Defense."
            ),
            Feed(
                name="Contract Announcements",
                content_type="400",
                base_url="https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx",
                site="945",
                max=10,
                description="U.S. Department of Defense Contracts valued at $7.5 million or more are announced each business day at 5 p.m."
            ),
            Feed(
                name="Advisories",
                content_type="500",
                base_url="https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx",
                max=10,
                description="Advisories from the Department of Defense."
            )
    ])

    def get_contract_announcements_urls(self) -> list[str]:
        """
        Returns a list of URLs for contract announcements.
        """
        contracts_rss_url = self.get_url_by_name("Contract Announcements")
        entries = feedparser.parse(contracts_rss_url)

        return entries


    def extract_contract_awards_content(self, url: str) -> list[str]:
        """
        Extracts paragraphs from a dod contract announcement page.
        """
        output_dir = Path("dod_awards_json")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        body_div = soup.find("div", class_="body")
        if body_div is None:
            raise RuntimeError("Could not find <div class='body'> on the page")

        raw_title = soup.find("h1").get_text(strip=True)
        page_title = sanitize_filename(raw_title)

        out_path = output_dir / f"{page_title}.json"

        if out_path.exists():
            print(f"File {out_path} already exists, skipping extraction.")
        else:
            paragraphs = [p.get_text(strip=True) for p in body_div.find_all('p') if p.get_text(strip=True)]

            # Write to JSON file
            with open(f"dod_awards_json/{page_title}.json", "w", encoding="utf-8") as f:
                json.dump(paragraphs, f, ensure_ascii=False, indent=2)

            print(f"Extracted {len(paragraphs)} paragraphs and saved to contracts.json")
            print(f"Page Title: {page_title}")


def main():
    dod = DOD_RSS()
    entries = dod.get_contract_announcements_urls()

    print(entries["entries"][0]["link"])
    for entry in entries['entries']:
        title = entry.get('title', 'No Title')
        link = entry.get('link', None)
        if link:
            print(f"Processing: {title} - {link}")
            dod.extract_contract_awards_content(link)
        else:
            print(f"Skipping entry without link: {title}")

if __name__ == "__main__":
    main()
    
    