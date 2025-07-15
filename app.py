from dataclasses import asdict, dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Template

TEMPLATE_PATH: Path = Path("templates")
HTML_PATH: Path = Path("output")


@dataclass
class Config:
    title: str = "Gazwald"
    copyright_year: str = "2025"


class Templater:
    templates_dir: Path = Path("templates")

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

    def index(self) -> str:
        return self.templater.render("index.html.j2", **asdict(self.config))


def _write(content: str, filename: str):
    if not HTML_PATH.is_dir():
        HTML_PATH.mkdir(parents=True)

    (HTML_PATH / filename).write_text(content)


def main():
    config = Config()
    sb = SiteBuilder(config)
    index = sb.index()
    print(index)
    _write(index, "index.html")


if __name__ == "__main__":
    main()
