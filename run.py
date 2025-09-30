from builder import Config, SiteBuilder
from builder.change_detect import ChangeDetect


def main():
    config = Config()
    sb = SiteBuilder(config)
    if config.watch:
        ChangeDetect(config, sb.build)
    else:
        sb.build()


if __name__ == "__main__":
    main()
