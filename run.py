from builder import Config, SiteBuilder


def main():
    config = Config()
    sb = SiteBuilder(config)
    sb.build()


if __name__ == "__main__":
    main()
