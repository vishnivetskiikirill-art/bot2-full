import os
from dataclasses import dataclass


def _get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    SESSION_SECRET: str
    WEBAPP_URL: str | None = None


DATABASE_URL = _get_env("DATABASE_URL") or _get_env("POSTGRES_URL") or _get_env("DATABASE_PRIVATE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in Railway Variables")

settings = Settings(
    DATABASE_URL=DATABASE_URL,
    SESSION_SECRET=_get_env("SESSION_SECRET", "change-me"),
    WEBAPP_URL=_get_env("WEBAPP_URL"),
)
