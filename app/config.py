from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    api_token: str
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"
    enable_healthcheck: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        api_token = os.getenv("API_TOKEN", "").strip()
        if not api_token:
            raise RuntimeError("Environment variable API_TOKEN is required")

        return cls(
            api_token=api_token,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8080")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            enable_healthcheck=os.getenv("ENABLE_HEALTHCHECK", "true").lower() in {"1", "true", "yes", "on"},
        )
