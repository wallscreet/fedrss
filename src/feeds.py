from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Feed:
    """
    Base class for all feeds.
    """
    name: str
    base_url: str
    description: str = ""
    content_type: Optional[str] = None
    site: Optional[str] = None
    max: Optional[int] = 10

    def __post_init__(self):
        self.url = f"{self.base_url}Site={self.site}&ContentType={self.content_type}&Max={self.max}"


@dataclass
class RSS_DOD:
    """
    RSS feed for the United States Department of Defense (DOD).

    :return: XML feed with the latest published releases from the DOD.
    """
    feeds: list[Feed] = None

    def __post_init__(self):
        self.feeds = [
            Feed(
                name="Feature Stories",
                content_type="800",
                base_url= "https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?",
                site="945",
                max=10,
                description="Feature stories from the Department of Defense."
            ),
            Feed(
                name="News",
                content_type="1",
                base_url="https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?",
                site="945",
                max=10,
                description="News from the Department of Defense."
            ),
            Feed(
                name="Releases",
                content_type="9",
                base_url="https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?",
                site="945",
                max=10,
                description="Press releases from the Department of Defense."
            ),
            Feed(
                name="Contract Announcements",
                content_type="400",
                base_url="https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?",
                site="945",
                max=10,
                description="U.S. Department of Defense Contracts valued at $7.5 million or more are announced each business day at 5 p.m."
            ),
            Feed(
                name="Advisories",
                content_type="500",
                base_url="https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?",
                site="945",
                max=10,
                description="Advisories from the Department of Defense."
            )
        ]

    
@dataclass
class GovInfo_RSS:
    """
    RSS feed for the U.S. Government Publishing Office (GPO) and the Government Publishing Office (GPO).

    :return: XML feed with the latest news and publications from the GPO.
    """
    feeds: list[Feed] = None

    def __post_init__(self):
        self.feeds = [
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
        ]


@dataclass
class TreasuryDirect_RSS:
    """
    RSS feed for the U.S. Department of the Treasury's Bureau of the Fiscal Service.

    :return: XML feed with the latest news and publications from TreasuryDirect.
    """
    feeds: list[Feed] = None

    def __post_init__(self):
        self.feeds = [
            Feed(
                name="Debt To The Penny",
                base_url="https://treasurydirect.gov/NP_WS/debt/feeds/recent",
                description="The most recent Debt to the Penny reported values."
            ),
        ]
