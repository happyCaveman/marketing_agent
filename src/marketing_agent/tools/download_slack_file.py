import argparse

from marketing_agent.services.slack_media_service import (
    SlackMediaService,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "file_id",
        type=str,
    )

    parser.add_argument(
        "--destination",
        type=str,
        default="data/temp/slack_test",
    )

    args = parser.parse_args()

    service = SlackMediaService()

    path = service.download_file(
        file_id=args.file_id,
        destination_dir=args.destination,
    )



if __name__ == "__main__":
    main()