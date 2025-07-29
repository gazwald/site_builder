from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

import markdown

from builder.constants import ARTICLE_PATH, HTML_PATH, TEMPLATE_PATH

if TYPE_CHECKING:
    from pathlib import Path

    from builder.types import SiteConfig


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
