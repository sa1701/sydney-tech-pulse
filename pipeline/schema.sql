-- Sydney Tech Pulse — Postgres schema
-- Raw SQL by design: the schema and analytics views ARE the data-engineering
-- portfolio artifact. Applied idempotently (safe to re-run).

create table if not exists jobs (
    adzuna_id        text primary key,
    title            text not null,
    company          text,
    created          timestamptz not null,          -- posting date from Adzuna
    salary_min       numeric,
    salary_max       numeric,
    salary_predicted boolean not null default false, -- Adzuna's ML guess, not employer-stated
    category         text,
    search_role      text not null,                  -- which query surfaced it first
    url              text,
    first_seen       timestamptz not null default now(),
    last_seen        timestamptz not null default now()
);

create index if not exists idx_jobs_created on jobs (created);

create table if not exists skills (
    slug    text primary key,
    display text not null,
    family  text not null check (family in
            ('language','frontend','backend','data','cloud','devops','ai','practice'))
);

create table if not exists job_skills (
    adzuna_id  text not null references jobs (adzuna_id) on delete cascade,
    skill_slug text not null references skills (slug) on delete cascade,
    primary key (adzuna_id, skill_slug)
);

create index if not exists idx_job_skills_skill on job_skills (skill_slug);

-- ---------------------------------------------------------------------------
-- Row-level security: the dashboard's anon role may only ever read.
-- The pipeline connects as the table owner, which RLS does not restrict.
-- ---------------------------------------------------------------------------

alter table jobs        enable row level security;
alter table skills      enable row level security;
alter table job_skills  enable row level security;

do $$ begin
    create policy anon_read_jobs       on jobs       for select using (true);
    exception when duplicate_object then null;
end $$;
do $$ begin
    create policy anon_read_skills     on skills     for select using (true);
    exception when duplicate_object then null;
end $$;
do $$ begin
    create policy anon_read_job_skills on job_skills for select using (true);
    exception when duplicate_object then null;
end $$;

-- ---------------------------------------------------------------------------
-- Analytics views — the dashboard reads ONLY these.
-- ---------------------------------------------------------------------------

-- Postings per ISO week (pipeline health + market volume).
create or replace view v_weekly_volume as
select date_trunc('week', created)::date as week,
       count(*)                          as postings
from jobs
group by 1
order by 1;

-- Skill demand per week, with share of that week's postings.
create or replace view v_skill_counts_weekly as
select date_trunc('week', j.created)::date as week,
       s.slug,
       s.display,
       s.family,
       count(*)                            as mentions,
       round(count(*)::numeric
             / nullif(max(w.postings), 0), 4) as share
from job_skills js
join jobs   j on j.adzuna_id = js.adzuna_id
join skills s on s.slug = js.skill_slug
join v_weekly_volume w on w.week = date_trunc('week', j.created)::date
group by 1, 2, 3, 4
order by 1, mentions desc;

-- Top skills over the trailing 30 days.
create or replace view v_top_skills_30d as
select s.slug,
       s.display,
       s.family,
       count(*) as mentions,
       round(count(*)::numeric
             / nullif((select count(*) from jobs
                       where created >= now() - interval '30 days'), 0), 4) as share
from job_skills js
join jobs   j on j.adzuna_id = js.adzuna_id
join skills s on s.slug = js.skill_slug
where j.created >= now() - interval '30 days'
group by 1, 2, 3
order by mentions desc;

-- Median employer-stated salary band per skill (predicted salaries excluded).
create or replace view v_skill_salary as
select s.slug,
       s.display,
       s.family,
       count(*) as sample_size,
       percentile_cont(0.5) within group (order by j.salary_min) as median_salary_min,
       percentile_cont(0.5) within group (order by j.salary_max) as median_salary_max
from job_skills js
join jobs   j on j.adzuna_id = js.adzuna_id
join skills s on s.slug = js.skill_slug
where j.salary_min is not null
  and not j.salary_predicted
group by 1, 2, 3
having count(*) >= 3              -- suppress noisy tiny samples (n shown in UI)
order by median_salary_max desc;

-- Momentum: this week's share vs the prior 4-week average share.
create or replace view v_skill_movers as
with weekly as (select * from v_skill_counts_weekly),
     latest as (select max(week) as week from weekly)
select w.slug,
       w.display,
       w.family,
       w.share                          as share_now,
       avg(p.share)                     as share_prior_4w,
       round(w.share - avg(p.share), 4) as delta
from weekly w
join latest l on w.week = l.week
join weekly p on p.slug = w.slug
            and p.week <  l.week
            and p.week >= l.week - interval '28 days'
group by w.slug, w.display, w.family, w.share
having count(p.week) >= 2             -- need some history to call it a trend
order by delta desc;
