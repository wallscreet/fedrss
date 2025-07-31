from dataclasses import dataclass, field
from typing import Optional, List
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from pathlib import Path
import json


@dataclass
class Feed:
    """
    Base class for rss feeds.
    """
    name: str
    base_url: str
    description: str = ""
    content_type: Optional[str] = None
    site: Optional[str] = None
    max: Optional[int] = None
    url: str = field(init=False)

    def __post_init__(self):
        params = {}
        if self.site is not None:
            params["Site"] = self.site
        if self.content_type is not None:
            params["ContentType"] = self.content_type
        if self.max is not None:
            params["Max"] = str(self.max)

        query_string = urlencode(params)
        self.url = f"{self.base_url}?{query_string}" if query_string else self.base_url


@dataclass
class BaseRSS:
    """
    Base class for RSS sources to contain their feeds.
    """
    feeds: List[Feed]

    def get_url_by_name(self, name: str) -> Optional[str]:
        feed = next((f for f in self.feeds if f.name == name), None)
        if not feed:
            raise ValueError(f"No feed found with name '{name}'")
        return feed.url



@dataclass
class GovInfo_RSS(BaseRSS):
    """
    RSS feeds for the U.S. Government Publishing Office (GPO) and the Government Publishing Office (GPO).
    """
    feeds: list[Feed] = field(default_factory=lambda: [
            Feed(
                name="Congressional Bills",
                base_url="https://www.govinfo.gov/rss/bills.xml",
                description="Provides access to newly published GovInfo content from the Congressional Bills. Congressional bills are legislative proposals from the House of Representatives and Senate within the United States Congress."
            ),
            Feed(
                name="Congressional Bills (Enrolled)",
                base_url="https://www.govinfo.gov/rss/bills-enr.xml",
                description="Provides access to newly published GovInfo content from the Congressional Bills- Enrolled. Enrolled bills are the final version of a bill passed by both the House and Senate and sent to the President for signature."
            ),
            Feed(
                name="Public and Private Laws",
                base_url="https://www.govinfo.gov/rss/plaw.xml",
                description="Provides access to newly published GovInfo content from the Public and Private Laws. Public and private laws are also known as slip laws. A slip law is an official publication of the law and is competent evidence admissible in all state and Federal courts and tribunals of the United States. Public laws affect society as a whole, while private laws affect an individual, family, or small group."
            ),
            Feed(
                name="Compilation of Presidential Documents",
                base_url="https://www.govinfo.gov/rss/dcpd.xml",
                description="Provides access to newly published GovInfo content from the Compilation of Presidential Documents. The Compilation of Presidential Documents collection consists of the official publications of materials released by the White House Press Secretary. The Compilation of Presidential Documents is published by the Office of the Federal Register (OFR), National Archives and Records Administration (NARA)."
            ),
            Feed(
                name="Statutes at Large",
                base_url="https://www.govinfo.gov/rss/statute.xml",
                description="Provides access to newly published GovInfo content from the United States Statutes at Large. The United States Statutes at Large, typically referred to as the Statutes at Large, is the permanent collection of all laws and resolutions enacted during each session of Congress. The Statutes at Large is prepared and published by the Office of the Federal Register (OFR), National Archives and Records Administration (NARA)."
            ),
            Feed(
                name="Budget of the US Government",
                base_url="https://www.govinfo.gov/rss/budget.xml",
                description="Provides access to newly published GovInfo content from the Budget of the United States Government. Issued by the Office of Management and Budget (OMB), the Budget of the United States Government is a collection of documents that contains the budget message of the President, information about the President's budget proposals for a given fiscal year, and other budgetary publications that have been issued throughout the fiscal year."
            ),
            Feed(
                name="Economic Indicators",
                base_url="https://www.govinfo.gov/rss/econi.xml",
                description="Provides access to newly published GovInfo content from the Economic Indicators. Available from April 1995 forward, this monthly publication is prepared by the Council of Economic Advisers for the Joint Economic Committee. It provides economic information on gross domestic product, income, employment, production, business activity, prices, money, credit, security markets, Federal finance, and international statistics."
            )
    ])


@dataclass
class FederalReserve_RSS(BaseRSS):
    """
    RSS feeds for the Federal Reserve Board.
    """
    feeds: list[Feed] = field(default_factory=lambda: [
        Feed(
            name="All Speeches and Testimony",
            base_url="https://www.federalreserve.gov/feeds/speeches_and_testimony.xml",
            description="All speeches and testimony by members of the Federal Reserve Board."
        ),
        Feed(
            name="Press Releases",
            base_url="https://www.federalreserve.gov/feeds/press_all.xml",
            description="All press releases from the Federal Reserve Board."
        )
    ])

    def fetch_fed_speech(self, url: str) -> dict:
        """
        Fetch an individual speech from the FRB All Speeches and Testimony feed.
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.find('h3').get_text(strip=True)

        # Extract speaker
        speaker_tag = soup.find('p', class_='speaker')
        speaker = speaker_tag.get_text(strip=True) if speaker_tag else None

        # Extract date (convert to ISO format)
        date_tag = soup.find('p', class_='article__time')
        date_raw = date_tag.get_text(strip=True) if date_tag else None
        date = datetime.strptime(date_raw, "%B %d, %Y").isoformat() if date_raw else None

        # Extract location (found in <em> inside the first paragraph)
        location_tag = soup.find('p', class_='location')
        location = location_tag.get_text(strip=True) if location_tag else None
        content_div = soup.find('div', class_='col-xs-12 col-sm-8 col-md-8')
        if content_div:
            first_para = content_div.find('p')
            em = first_para.find('em') if first_para else None

        # Extract full content for summarization
        paragraphs = content_div.find_all('p') if content_div else []
        content = "\n".join(p.get_text(strip=True) for p in paragraphs)

        return {
            "title": title,
            "speaker": speaker,
            "date": date,
            "location": location,
            "url": url,
            "content": content  # You can optionally omit or truncate here
        }

    def append_speech_to_json(self, speech: dict, base_dir="../fed_speeches_json"):
        """
        Append a speech dict to a JSON file grouped by speaker.
        Prevents duplication by comparing URLs.
        """
        os.makedirs(base_dir, exist_ok=True)

        speaker_slug = speech['speaker'].lower().replace(" ", "_")
        json_path = Path(base_dir) / f"{speaker_slug}.json"

        # Load existing data or initialize structure
        if json_path.exists():
            with open(json_path, "r") as f:
                data = json.load(f)
        else:
            data = {
                "speaker": speech["speaker"],
                "speeches": []
            }

        # Deduplication check based on URL
        existing_urls = {entry.get("url") for entry in data.get("speeches", [])}
        if speech.get("url") in existing_urls:
            print(f"⚠️ Speech already exists in {json_path}. Skipping.")
            return

        cleaned_speech = {
            "title": speech["title"],
            "date": speech["date"],
            "location": speech["location"],
            "url": speech.get("url"),
            "content": speech["content"]
        }

        data["speeches"].append(cleaned_speech)

        # Save to JSON
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✔️ Appended new speech to {json_path}")
