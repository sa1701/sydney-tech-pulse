"use client";

import { useState } from "react";
import type { TopSkill } from "@/lib/data";

const FAMILIES = [
  ["all", "All"],
  ["language", "Languages"],
  ["frontend", "Frontend"],
  ["backend", "Backend"],
  ["data", "Data"],
  ["cloud", "Cloud"],
  ["devops", "DevOps"],
  ["ai", "AI"],
  ["practice", "Practices"],
] as const;

export default function TopSkills({ skills }: { skills: TopSkill[] }) {
  const [family, setFamily] = useState<string>("all");

  const rows = skills
    .filter((s) => family === "all" || s.family === family)
    .slice(0, 20);
  const max = rows[0]?.mentions ?? 1;

  return (
    <section className="panel p-6 sm:p-8">
      <div className="flex flex-wrap items-baseline justify-between gap-3 mb-6">
        <h2 className="text-xl font-semibold">Top skills right now</h2>
        <span className="spec">Trailing 30 days</span>
      </div>

      <div className="flex flex-wrap gap-2 mb-7" role="tablist" aria-label="Skill family filter">
        {FAMILIES.map(([key, label]) => (
          <button
            key={key}
            role="tab"
            aria-selected={family === key}
            onClick={() => setFamily(key)}
            className={`mono text-xs px-3 py-1.5 rounded-full border transition-colors ${
              family === key
                ? "border-[var(--signal)] text-[var(--signal)]"
                : "border-[var(--line)] text-[var(--muted)] hover:text-[var(--ink)]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {rows.length === 0 ? (
        <p className="mono text-sm text-[var(--muted)]">pipeline warming up…</p>
      ) : (
        <ol className="space-y-2.5">
          {rows.map((s, i) => (
            <li key={s.slug} className="grid grid-cols-[1.5rem_6.5rem_1fr_3.5rem] sm:grid-cols-[2.5rem_11rem_1fr_5.5rem] items-center gap-2 sm:gap-3">
              <span className="mono text-xs text-[var(--muted)]">{String(i + 1).padStart(2, "0")}</span>
              <span className="text-sm truncate">{s.display}</span>
              <span className="h-2.5 rounded-sm bg-[var(--line)] overflow-hidden">
                <span
                  className="block h-full rounded-sm bg-[var(--signal)] transition-[width] duration-500"
                  style={{ width: `${(s.mentions / max) * 100}%` }}
                />
              </span>
              <span className="mono text-[10px] sm:text-xs text-[var(--muted)] text-right whitespace-nowrap">
                <span className="hidden sm:inline">{s.mentions} · </span>
                {(s.share * 100).toFixed(1)}%
              </span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
