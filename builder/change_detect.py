from __future__ import annotations

from hashlib import md5
from time import sleep
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

    from builder.models import Config


class Callback(Protocol):
    def __call__(self, files: set[Path] | None = None) -> None: ...


class ChangeDetect:
    config: Config
    files: dict[Path, bytes]
    change_set: set[Path]
    run: bool = True
    first_run: bool = True

    suffixes: ClassVar[set[str]] = {
        ".html",
        ".j2",
        ".css",
        ".js",
        ".jpg",
        ".png",
        ".ico",
        ".svg",
    }

    def __init__(self, config: Config, callback: Callback) -> None:
        self.config = config
        self.callback = callback
        self.files = {}
        self.start()

    def start(self):
        try:
            self._run()
        except KeyboardInterrupt:
            self.run = False
            print("Caught KeyboardInterrupt, stopping")

    def _run(self) -> None:
        print(f"Looking for changes in {', '.join(map(str, self.config.change_searchpath))}")
        while self.run:
            self.changes = self._find()
            if self.change_set:
                self._handle_callback()

            sleep(1)

    def _handle_callback(self) -> None:
        if not self.first_run:
            for changed_file in self.change_set:
                print(f"Detected change in {changed_file}")

        try:
            if self.first_run:
                self.callback()
                self.first_run = False
            else:
                self.callback(self.change_set)
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
