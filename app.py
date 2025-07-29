from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import ClassVar, TypedDict

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Template

TEMPLATE_PATH: Path = Path("templates")
HTML_PATH: Path = Path("output")
ARTICLE_PATH: Path = Path("articles")


@dataclass
class Article:
    path: Path
    title: str = field(init=False)
    content: str = field(init=False)
    markdown: str = field(init=False)

    def __post_init__(self) -> None:
        self.markdown = self.path.read_text()
        self.title = self.path.stem.replace("_", " ").title()

    @property
    def created(self) -> str:
        return datetime.fromtimestamp(self.path.stat().st_ctime).date().isoformat()

    @property
    def edited(self) -> str | None:
        mtime: float = self.path.stat().st_mtime
        if mtime < (datetime.now().timestamp() + 3600):
            return None

        return datetime.fromtimestamp(mtime).date().isoformat()

    @property
    def slug(self) -> str:
        return self.path.stem.casefold()

    @property
    def params(self) -> dict[str, str | None]:
        return {
            **self.for_index,
            "article_content": markdown.markdown(self.markdown),
            "article_created": self.created,
            "article_edited": self.edited,
        }

    @property
    def for_index(self) -> dict[str, str]:
        return {
            "article_title": self.title,
            "article_slug": self.slug,
        }


class SiteConfig(TypedDict):
    title: str
    copyright_year: str


@dataclass
class Config:
    title: str = "Gazwald"
    copyright_year: str = "2025"
    template_path: Path = TEMPLATE_PATH
    html_path: Path = HTML_PATH
    article_path: Path = ARTICLE_PATH

    @property
    def site_config(self) -> SiteConfig:
        return {
            "title": self.title,
            "copyright_year": self.copyright_year,
        }


class Templater:
    templates_dir: ClassVar[Path] = TEMPLATE_PATH

    def __init__(self) -> None:
        self.env = self._create_env()

    def _create_env(self) -> Environment:
        return Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(),
        )

    def _get_template(self, filename: str) -> Template:
        return self.env.get_template(filename)

    def render(self, filename: str, **kwargs) -> str:
        return self._get_template(filename).render(**kwargs)


class SiteBuilder:
    config: Config
    templater: Templater

    def __init__(self, config: Config) -> None:
        self.templater = Templater()
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
        if not self.config.html_path.is_dir():
            self.config.html_path.mkdir(parents=True)

        articles = [self._render_article(article) for article in self._load_articles()]
        index = self._index(self._recent_articles(articles))
        self._write(index, "index.html")
        for article in articles:
            self._write_article(article)

    def _write_article(self, article: Article) -> None:
        self._write(article.content, f"{article.slug}.html")

    def _write(self, content: str, filename: str) -> None:
        (self.config.html_path / filename).write_text(content)


def main():
    config = Config()
    sb = SiteBuilder(config)
    sb.build()


if __name__ == "__main__":
    main()
