import time

import httpx

from marketing_agent.config.settings import settings


def main() -> None:
    image_url = (
        # "https://YOUR-RAILWAY-DOMAIN/"
        # "media/YOUR-REQUEST-ID/image.jpg"
        "https://cooperative-clinical-nylon-compatible.trycloudflare.com/media/7c502261-9a85-4646-9641-70e5f8c39a4a/won1.png"
    )

    caption = (
        "Instagram API 자동 게시 테스트입니다.\n\n"
        "#테스트 #자동화"
    )

    create_url = (
        f"https://graph.instagram.com/"
        f"{settings.instagram_account_id}/media"
    )

    create_response = httpx.post(
        create_url,
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": settings.instagram_access_token,
        },
        timeout=30.0,
    )

    print(
        "create:",
        create_response.status_code,
        create_response.text,
    )

    create_response.raise_for_status()

    creation_id = (
        create_response.json()["id"]
    )

    time.sleep(5)

    publish_url = (
        f"https://graph.instagram.com/"
        f"{settings.instagram_account_id}/media_publish"
    )

    publish_response = httpx.post(
        publish_url,
        data={
            "creation_id": creation_id,
            "access_token": settings.instagram_access_token,
        },
        timeout=30.0,
    )

    print(
        "publish:",
        publish_response.status_code,
        publish_response.text,
    )

    publish_response.raise_for_status()


if __name__ == "__main__":
    main()