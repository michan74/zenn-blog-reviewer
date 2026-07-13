from dataclasses import dataclass, field


@dataclass
class User:
    username: str
    name: str


@dataclass
class Article:
    slug: str
    title: str
    published_at: str
    tags: list[str]
    liked_count: int
    publication_name: str | None
    emoji: str
    article_type: str = "tech"
