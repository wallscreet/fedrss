from dataclasses import dataclass


@dataclass
class Feed:
    """
    Base class for all feeds.
    """
    name: str
    content_type: str
    base_url: str
    site: str
    max: int = 5
    description: str = ""

    def __post_init__(self):
        self.url = f"{self.base_url}Site={self.site}&ContentType={self.content_type}&Max={self.max}"


@dataclass
class RSS_DOD:
    """
    RSS feed for the United States Department of Defense (DOD).
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

    
    
