from dataclasses import dataclass, field
import os
import re
import json
from pathlib import Path
import feedparser
from feeds import BaseRSS, Feed
from datetime import datetime
from zoneinfo import ZoneInfo

def format_currency(amount: float) -> str:
    """
    Format a float as a currency string.
    """
    return f"${amount:,.2f}"


@dataclass
class DebtEntry:
    """
    Dataclass to represent a daily debt entry for the national debt.
    """
    date: str
    public_debt: float
    intragovernmental: float
    total_debt: float
    pub_date: str


@dataclass
class TreasuryDirect_RSS(BaseRSS):
    """
    RSS feeds for the U.S. Department of the Treasury's Bureau of the Fiscal Service.
    """
    feeds: list[Feed] = field(default_factory=lambda: [
            Feed(
                name="Debt To The Penny",
                base_url="https://treasurydirect.gov/NP_WS/debt/feeds/recent",
                description="The most recent Debt to the Penny reported values."
            ),
    ])

    def parse_debt_content(self, content: str) -> tuple[float, float, float]:
        """
        Parse the content:encoded field to extract debt values.
        """
        public_debt = re.search(r"Debt Held by the Public:</em>\s*([\d,]+\.\d{2})", content)
        intragovernmental = re.search(r"Intragovernmental Holdings:</em>\s*([\d,]+\.\d{2})", content)
        total_debt = re.search(r"Total Public Debt Outstanding:</em>\s*([\d,]+\.\d{2})", content)
        
        if not all([public_debt, intragovernmental, total_debt]):
            raise ValueError("Could not parse debt values from content")
        
        # Convert strings to floats, removing commas
        return (
            float(public_debt.group(1).replace(",", "")),
            float(intragovernmental.group(1).replace(",", "")),
            float(total_debt.group(1).replace(",", ""))
        )

    def fetch_debt_data(self, url: str, num_posts: int = 20) -> list[DebtEntry]:
        """
        Fetch and parse the most recent n posts from the RSS feed.
        """
        feed = feedparser.parse(url)
        entries = []
        
        for entry in feed.entries[:num_posts]:
            date = entry.title.split("for ")[-1]  # Extract date from title
            public_debt, intragovernmental, total_debt = self.parse_debt_content(entry.content[0].value)
            
            entries.append(DebtEntry(
                date=date,
                public_debt=public_debt,
                intragovernmental=intragovernmental,
                total_debt=total_debt,
                pub_date=entry.published
            ))
        
        return entries
    
    def debt_data_periodic(self, start_date: str = "07/01/2025", end_date: str = "07/29/2025"):
        """
        Fetch and display US debt data for a specific period.
        """

        with open('../debt_data_json/debt_data.json', 'r') as file:
            data = json.load(file)

        start_date = start_date
        end_date = end_date

        start_total_debt = None
        end_total_debt = None

        sep_single = "-" * 55
        sep_double = "=" * 55

        for entry in data:
            if entry["date"] == start_date:
                start_public_debt = entry["public_debt"]
                start_intragovernmental = entry["intragovernmental"]
                start_total_debt = entry["total_debt"]
            if entry["date"] == end_date:
                end_public_debt = entry["public_debt"]
                end_intragovernmental = entry["intragovernmental"]
                end_total_debt = entry["total_debt"]

        # Calc diffs
        if start_total_debt is not None and end_total_debt is not None:
            public_debt_diff = end_public_debt - start_public_debt
            public_debt_sign = "+" if public_debt_diff >= 0 else "-"
            intragovernmental_diff = end_intragovernmental - start_intragovernmental
            intragovernmental_sign = "+" if intragovernmental_diff >= 0 else "-"
            total_debt_diff = end_total_debt - start_total_debt
            total_debt_sign = "+" if total_debt_diff >= 0 else "-"
        else:
            public_debt_diff = None
            public_debt_sign = ""
            intragovernmental_diff = None
            intragovernmental_sign = ""
            total_debt_diff = None
            total_debt_sign = ""
            print("Error: One or both dates not found in the data.")

        # Time calcs
        start_date_obj = datetime.strptime(start_date, "%m/%d/%Y")
        end_date_obj = datetime.strptime(end_date, "%m/%d/%Y")
        days_elapsed = (end_date_obj - start_date_obj).days

        gmt_time = datetime.now(ZoneInfo("UTC"))
        eastern_time = datetime.now(ZoneInfo("America/New_York"))

        # Output
        print("\033[H\033[J", end="")  # ANSI escape code to clear screen
        print("\n")
        print(f"  TreasuryDirect - US Debt to the Penny")
        print(f"  {sep_double}")
        print(f"  Time Run: {gmt_time.strftime('%Y-%m-%d %H:%M:%S')} (GMT)")
        print(f"            {eastern_time.strftime('%Y-%m-%d %H:%M:%S')} (US/EST)")
        print(f"  {sep_double}")

        print(f"  Date: {start_date}")
        print(f"    Debt Held by the Public:       {format_currency(start_public_debt)}")
        print(f"    Intragovernmental Holdings:    {format_currency(start_intragovernmental)}")
        print(f"    Total Public Debt Outstanding: {format_currency(start_total_debt)}")
        print(f"  {sep_single}")

        print(f"  Date: {end_date}")
        print(f"    Debt Held by the Public:       {format_currency(end_public_debt)}")
        print(f"    Intragovernmental Holdings:    {format_currency(end_intragovernmental)}")
        print(f"    Total Public Debt Outstanding: {format_currency(end_total_debt)}")
        print(f"  {sep_single}")

        print(f"  {sep_single}")
        print(f"  Debt Accumulated Over Period: {start_date} to {end_date}")
        print(f"  {sep_single}")
        print(f"  Days Elapsed:                    {days_elapsed}")
        print(f"  Debt Held by the Public:         {public_debt_sign} {format_currency(public_debt_diff)}")
        print(f"  Intragovernmental Holdings:      {intragovernmental_sign} {format_currency(intragovernmental_diff)}")
        print(f"  Total Public Debt Outstanding:   {total_debt_sign} {format_currency(total_debt_diff)}")
        print(f"  Total Debt Accumulation Rate:   {total_debt_sign} {format_currency(total_debt_diff / (days_elapsed * 24))} / hr")
        print(f"  {sep_double}")
        print("\n")
    
    def sync_debt_data_to_json(self, entries: list[DebtEntry], base_dir="../debt_data_json"):
        """
        Sync the debt data to a JSON file.
        Prevents duplication by comparing dates.
        """
        os.makedirs(base_dir, exist_ok=True)
        json_path = Path(base_dir) / "debt_data.json"

        # Load existing data or initialize structure
        if json_path.exists():
            with open(json_path, "r") as f:
                data = json.load(f)
        else:
            data = []

        # Deduplication check based on date
        existing_dates = {entry['date'] for entry in data}
        
        for entry in entries:
            if entry.date in existing_dates:
                print(f"⚠️ Entry for {entry.date} already exists. Skipping.")
                continue
            
            cleaned_entry = {
                "date": entry.date,
                "public_debt": entry.public_debt,
                "intragovernmental": entry.intragovernmental,
                "total_debt": entry.total_debt,
                "pub_date": entry.pub_date
            }
            data.append(cleaned_entry)

        # Save to JSON
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✔️ Synced debt data to {json_path}")