from threading import Thread

from builder import Config, SiteBuilder
from builder.change_detect import ChangeDetect
from builder.dev_server import run_httpd


def site():
    config = Config()
    sb = SiteBuilder(config)
    if config.watch:
        ChangeDetect(config, sb.build)
    else:
        sb.build()


def main():
    threads = [
        Thread(target=site),
        Thread(target=run_httpd, daemon=True),
    ]
    for thread in threads:
        thread.start()


if __name__ == "__main__":
    main()
