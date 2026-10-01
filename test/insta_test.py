import httpx

from marketing_agent.config.settings import settings


def main() -> None:
    url = "https://graph.instagram.com/me"

    response = httpx.get(
        url,
        params={
            "fields": "id,username",
            "access_token": settings.instagram_access_token,
        },
        timeout=30.0,
    )

    print("status:", response.status_code)
    print("body:", response.text)

    response.raise_for_status()


if __name__ == "__main__":
    main()