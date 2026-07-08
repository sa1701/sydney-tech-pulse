"""Central config — everything comes from the environment, nothing from code."""
from __future__ import annotations

import os


class Settings:
    adzuna_app_id: str = os.getenv("ADZUNA_APP_ID", "")
    adzuna_app_key: str = os.getenv("ADZUNA_APP_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", "")

    # The role queries that define "Sydney tech market" for this project.
    search_roles: tuple[str, ...] = (
        "software engineer",
        "data engineer",
        "machine learning",
        "data analyst",
        "devops",
        "web developer",
    )
    where: str = "Sydney"
    country: str = "au"
    results_per_page: int = 50          # Adzuna max
    max_pages_per_role: int = 8         # backfill cap; daily runs stop early anyway
    request_gap_seconds: float = 2.5    # stay under 25 req/min

    def check(self) -> None:
        missing = [
            name for name, val in (
                ("ADZUNA_APP_ID", self.adzuna_app_id),
                ("ADZUNA_APP_KEY", self.adzuna_app_key),
                ("DATABASE_URL", self.database_url),
            ) if not val
        ]
        if missing:
            raise RuntimeError(
                f"Missing env vars: {', '.join(missing)} — see README §Setup."
            )


settings = Settings()
