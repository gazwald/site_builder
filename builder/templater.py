from __future__ import annotations

from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, select_autoescape

from builder.constants import TEMPLATE_PATH

if TYPE_CHECKING:
    from pathlib import Path

    from jinja2.environment import Template


class Templater:
    templates_dir: Path

    def __init__(self, templates_dir: Path = TEMPLATE_PATH) -> None:
        self.templates_dir = templates_dir
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
