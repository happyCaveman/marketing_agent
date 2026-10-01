import os
from pathlib import Path

from flask import (
    Flask,
    abort,
    send_file,
)

from marketing_agent.config.settings import (
    PROJECT_ROOT,
)


app = Flask(__name__)


TEMP_DIR = (
    PROJECT_ROOT
    / "data"
    / "temp"
).resolve()


@app.get(
    "/media/<request_id>/<filename>"
)
def get_media(
    request_id: str,
    filename: str,
):
    file_path = (
        TEMP_DIR
        / request_id
        / "images"
        / filename
    ).resolve()

    request_dir = (
        TEMP_DIR
        / request_id
        / "images"
    ).resolve()

    if request_dir not in file_path.parents:
        abort(403)

    if not file_path.exists():
        abort(404)

    if not file_path.is_file():
        abort(404)

    return send_file(
        file_path
    )


def main() -> None:
    port = int(
        os.getenv(
            "PORT",
            "8080",
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
    )


if __name__ == "__main__":
    main()