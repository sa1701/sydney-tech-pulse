# BUILD HANDOFF — Sydney Tech Pulse

> For the next Claude session (any model). Written 2026-07-09 at the end of the
> Fable 5 window. The design is locked; execute, don't re-derive. The approved
> plan lives at `~/.claude/plans/what-are-some-good-wobbly-conway.md`.
> Delete this file before the repo goes public (final step).

## What this is
Job-market data pipeline + live dashboard: "Which skills are Sydney tech
employers hiring for right now?" Fills the data-engineering gap in Seif's
AI & Big Data portfolio. 1–2 day sprint scope.

## State right now (all ✅ verified)
- Pipeline code complete under `pipeline/`: Adzuna client → taxonomy regex
  extraction → psycopg3 idempotent upserts. `schema.sql` has tables + 5
  analytics views (dashboard reads ONLY views).
- 13/13 extractor unit tests pass locally (`pytest tests/test_extract.py`).
  DB tests skip without DATABASE_URL, run in CI via Postgres service.
- Workflows written: `ci.yml` (tests + service container), `pipeline.yml`
  (daily cron 21:00 UTC = 07:00 Sydney + manual dispatch w/ backfill input).
- Docker Desktop was installed via winget (exit 0) but NOT yet launched —
  first run needs WSL2 init and possibly a reboot.
- NOT yet done: first commit/push, GitHub repo creation, secrets, backfill,
  the entire `web/` dashboard, README, portfolio/CV wiring, memory file.

## Blockers needing Seif (ask him first thing)
1. **Adzuna keys** — register free at developer.adzuna.com → APP_ID + APP_KEY.
2. **Supabase project** — new project "tech-pulse" → the *pooler* connection
   string (port 6543, or 5432 session mode for the pipeline) + project URL +
   anon key for the web app.

## Execution order
1. `git add -A && git commit` (NO Claude trailers — hard rule, see memory
   `feedback_no_claude_coauthor.md`), `gh repo create sa1701/sydney-tech-pulse
   --public --source=. --push`.
2. `gh secret set ADZUNA_APP_ID / ADZUNA_APP_KEY / DATABASE_URL` once Seif
   pastes values. Verify CI goes green on GitHub (that's the badge).
3. Local smoke test: `docker compose up -d db` → `$env:DATABASE_URL =
   "postgresql://pulse:pulse@localhost:5433/pulse"` → `python -m pulse.run
   --backfill` from `pipeline/` (PYTHONPATH=src or `pip install -e .`).
   Expect a few thousand rows. Re-run daily mode → assert 0 new inserts crash.
4. Prod backfill: `gh workflow run pipeline.yml -f backfill=true`, check the
   Actions log summary line, then sanity-check per plan §Verification
   (top-10 skills should look like Python/AWS/React/SQL...).
5. Build `web/` dashboard (spec below), deploy to Vercel, verify with
   Playwright screenshots at 1440px and 390px.
6. README (badges: CI + live link; architecture diagram from the plan; honest
   limitations: truncated descriptions, Adzuna ≠ whole market, predicted
   salaries excluded). Portfolio card in `portfolio/components/Projects.tsx`
   (pattern: existing PROJECTS array; put it after GEARHEAD, github +
   liveUrl fields). CV bullets in `career-ops/cv.md` — concise, honest;
   regenerate PDF only if Seif confirms. New memory file
   `project_sydney_tech_pulse.md` + MEMORY.md line.
7. Delete HANDOFF.md, final commit.

## Dashboard spec (web/) — follow this closely, it carries the design intent
- Next.js 14 App Router + Tailwind + recharts; `@supabase/supabase-js` with
  anon key; server components fetch from the 5 views only. ISR
  (`revalidate = 3600`) so the page is static-fast but fresh daily.
- **Identity**: dark terminal-meets-Bloomberg. bg `#0b0e11`, panel `#12161b`,
  line `#232a33`, ink `#e6ebf0`, accent **signal green `#3ddc84`** (data going
  up), secondary amber `#ffb01f` only for "mover" deltas. JetBrains Mono for
  every number and axis label; Inter (or system) for prose. No gradients, no
  glassmorphism — hairline borders, generous whitespace, chart-first.
- **Layout, top to bottom**:
  1. Header: `SYDNEY TECH PULSE` wordmark + live badge "UPDATED DAILY · 07:00
     AEST" + GitHub link.
  2. Hero stat row (4 cards): live postings (30d), postings this week, #1
     skill, biggest mover ↑ (from v_skill_movers, show +Δpp).
  3. **Top skills now** — horizontal bars (v_top_skills_30d, top 20), family
     filter pills (All/Languages/Data/Cloud/AI/...), % share labels.
  4. **Six-week trends** — line chart (v_skill_counts_weekly share), default
     series: python, typescript, aws, react, machine-learning; clickable
     legend to toggle any taxonomy skill. Drop the current partial week.
  5. **Salary by skill** — v_skill_salary top 15 by sample_size: dumbbell/bar
     from median_min→median_max, k-format labels, footnote "employer-stated
     salaries only (n≥5); Adzuna-predicted excluded".
  6. Methodology footer: source, cadence, taxonomy repo link, the caveats.
- Charts must be readable at 390px (stack cards, horizontal-scroll the
  trends chart if needed). `prefers-reduced-motion` respected (recharts
  `isAnimationActive={false}` when set).
- Empty-DB state: every section renders a "pipeline warming up" skeleton
  rather than crashing (views return 0 rows until backfill).

## Environment gotchas (learned this session, will bite you)
- PowerShell 5.1: no `&&`; `Invoke-WebRequest` fails in NonInteractive mode —
  use `curl` via the Bash tool for HTTP checks.
- Git Bash: `bc` doesn't exist (use awk); every Bash call prints a
  `dash | port | pyp` profile banner — ignore it.
- Long/sleepy foreground commands get auto-backgrounded; you'll be notified.
  Background bash tasks CAN outlive the 10-min default (fixdb ran 30 min).
- `gh` CLI is authed as sa1701. Vercel CLI is authed (portfolio deploys work).
- Supabase from GitHub Actions: use the **session pooler** string if direct
  5432 is IPv6-only (Actions runners are IPv4).
- Seif's standing rules: plan mode for non-trivial work, verify before done,
  no Claude commit trailers, no grades on CV, API cost discipline (this
  project is $0 by design — keep it that way).

## Definition of done
CI badge green · cron pipeline ran against Supabase · dashboard live on
Vercel with real backfill data · README complete · portfolio card + CV
bullets in · memory saved · HANDOFF.md deleted.
