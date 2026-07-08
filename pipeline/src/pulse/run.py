"""Pipeline entry point.

  python -m pulse.run              -> daily pull (last 2 days of postings)
  python -m pulse.run --backfill   -> one-time 30-day backfill
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from .adzuna import fetch_all
from .config import settings
from .db import apply_schema, connect, seed_skills, upsert_jobs
from .extract import extract_skills

SCHEMA = Path(__file__).resolve().parents[2] / "schema.sql"


def main() -> None:
    settings.check()
    backfill = "--backfill" in sys.argv
    max_days_old = 30 if backfill else 2

    print(f"Sydney Tech Pulse — {'backfill (30d)' if backfill else 'daily pull (2d)'}")
    jobs = fetch_all(max_days_old)
    print(f"Fetched {len(jobs)} unique postings")

    skills_by_id = {
        j["adzuna_id"]: extract_skills(f"{j['title']} {j['description']}")
        for j in jobs
    }

    conn = connect()
    try:
        apply_schema(conn, SCHEMA.read_text(encoding="utf-8"))
        seed_skills(conn)
        inserted, updated = upsert_jobs(conn, jobs, skills_by_id)
    finally:
        conn.close()

    top = Counter(s for sk in skills_by_id.values() for s in sk).most_common(8)
    print(f"DONE — {inserted} new, {updated} already known")
    print("Top skills in this batch:", ", ".join(f"{s}({n})" for s, n in top))


if __name__ == "__main__":
    main()
