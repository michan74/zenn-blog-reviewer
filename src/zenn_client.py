import time

import requests

from .models import Article, User

TIMEOUT = 15  # seconds


class ZennClient:
    BASE_URL = "https://zenn.dev"

    def _get(self, url: str, **kwargs) -> requests.Response:
        try:
            return requests.get(url, timeout=TIMEOUT, **kwargs)
        except requests.ConnectionError:
            raise ConnectionError("Zenn に接続できませんでした。ネットワーク接続を確認してください。")
        except requests.Timeout:
            raise TimeoutError("リクエストがタイムアウトしました。しばらく待ってから再試行してください。")

    def get_user(self, username: str) -> User:
        url = f"{self.BASE_URL}/api/users/{username}"
        response = self._get(url)
        if response.status_code == 404:
            raise ValueError(f"ユーザー '{username}' が見つかりません。ユーザー名を確認してください。")
        if response.status_code == 429:
            raise RuntimeError("リクエストが多すぎます。しばらく待ってから再試行してください。")
        response.raise_for_status()
        data = response.json()
        return User(username=data["user"]["username"], name=data["user"]["name"])

    def get_all_articles(self, username: str) -> list[Article]:
        articles = []
        page = 1
        while True:
            url = f"{self.BASE_URL}/api/articles"
            response = self._get(url, params={"username": username, "order": "latest", "page": page})
            if response.status_code == 429:
                raise RuntimeError("リクエストが多すぎます。しばらく待ってから再試行してください。")
            response.raise_for_status()
            data = response.json()
            items = data.get("articles", [])
            if not items:
                break
            for item in items:
                tags = [t["name"] for t in item.get("topics", [])]
                articles.append(Article(
                    slug=item["slug"],
                    title=item["title"],
                    published_at=item.get("published_at", ""),
                    tags=tags,
                ))
            page += 1
        return articles

    def get_article_html(self, username: str, slug: str) -> str:
        time.sleep(0.5)
        url = f"{self.BASE_URL}/{username}/articles/{slug}"
        response = self._get(url)
        response.raise_for_status()
        return response.text
