"""One-off: apply schema (incl. RLS) to the DATABASE_URL target and report."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "src")

from pulse.db import apply_schema, connect  # noqa: E402

conn = connect()
apply_schema(conn, (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8"))
n = conn.execute("select count(*) from jobs").fetchone()[0]
rls = conn.execute(
    "select relname, relrowsecurity from pg_class "
    "where relname in ('jobs','skills','job_skills') order by 1"
).fetchall()
top = conn.execute("select display, mentions from v_top_skills_30d limit 5").fetchall()
conn.close()
print("jobs:", n)
print("RLS enabled:", rls)
print("top skills view:", top)
