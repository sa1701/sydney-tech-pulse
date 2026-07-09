import Salary from "@/components/Salary";
import TopSkills from "@/components/TopSkills";
import Trends from "@/components/Trends";
import {
  dropPartialWeek,
  getMovers,
  getSalaries,
  getTopSkills,
  getVolume,
  getWeeklyCounts,
} from "@/lib/data";

export const revalidate = 3600; // static-fast, fresh within the hour of each daily run

export default async function Home() {
  const [topSkills, weeklyRaw, salaries, movers, volumeRaw] = await Promise.all([
    getTopSkills(),
    getWeeklyCounts(),
    getSalaries(),
    getMovers(),
    getVolume(),
  ]);

  const weekly = dropPartialWeek(weeklyRaw);

  const total30d = topSkills.length
    ? Math.round(topSkills[0].mentions / (topSkills[0].share || 1))
    : 0;
  const thisWeek = volumeRaw.at(-1)?.postings ?? 0;
  const topSkill = topSkills[0];
  const mover = movers.find((m) => m.delta > 0);

  const stats: [string, string, string][] = [
    ["Postings · 30d", total30d ? total30d.toLocaleString() : "—", "unique Sydney tech ads"],
    ["This week", thisWeek ? thisWeek.toLocaleString() : "—", "and counting, updated daily"],
    ["#1 skill", topSkill?.display ?? "—", topSkill ? `in ${(topSkill.share * 100).toFixed(0)}% of postings` : "warming up"],
    ["Rising", mover?.display ?? "—", mover ? `+${(mover.delta * 100).toFixed(1)}pp vs prior 4w` : "needs more history"],
  ];

  return (
    <main className="max-w-5xl mx-auto px-5 py-10 sm:py-14 space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4 pb-2">
        <div>
          <h1 className="mono text-lg tracking-[0.28em] font-semibold">
            SYDNEY&nbsp;TECH&nbsp;<span className="text-[var(--signal)]">PULSE</span>
          </h1>
          <p className="text-sm text-[var(--muted)] mt-1.5 max-w-md">
            What Sydney tech employers are actually hiring for — extracted daily from live job postings.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <span className="spec flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[var(--signal)] inline-block animate-pulse" />
            Updated daily · 07:00 AEST
          </span>
          <a
            href="https://github.com/sa1701/sydney-tech-pulse"
            target="_blank"
            rel="noopener noreferrer"
            className="mono text-xs border border-[var(--line)] rounded-full px-4 py-2 hover:border-[var(--signal)] hover:text-[var(--signal)] transition-colors"
          >
            Source ↗
          </a>
        </div>
      </header>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(([label, value, sub]) => (
          <div key={label} className="panel p-5">
            <div className="spec mb-2">{label}</div>
            <div className="mono text-2xl font-semibold text-[var(--signal)] truncate">{value}</div>
            <div className="text-xs text-[var(--muted)] mt-1.5">{sub}</div>
          </div>
        ))}
      </div>

      <TopSkills skills={topSkills} />
      <Trends weekly={weekly} />
      <Salary salaries={salaries} />

      <footer className="panel p-6 sm:p-8 text-sm text-[var(--muted)] leading-relaxed">
        <div className="spec mb-3">Methodology</div>
        <p>
          Postings are pulled daily from the{" "}
          <a className="underline hover:text-[var(--ink)]" href="https://developer.adzuna.com">Adzuna API</a>{" "}
          (six role queries, Sydney), deduplicated, and matched against a{" "}
          <a className="underline hover:text-[var(--ink)]" href="https://github.com/sa1701/sydney-tech-pulse/blob/main/pipeline/src/pulse/taxonomy.py">
            ~90-skill taxonomy
          </a>{" "}
          of word-boundary patterns — deterministic, no LLM. Caveats: Adzuna truncates descriptions, so late-ad skills are
          undercounted uniformly; Adzuna coverage is not the whole market; predicted salaries are excluded from salary medians.
          Built by <a className="underline hover:text-[var(--ink)]" href="https://github.com/sa1701">Seif Ali</a> — pipeline: Python · Postgres · Docker · GitHub Actions; dashboard: Next.js.
        </p>
      </footer>
    </main>
  );
}
