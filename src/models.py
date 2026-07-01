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


@dataclass
class ArticleContent:
    slug: str
    title: str
    text: str
    emojis: list[str]


@dataclass
class AnalysisResult:
    username: str
    article_count: int
    habits: list[tuple[str, int]]           # (フレーズ, 出現回数)
    syntax_patterns: list[tuple[str, int]]  # (パターン名, 出現回数)
    interesting_phrases: list[str]
    fortune: tuple[str, str]                # (絵文字, メッセージ)
    knowledge_map_html: str                 # pyvis が生成した graph HTML
