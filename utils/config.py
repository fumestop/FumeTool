from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Local development reads from a gitignored .env at the repo root. In
# production the environment is populated by Doppler and no .env exists, so
# load_dotenv is a harmless no-op.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class Config:
    @staticmethod
    def _get_from_env(name: str) -> str:
        try:
            return os.environ[name]
        except KeyError:
            raise RuntimeError(
                f"Missing required config {name!r} "
                "(set it in .env for local development, or Doppler in production)"
            ) from None

    TOKEN: str = _get_from_env("TOKEN")

    EMBED_COLOR: int = int(_get_from_env("EMBED_COLOR"), 0)

    WEBHOOK_ID: int = int(_get_from_env("WEBHOOK_ID"))
    WEBHOOK_TOKEN: str = _get_from_env("WEBHOOK_TOKEN")

    IPC_SECRET_KEY: str = _get_from_env("IPC_SECRET_KEY")
    IPC_STANDARD_PORT: int = int(_get_from_env("IPC_STANDARD_PORT"))
    IPC_MULTICAST_PORT: int = int(_get_from_env("IPC_MULTICAST_PORT"))

    COMMUNITY_GUILD_ID: int = int(_get_from_env("COMMUNITY_GUILD_ID"))

    DB_HOST: str = _get_from_env("DB_HOST")
    DB_PORT: int = int(_get_from_env("DB_PORT"))
    DB_NAME: str = _get_from_env("DB_NAME")
    DB_USER: str = _get_from_env("DB_USER")
    DB_PASSWORD: str = _get_from_env("DB_PASSWORD")

    STEAM_API_KEY: str = _get_from_env("STEAM_API_KEY")
    WEATHER_API_KEY: str = _get_from_env("WEATHER_API_KEY")
    TOPGG_TOKEN: str = _get_from_env("TOPGG_TOKEN")

    INITIAL_EXTENSIONS: list[str] = [
        item.strip()
        for item in _get_from_env("INITIAL_EXTENSIONS").split(",")
        if item.strip()
    ]
