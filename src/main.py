import argparse

from archive import Archiver
from presets import PRESETS


def main():
    parser = argparse.ArgumentParser(
        description="Archive URLs using the Internet Archive's Save Page Now 2 API"
    )
    parser.add_argument("urls", nargs="*", help="URLs to archive")
    parser.add_argument(
        "-p",
        "--preset",
        action="append",
        choices=list(PRESETS.keys()),
        default=[],
        help="additional URLs to archive via presets (can be specified multiple times)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=10,
        help="maximum retries before giving up (default: 10)",
    )
    parser.add_argument("--debug", action="store_true", help="enable debug output")

    args = parser.parse_args()

    links = list(args.urls)
    for preset_name in args.preset:
        preset_fn = PRESETS[preset_name]
        links.extend(preset_fn())

    if not links:
        parser.error("No URLs provided. Specify URLs directly or use --preset.")

    archiver = Archiver(max_retries=args.max_retries, debug=args.debug)
    success = archiver.archive_all(links)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
