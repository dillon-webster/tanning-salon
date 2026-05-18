import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tanning_salon.db")


def get_admin_api_key() -> str | None:
    return os.getenv("ADMIN_API_KEY")
