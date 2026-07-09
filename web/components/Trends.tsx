"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { WeeklyCount } from "@/lib/data";

const DEFAULT_SERIES = ["python", "typescript", "aws", "react", "machine-learning"];
const PALETTE = ["#3ddc84", "#5eb1ff", "#ffb01f", "#ff6b81", "#c792ea", "#7fdbca", "#f78c6c"];

export default function Trends({ weekly }: { weekly: WeeklyCount[] }) {
  const available = useMemo(() => {
    const totals = new Map<string, { display: string; total: number }>();
    for (const r of weekly) {
      const t = totals.get(r.slug) ?? { display: r.display, total: 0 };
      t.total += r.mentions;
      totals.set(r.slug, t);
    }
    const ranked = Array.from(totals.entries()).sort((a, b) => b[1].total - a[1].total);
    const top = ranked.slice(0, 14);
    // keep default series toggleable even when they fall outside the top 14
    for (const slug of DEFAULT_SERIES) {
      if (!top.some(([s]) => s === slug)) {
        const hit = ranked.find(([s]) => s === slug);
        if (hit) top.push(hit);
      }
    }
    return top.map(([slug, v]) => ({ slug, display: v.display }));
  }, [weekly]);

  const [active, setActive] = useState<string[]>(DEFAULT_SERIES);

  const data = useMemo(() => {
    const byWeek = new Map<string, Record<string, number | string>>();
    for (const r of weekly) {
      if (!active.includes(r.slug)) continue;
      const row = byWeek.get(r.week) ?? { week: r.week.slice(5) };
      row[r.slug] = Math.round(r.share * 1000) / 10; // % share
      byWeek.set(r.week, row);
    }
    return Array.from(byWeek.values());
  }, [weekly, active]);

  const toggle = (slug: string) =>
    setActive((a) => (a.includes(slug) ? a.filter((s) => s !== slug) : [...a, slug].slice(-7)));

  return (
    <section className="panel p-6 sm:p-8">
      <div className="flex flex-wrap items-baseline justify-between gap-3 mb-6">
        <h2 className="text-xl font-semibold">Weekly demand trends</h2>
        <span className="spec">% of postings mentioning skill</span>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {available.map(({ slug, display }) => {
          const idx = active.indexOf(slug);
          return (
            <button
              key={slug}
              onClick={() => toggle(slug)}
              aria-pressed={idx >= 0}
              className={`mono text-xs px-3 py-1.5 rounded-full border transition-colors ${
                idx >= 0
                  ? "border-transparent text-[#0b0e11] font-semibold"
                  : "border-[var(--line)] text-[var(--muted)] hover:text-[var(--ink)]"
              }`}
              style={idx >= 0 ? { background: PALETTE[idx % PALETTE.length] } : undefined}
            >
              {display}
            </button>
          );
        })}
      </div>

      {data.length < 2 ? (
        <p className="mono text-sm text-[var(--muted)]">
          not enough weekly history yet — check back after a few daily runs
        </p>
      ) : (
        <div className="h-72 -ml-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 6, right: 12, bottom: 0, left: -14 }}>
              <CartesianGrid stroke="#232a33" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="week" stroke="#8494a6" tick={{ fontSize: 11, fontFamily: "var(--font-mono)" }} />
              <YAxis stroke="#8494a6" tick={{ fontSize: 11, fontFamily: "var(--font-mono)" }} unit="%" />
              <Tooltip
                contentStyle={{ background: "#12161b", border: "1px solid #232a33", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#8494a6" }}
                formatter={(v, name) => [`${v}%`, available.find((a) => a.slug === name)?.display ?? String(name)]}
              />
              {active.map((slug, i) => (
                <Line
                  key={slug}
                  type="monotone"
                  dataKey={slug}
                  stroke={PALETTE[i % PALETTE.length]}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
