import { createClient } from "@supabase/supabase-js";

// All dashboard data comes from the 5 read-only analytics views.
// Missing env vars (e.g. a cold clone) degrade to empty datasets so the
// page renders its "pipeline warming up" states instead of crashing.

export interface TopSkill {
  slug: string;
  display: string;
  family: string;
  mentions: number;
  share: number;
}
export interface WeeklyCount {
  week: string;
  slug: string;
  display: string;
  mentions: number;
  share: number;
}
export interface SkillSalary {
  slug: string;
  display: string;
  family: string;
  sample_size: number;
  median_salary_min: number;
  median_salary_max: number;
}
export interface Mover {
  slug: string;
  display: string;
  share_now: number;
  share_prior_4w: number;
  delta: number;
}
export interface WeeklyVolume {
  week: string;
  postings: number;
}

function client() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  return createClient(url, key);
}

interface ViewOpts {
  orderBy: string;
  ascending?: boolean;
  limit?: number;
}

async function view<T>(name: string, opts: ViewOpts): Promise<T[]> {
  const sb = client();
  if (!sb) return [];
  let q = sb
    .from(name)
    .select("*")
    .order(opts.orderBy, { ascending: opts.ascending ?? true });
  if (opts.limit) q = q.limit(opts.limit);
  const { data, error } = await q;
  if (error) {
    console.error(`view ${name}:`, error.message);
    return [];
  }
  return (data ?? []) as T[];
}

export const getTopSkills = () =>
  view<TopSkill>("v_top_skills_30d", { orderBy: "mentions", ascending: false, limit: 60 });

export const getWeeklyCounts = () =>
  view<WeeklyCount>("v_skill_counts_weekly", { orderBy: "week" });

export const getSalaries = () =>
  view<SkillSalary>("v_skill_salary", { orderBy: "sample_size", ascending: false, limit: 15 });

export const getMovers = () =>
  view<Mover>("v_skill_movers", { orderBy: "delta", ascending: false });

export const getVolume = () =>
  view<WeeklyVolume>("v_weekly_volume", { orderBy: "week" });

/** Drop the current (partial) ISO week so trend lines never nosedive at the end. */
export function dropPartialWeek<T extends { week: string }>(rows: T[]): T[] {
  const monday = new Date();
  const day = monday.getDay() || 7;
  monday.setDate(monday.getDate() - day + 1);
  const cutoff = monday.toISOString().slice(0, 10);
  return rows.filter((r) => r.week < cutoff);
}
