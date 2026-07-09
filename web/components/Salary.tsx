import type { SkillSalary } from "@/lib/data";

const fmt = (n: number) => `$${Math.round(n / 1000)}k`;

export default function Salary({ salaries }: { salaries: SkillSalary[] }) {
  if (salaries.length === 0) {
    return (
      <section className="panel p-6 sm:p-8">
        <h2 className="text-xl font-semibold mb-2">Salary bands by skill</h2>
        <p className="mono text-sm text-[var(--muted)]">
          not enough employer-stated salaries yet (n ≥ 3 required per skill)
        </p>
      </section>
    );
  }

  const lo = Math.min(...salaries.map((s) => s.median_salary_min));
  const hi = Math.max(...salaries.map((s) => s.median_salary_max));
  const span = hi - lo || 1;
  const pos = (v: number) => ((v - lo) / span) * 100;

  return (
    <section className="panel p-6 sm:p-8">
      <div className="flex flex-wrap items-baseline justify-between gap-3 mb-7">
        <h2 className="text-xl font-semibold">Salary bands by skill</h2>
        <span className="spec">
          Median advertised range · {fmt(lo)}–{fmt(hi)}
        </span>
      </div>

      <ol className="space-y-3">
        {salaries.map((s) => (
          <li
            key={s.slug}
            className="grid grid-cols-[9rem_1fr] sm:grid-cols-[11rem_1fr_8rem] items-center gap-3"
          >
            <span className="text-sm truncate">
              {s.display}
              <span className="mono text-[10px] text-[var(--muted)] ml-2">n={s.sample_size}</span>
            </span>
            <span className="relative h-2.5 rounded-full bg-[var(--line)]">
              <span
                className="absolute h-full rounded-full bg-gradient-to-r from-[var(--signal)]/50 to-[var(--signal)]"
                style={{
                  left: `${pos(s.median_salary_min)}%`,
                  width: `${Math.max(pos(s.median_salary_max) - pos(s.median_salary_min), 2)}%`,
                }}
              />
            </span>
            <span className="mono text-xs text-[var(--muted)] text-right hidden sm:block">
              {fmt(s.median_salary_min)} – {fmt(s.median_salary_max)}
            </span>
          </li>
        ))}
      </ol>

      <p className="mono text-[11px] text-[var(--muted)] mt-6">
        employer-stated salaries only (Adzuna-predicted excluded) · medians per skill · n ≥ 3
      </p>
    </section>
  );
}
