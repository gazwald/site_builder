from __future__ import annotations

from pathlib import PosixPath
from typing import TYPE_CHECKING

from builder.models import Article
from builder.templater import Templater

if TYPE_CHECKING:
    from pathlib import Path

    from builder.models import Config


class SiteBuilder:
    config: Config
    templater: Templater

    def __init__(self, config: Config) -> None:
        self.templater = Templater(config)
        self.config = config

    def _index(self, recent_articles: list[dict[str, str]] | None = None) -> str:
        render_kwargs = {
            **self.config.site_config,
            **{"recent_articles": recent_articles if recent_articles else []},
        }
        return self.templater.render(
            "index.html.j2",
            **render_kwargs,
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

    def build(self, files: set[Path] | None = None):
        if not self.config.html_path.is_dir():
            self.config.html_path.mkdir(parents=True)

        if files is None or len(files) == 0:
            self._build_all()
        else:
            self._build_updated(files)

    def _build_index(self, articles: list[Article] | None = None):
        if articles:
            index = self._index(self._recent_articles(articles))
        else:
            index = self._index()
        self._write(index, "index.html")

    def _build_articles(self) -> list[Article]:
        articles = [self._render_article(article) for article in self._load_articles()]
        for article in articles:
            self._write_article(article)
        return articles

    def _build_all(self):
        print("Building...", end=" ")

        if self.config.include_articles:
            articles = self._build_articles()
            self._build_index(articles)
        else:
            self._build_index()

        print("done.")

    def _build_updated(self, files: set[Path]):
        for file in files:
            match file.suffix:
                case ".j2":
                    self._build_index()
                case ".md":
                    if file.is_relative_to(self.config.article_path / "published"):
                        self._build_articles()

    def _write_article(self, article: Article) -> None:
        self._write(article.content, f"{article.slug}.html")

    def _write(self, content: str, filename: str) -> None:
        (self.config.html_path / filename).write_text(content)
