from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Callable

    from builder.models import Config


class ChangeDetect:
    config: Config
    files: dict[Path, float]
    change_set: set[Path] = set()
    pattern: str = "**/*.html.j2"
    callback: Callable
    run: bool = True

    def __init__(self, config: Config, callback: Callable) -> None:
        self.config = config
        self.callback = callback
        print(f"Monitoring {self.config.jinja_searchpath}")
        self.files = {}
        try:
            self._run()
        except KeyboardInterrupt:
            self.run = False
            print("Caught KeyboardInterrupt, stopping")

    def _run(self) -> None:
        print(f"Looking for changes in {self.config.jinja_searchpath}")
        while self.run:
            self.changes = self._find()
            if self.change_set:
                for changed_file in self.change_set:
                    print(f"Detected change in {changed_file}")
                self.callback()

            sleep(1)

    def _find(self) -> None:
        self.change_set = set()
        for path in self.config.jinja_searchpath:
            for file in path.rglob(self.pattern):
                last: float | None = self.files.get(file)
                current: float = file.stat().st_mtime
                if last and current != last:
                    self.change_set.add(file)

                self.files[file] = current
