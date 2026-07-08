"""Adzuna API client — the extract step of the pipeline.

Free tier: 25 requests/min, 250/day. A full backfill (6 roles x 8 pages) is
48 calls; the daily run is typically 6-12. The request_gap sleep keeps us
politely under the per-minute cap.
"""
from __future__ import annotations

import time
from typing import Iterator

import httpx

from .config import settings

BASE = "https://api.adzuna.com/v1/api/jobs"


def _normalise(raw: dict, search_role: str) -> dict:
    """Flatten one Adzuna result into our jobs-table shape."""
    return {
        "adzuna_id": str(raw["id"]),
        "title": (raw.get("title") or "").strip(),
        "company": ((raw.get("company") or {}).get("display_name") or "").strip() or None,
        "created": raw["created"],
        "salary_min": raw.get("salary_min"),
        "salary_max": raw.get("salary_max"),
        "salary_predicted": str(raw.get("salary_is_predicted", "0")) == "1",
        "category": ((raw.get("category") or {}).get("label") or None),
        "search_role": search_role,
        "url": raw.get("redirect_url"),
        # description only feeds skill extraction; it is NOT stored (see run.py)
        "description": raw.get("description") or "",
    }


def fetch_role(client: httpx.Client, role: str, max_days_old: int,
               max_pages: int) -> Iterator[dict]:
    """Yield normalised postings for one role query, newest first."""
    for page in range(1, max_pages + 1):
        resp = client.get(
            f"{BASE}/{settings.country}/search/{page}",
            params={
                "app_id": settings.adzuna_app_id,
                "app_key": settings.adzuna_app_key,
                "what": role,
                "where": settings.where,
                "results_per_page": settings.results_per_page,
                "max_days_old": max_days_old,
                "sort_by": "date",
            },
            timeout=30,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        for raw in results:
            yield _normalise(raw, role)
        if len(results) < settings.results_per_page:
            break  # last page for this role
        time.sleep(settings.request_gap_seconds)


def fetch_all(max_days_old: int) -> list[dict]:
    """Fetch every configured role and dedupe across roles by adzuna_id."""
    seen: dict[str, dict] = {}
    with httpx.Client() as client:
        for role in settings.search_roles:
            n_before = len(seen)
            for job in fetch_role(client, role, max_days_old,
                                  settings.max_pages_per_role):
                seen.setdefault(job["adzuna_id"], job)
            print(f"  [{role}] +{len(seen) - n_before} new "
                  f"({len(seen)} total)", flush=True)
            time.sleep(settings.request_gap_seconds)
    return list(seen.values())
