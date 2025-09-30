from __future__ import annotations

from typing import TYPE_CHECKING

from builder.models import Article
from builder.templater import Templater

if TYPE_CHECKING:
    from builder.models import Config


class SiteBuilder:
    config: Config
    templater: Templater

    def __init__(self, config: Config) -> None:
        self.templater = Templater(config)
        self.config = config

    def _index(self, recent_articles: list[dict[str, str]]) -> str:
        return self.templater.render(
            "index.html.j2",
            **{
                **self.config.site_config,
                **{"recent_articles": recent_articles},
            },
        )

    def _render_article(self, article: Article) -> Article:
        article.content = self.templater.render(
            "article.html.j2",
            **{
                **self.config.site_config,
                **article.params,
            },
        )
        return article

    def _load_articles(self) -> list[Article]:
        return [Article(path) for path in self.config.article_path.glob("published/*.md")]

    def _recent_articles(self, articles: list[Article]) -> list[dict[str, str]]:
        return [article.for_index for article in sorted(articles, key=lambda a: a.created)][:3]

    def build(self):
        print("Building...", end=" ")
        if not self.config.html_path.is_dir():
            self.config.html_path.mkdir(parents=True)

        articles = [self._render_article(article) for article in self._load_articles()]
        index = self._index(self._recent_articles(articles))
        self._write(index, "index.html")
        for article in articles:
            self._write_article(article)

        print("done.")

    def _write_article(self, article: Article) -> None:
        self._write(article.content, f"{article.slug}.html")

    def _write(self, content: str, filename: str) -> None:
        (self.config.html_path / filename).write_text(content)
