import unicodedata

from bs4 import BeautifulSoup

from .models import ArticleContent


def _is_emoji(char: str) -> bool:
    category = unicodedata.category(char)
    codepoint = ord(char)
    return category == "So" or (0x1F000 <= codepoint <= 0x1FFFF) or (0x2600 <= codepoint <= 0x27FF)


class ContentParser:
    def parse(self, html: str, slug: str, title: str) -> ArticleContent:
        soup = BeautifulSoup(html, "html.parser")

        article = soup.find("article")
        target = article if article else soup

        for tag in target.find_all(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        text = target.get_text(separator="\n")

        emojis = [char for char in text if _is_emoji(char)]

        return ArticleContent(slug=slug, title=title, text=text, emojis=emojis)
