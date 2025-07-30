import feedparser
import re
from dataclasses import dataclass
from typing import Optional
import time
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass
class DebtEntry:
    date: str
    public_debt: float
    intragovernmental: float
    total_debt: float
    pub_date: str


sep_double = "=" * 55
sep_single = "-" * 55


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


def fetch_debt_data(url: str, num_posts: int = 2) -> list[DebtEntry]:
    """
    Fetch and parse the most recent n posts from the RSS feed.
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
    Format a float as a currency string.
    """
    return f"${amount:,.2f}"


def display_debt_clock(entries: list[DebtEntry]):
    """
    Display the daily debt data pulled.
    """
    gmt_time = datetime.now(ZoneInfo("UTC"))
    eastern_time = datetime.now(ZoneInfo("America/New_York"))

    # Clear console (works on Unix-like systems and Windows)
    print("\033[H\033[J", end="")  # ANSI escape code to clear screen
    print("\n")
    print(f"  TreasuryDirect - US Debt to the Penny")
    print(f"  {sep_double}")
    print(f"  Time Run: {gmt_time.strftime('%Y-%m-%d %H:%M:%S')} (GMT)")
    print(f"            {eastern_time.strftime('%Y-%m-%d %H:%M:%S')} (US/EST)")
    print(f"  {sep_double}")
    
    for entry in entries:
        print(f"  Date: {entry.date}")
        print(f"    Debt Held by the Public: {format_currency(entry.public_debt)}")
        print(f"    Intragovernmental Holdings: {format_currency(entry.intragovernmental)}")
        print(f"    Total Public Debt Outstanding: {format_currency(entry.total_debt)}")
        print(f"    Published: {entry.pub_date}")
        print(f"  {sep_single}")


def display_math(entries: list[DebtEntry]):
    print(f"  {sep_single}")
    print("  Day Over Day Diffs")
    print(f"  {sep_single}")

    debt_held_by_public_diff = entries[0].public_debt - entries[1].public_debt
    intragovernmental_diff = entries[0].intragovernmental - entries[1].intragovernmental
    total_debt_diff = entries[0].total_debt - entries[1].total_debt

    print(f"  Debt Held by the Public: {format_currency(debt_held_by_public_diff)}")
    print(f"  Intragovernmental Holdings: {format_currency(intragovernmental_diff)}")
    print(f"  Total Public Debt Outstanding: {format_currency(total_debt_diff)}")
    print(f"  {sep_double}")
    print("\n")


def main():
    # Fetch the most recent two posts
    entries = fetch_debt_data("https://treasurydirect.gov/NP_WS/debt/feeds/recent")
    
    display_debt_clock(entries)
    display_math(entries)


if __name__ == "__main__":
    main()
    