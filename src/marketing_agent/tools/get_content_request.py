import argparse
import json

from marketing_agent.services.content_request_service import (
    ContentRequestService,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--request-id",
        required=True,
        type=str,
    )

    args = parser.parse_args()

    service = ContentRequestService()

    request = service.get_request(
        request_id=args.request_id
    )

    print(
        json.dumps(
            request.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()