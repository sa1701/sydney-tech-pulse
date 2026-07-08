"""Postgres load step — idempotent upserts via psycopg3.

Descriptions are never stored: we extract skills in-flight and persist only
structured facts. Keeps the DB lean and sidesteps republishing scraped text.
"""
from __future__ import annotations

import psycopg

from .config import settings
from .taxonomy import seed_rows

UPSERT_JOB = """
insert into jobs (adzuna_id, title, company, created, salary_min, salary_max,
                  salary_predicted, category, search_role, url)
values (%(adzuna_id)s, %(title)s, %(company)s, %(created)s, %(salary_min)s,
        %(salary_max)s, %(salary_predicted)s, %(category)s, %(search_role)s, %(url)s)
on conflict (adzuna_id) do update set last_seen = now()
returning (xmax = 0) as inserted
"""


def connect() -> psycopg.Connection:
    return psycopg.connect(settings.database_url)


def apply_schema(conn: psycopg.Connection, schema_sql: str) -> None:
    conn.execute(schema_sql)
    conn.commit()


def seed_skills(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.executemany(
            """insert into skills (slug, display, family) values (%s, %s, %s)
               on conflict (slug) do update
               set display = excluded.display, family = excluded.family""",
            seed_rows(),
        )
    conn.commit()


def upsert_jobs(conn: psycopg.Connection,
                jobs: list[dict],
                skills_by_id: dict[str, set[str]]) -> tuple[int, int]:
    """Upsert jobs + their skill links. Returns (inserted, updated)."""
    inserted = updated = 0
    with conn.cursor() as cur:
        for job in jobs:
            row = {k: v for k, v in job.items() if k != "description"}
            cur.execute(UPSERT_JOB, row)
            if cur.fetchone()[0]:
                inserted += 1
            else:
                updated += 1
            links = [(job["adzuna_id"], slug)
                     for slug in sorted(skills_by_id.get(job["adzuna_id"], ()))]
            if links:
                cur.executemany(
                    """insert into job_skills (adzuna_id, skill_slug)
                       values (%s, %s) on conflict do nothing""",
                    links,
                )
    conn.commit()
    return inserted, updated
