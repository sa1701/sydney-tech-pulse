"""DB integration tests — run against a real Postgres (docker compose locally,
service container in CI). Skipped automatically when DATABASE_URL is unset."""
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"), reason="needs a Postgres (set DATABASE_URL)"
)

SAMPLE = {
    "adzuna_id": "test-123",
    "title": "Graduate Software Engineer",
    "company": "Acme",
    "created": "2026-07-01T00:00:00Z",
    "salary_min": 80000,
    "salary_max": 95000,
    "salary_predicted": False,
    "category": "IT Jobs",
    "search_role": "software engineer",
    "url": "https://example.com/j/123",
    "description": "Python and AWS, Docker a plus",
}


@pytest.fixture()
def conn():
    from pulse.db import apply_schema, connect, seed_skills

    schema = (Path(__file__).resolve().parents[1] / "schema.sql").read_text(encoding="utf-8")
    c = connect()
    apply_schema(c, schema)
    seed_skills(c)
    c.execute("delete from jobs where adzuna_id like 'test-%'")
    c.commit()
    yield c
    c.execute("delete from jobs where adzuna_id like 'test-%'")
    c.commit()
    c.close()


def test_upsert_is_idempotent(conn):
    from pulse.db import upsert_jobs
    from pulse.extract import extract_skills

    skills = {"test-123": extract_skills(SAMPLE["title"] + " " + SAMPLE["description"])}

    ins1, upd1 = upsert_jobs(conn, [SAMPLE], skills)
    assert (ins1, upd1) == (1, 0)

    ins2, upd2 = upsert_jobs(conn, [SAMPLE], skills)
    assert (ins2, upd2) == (0, 1)

    n = conn.execute(
        "select count(*) from jobs where adzuna_id = 'test-123'"
    ).fetchone()[0]
    assert n == 1

    linked = conn.execute(
        "select skill_slug from job_skills where adzuna_id = 'test-123' order by 1"
    ).fetchall()
    assert [r[0] for r in linked] == ["aws", "docker", "python"]


def test_views_exist(conn):
    for view in ("v_weekly_volume", "v_skill_counts_weekly", "v_top_skills_30d",
                 "v_skill_salary", "v_skill_movers"):
        conn.execute(f"select * from {view} limit 1")  # raises if missing
