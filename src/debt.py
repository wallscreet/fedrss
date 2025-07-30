import feedparser
import re
from dataclasses import dataclass
from typing import Optional
import time
from datetime import datetime


@dataclass
class DebtEntry:
    date: str
    public_debt: float
    intragovernmental: float
    total_debt: float
    pub_date: str

def parse_debt_content(content: str) -> tuple[float, float, float]:
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

def fetch_debt_data(url: str, num_posts: int = 20) -> list[DebtEntry]:
    """
    Fetch and parse the most recent posts from the RSS feed.
    """
    feed = feedparser.parse(url)
    entries = []
    
    for entry in feed.entries[:num_posts]:
        date = entry.title.split("for ")[-1]  # Extract date from title
        public_debt, intragovernmental, total_debt = parse_debt_content(entry.content[0].value)
        entries.append(DebtEntry(
            date=date,
            public_debt=public_debt,
            intragovernmental=intragovernmental,
            total_debt=total_debt,
            pub_date=entry.published
        ))
    
    return entries

def format_currency(amount: float) -> str:
    """
    Format a float as a currency string with commas and two decimal places.
    """
    return f"${amount:,.2f}"

def display_debt_clock(entries: list[DebtEntry]):
    """
    Display the debt data in a real-time clock format.
    """
    # Clear console (works on Unix-like systems and Windows)
    print("\033[H\033[J", end="")  # ANSI escape code to clear screen
    print("US Debt to the Penny")
    print("=" * 40)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)
    
    for entry in entries:
        print(f"Date: {entry.date}")
        print(f"  Debt Held by the Public: {format_currency(entry.public_debt)}")
        print(f"  Intragovernmental Holdings: {format_currency(entry.intragovernmental)}")
        print(f"  Total Public Debt Outstanding: {format_currency(entry.total_debt)}")
        print(f"  Published: {entry.pub_date}")
        print("-" * 40)
        

def main():
    # Fetch the most recent two posts
    entries = fetch_debt_data("https://treasurydirect.gov/NP_WS/debt/feeds/recent")
    
    display_debt_clock(entries)

if __name__ == "__main__":
    main()