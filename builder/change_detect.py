from __future__ import annotations

from hashlib import md5
from time import sleep
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Callable

    from builder.models import Config


class ChangeDetect:
    config: Config
    files: dict[Path, bytes]
    change_set: set[Path] = set()
    callback: Callable
    run: bool = True

    suffixes: ClassVar[set[str]] = {".html", ".j2", ".css", ".js", ".jpg", ".png", ".ico", ".svg"}

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
                self._handle_callback()

            sleep(1)

    def _handle_callback(self) -> None:
        try:
            self.callback()
        except Exception as e:
            print("Caught exception during callback:", end=" ")
            print(e)

    def _find(self) -> None:
        self.change_set = set()
        for path in self.config.change_searchpath:
            for filepath in path.rglob("**/*"):
                self._detect(filepath)

    def _detect(self, filepath: Path) -> None:
        if not filepath.suffix in self.suffixes:
            return None

        last: bytes | None = self.files.get(filepath)
        current: bytes | None = self._checksum(filepath)

        if (last and current != last) or (filepath not in self.files):
            self.change_set.add(filepath)

        if current:
            self.files[filepath] = current

    @staticmethod
    def _checksum(path: Path) -> bytes | None:
        if not path.exists():
            return None

        hash = md5(
            data=path.read_bytes(),
            usedforsecurity=False,
        )
        return hash.digest()
