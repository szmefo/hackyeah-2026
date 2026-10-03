"use client";
import { useSyncExternalStore } from "react";
import {
  type DemoMoment,
  paceLabel,
  minuteLabel,
  durationLabel,
  decimal,
} from "@/lib/demo";
import type { Point } from "@/lib/run-story";
import { useDemo } from "./demo-context";
import { DataBadge } from "./app-shell";
function subscribeViewport(onChange: () => void) {
  const media = window.matchMedia("(max-width: 780px)");
  media.addEventListener("change", onChange);
  return () => media.removeEventListener("change", onChange);
}
const compactViewport = () => window.matchMedia("(max-width: 780px)").matches;
const serverViewport = () => false;
function measuredSegments(samples: { minute: number; value: number | null }[]) {
  const segments: Point[][] = [];
  let current: Point[] = [];
  for (const p of samples) {
    if (p.value === null || !Number.isFinite(p.value)) {
      if (current.length) segments.push(current);
      current = [];
      continue;
    }
    if (current.length && p.minute - current[current.length - 1].minute > 2) {
      segments.push(current);
      current = [];
    }
    current.push({ minute: p.minute, value: p.value });
  }
  if (current.length) segments.push(current);
  return segments;
}
function Plot({
  kind,
  selected,
  onSelect,
}: {
  kind: "glucose" | "pace" | "hr";
  selected: DemoMoment;
  onSelect: (id: string) => void;
}) {
  const { currentRun: run } = useDemo();
  const compact = useSyncExternalStore(
    subscribeViewport,
    compactViewport,
    serverViewport,
  );
  const W = compact ? 400 : 760,
    H = compact ? 150 : 132,
    LEFT = 42,
    RIGHT = 14,
    TOP = 13,
    BOTTOM = 27;
  const duration = Math.max(run.durationMinutes, 0.01);
  const x = (minute: number) =>
    LEFT +
    (Math.max(0, Math.min(duration, minute)) / duration) * (W - LEFT - RIGHT);
  const segments =
    kind === "glucose"
      ? run.glucoseSegments
      : measuredSegments(
          run.samples.map((s) => ({
            minute: s.minute,
            value: kind === "pace" ? s.pace : s.hr,
          })),
        );
  const values = segments.flat().map((p) => p.value);
  const baseMin = kind === "glucose" ? 40 : kind === "pace" ? 4 : 90;
  const baseMax = kind === "glucose" ? 200 : kind === "pace" ? 9 : 180;
  const min = values.reduce((lo, v) => Math.min(lo, v), baseMin),
    max = values.reduce((hi, v) => Math.max(hi, v), baseMax);
  const reverse = kind === "pace";
  const y = (v: number, lo = min, hi = max, rev = reverse) =>
    TOP +
    (rev ? (v - lo) / (hi - lo || 1) : (hi - v) / (hi - lo || 1)) *
      (H - TOP - BOTTOM);
  const path = (points: Point[], lo = min, hi = max, rev = reverse) =>
    points
      .map(
        (p, i) =>
          `${i ? "L" : "M"}${x(p.minute).toFixed(2)},${y(p.value, lo, hi, rev).toFixed(2)}`,
      )
      .join(" ");
  const ticks =
    kind === "glucose"
      ? [
          70,
          180,
          ...(Math.abs(y(min) - y(70)) >= 18 ? [min] : []),
          ...(Math.abs(y(max) - y(180)) >= 18 ? [max] : []),
        ]
      : [min, (min + max) / 2, max];
  // Round tick intervals keep labels scannable; positions still use elapsed time.
  const tickStep =
    [1 / 60, 5 / 60, 0.25, 0.5, 1, 2, 5, 10, 15, 20, 30, 60, 120, 240, 480, 1440]
      .find((step) => step >= duration / (compact ? 3 : 5)) ?? duration / 5;
  const timeTicks = Array.from(
    { length: Math.floor(duration / tickStep) + 1 },
    (_, i) => i * tickStep,
  );
  if (duration - timeTicks[timeTicks.length - 1] < tickStep * 0.4) {
    timeTicks[timeTicks.length - 1] = duration;
  } else {
    timeTicks.push(duration);
  }
  const label =
    kind === "glucose" ? "Glukoza" : kind === "pace" ? "Tempo" : "Tętno";
  const unit =
    kind === "glucose" ? "mg/dL" : kind === "pace" ? "min/km" : "ud./min";
  const selectedValue =
    kind === "glucose"
      ? selected.minGlucose
      : kind === "pace"
        ? selected.pace
        : selected.hr;
  const terrain = measuredSegments(
    run.samples.map((s) => ({ minute: s.minute, value: s.altitude })),
  );
  const heights = terrain.flat().map((p) => p.value);
  const hMin = heights.reduce((lo, v) => Math.min(lo, v), heights[0] ?? 0) - 5;
  const hMax = heights.reduce((hi, v) => Math.max(hi, v), heights[0] ?? 0) + 5;
  return (
    <div className={`plot plot-${kind}`}>
      <div className="plot-heading">
        <span>
          {label}
          <small>{unit}</small>
        </span>
        {kind !== "glucose" && (
          <span className="plot-detail">
            {kind === "pace" && heights.length
              ? "wysokość trasy w tle"
              : run.synthetic
                ? "dane przykładowe"
                : "pomiar z zegarka"}
          </span>
        )}
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={`${label} w czasie biegu; wybrany moment ${minuteLabel(selected.minute)}. minuta`}
        onClick={(event) => {
          const rect = event.currentTarget.getBoundingClientRect();
          const minute =
            ((((event.clientX - rect.left) / rect.width) * W - LEFT) /
              (W - LEFT - RIGHT)) *
            duration;
          const nearest = run.moments.reduce((a, b) =>
            Math.abs(a.minute - minute) < Math.abs(b.minute - minute) ? a : b,
          );
          onSelect(nearest.id);
        }}
      >
        {kind === "glucose" && (
          <rect
            x={LEFT}
            y={y(180)}
            width={W - LEFT - RIGHT}
            height={y(70) - y(180)}
            fill="var(--accent)"
            opacity=".035"
          />
        )}
        {timeTicks.map((t) => (
          <g key={t}>
            <line
              x1={x(t)}
              x2={x(t)}
              y1={TOP}
              y2={H - BOTTOM}
              className="grid-line"
            />
            <text x={x(t)} y={H - 5} textAnchor="middle" className="axis-label">
              {durationLabel(t).replace(/^0:/, "")}
            </text>
          </g>
        ))}
        {ticks.map((t) => (
          <g key={t}>
            <line
              x1={LEFT}
              x2={W - RIGHT}
              y1={y(t)}
              y2={y(t)}
              className={
                kind === "glucose" && (t === 70 || t === 180)
                  ? "range-line"
                  : "grid-line"
              }
            />
            <text
              x={LEFT - 10}
              y={y(t) + 4}
              textAnchor="end"
              className="axis-label"
            >
              {kind === "pace" ? paceLabel(t) : Math.round(t)}
            </text>
          </g>
        ))}
        {kind === "pace" &&
          terrain.map((s, i) => (
            <path
              key={i}
              d={`${path(s, hMin, hMax, false)} L${x(s[s.length - 1].minute)},${H - BOTTOM} L${x(s[0].minute)},${H - BOTTOM} Z`}
              className="terrain-area"
            />
          ))}
        <rect
          x={x(selected.windowStart)}
          y={TOP}
          width={x(selected.windowEnd) - x(selected.windowStart)}
          height={H - BOTTOM - TOP}
          className="selection-window"
        />
        {kind === "glucose" &&
          run.gaps.map((gap) => (
            <g key={`${gap.start}-${gap.end}`}>
              <rect
                x={x(gap.start)}
                y={TOP}
                width={x(gap.end) - x(gap.start)}
                height={H - TOP - BOTTOM}
                fill="url(#missing-pattern)"
              />
              {x(gap.end) - x(gap.start) > 70 && (
                <>
                  <text
                    x={x((gap.start + gap.end) / 2)}
                    y={49}
                    textAnchor="middle"
                    className="gap-label"
                  >
                    Brak danych
                  </text>
                  <text
                    x={x((gap.start + gap.end) / 2)}
                    y={65}
                    textAnchor="middle"
                    className="axis-label"
                  >
                    {minuteLabel(gap.start)}–{minuteLabel(gap.end)} min
                  </text>
                </>
              )}
            </g>
          ))}
        <defs>
          <pattern
            id="missing-pattern"
            width="8"
            height="8"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M-2 2 2-2M0 8 8 0M6 10 10 6"
              stroke="var(--muted)"
              strokeWidth=".3"
              opacity=".18"
            />
          </pattern>
        </defs>
        {segments.map((segment, i) =>
          segment.length === 1 ? (
            <circle
              key={i}
              cx={x(segment[0].minute)}
              cy={y(segment[0].value)}
              r="3"
              className={
                kind === "glucose" ? "glucose-single" : "neutral-single"
              }
            />
          ) : (
            <path
              key={i}
              d={path(segment)}
              fill="none"
              className={`data-line ${kind === "glucose" ? "glucose-line" : "neutral-line"}`}
            />
          ),
        )}
        {!values.length && (
          <text x={W / 2} y={H / 2} textAnchor="middle" className="gap-label">
            Brak pomiarów {label.toLowerCase()}
          </text>
        )}
        {kind === "glucose" &&
          run.glucoseFlags?.map((p) => (
            <text
              key={`${p.minute}-${p.flag}`}
              x={x(p.minute)}
              y={p.flag === "below_range" ? H - BOTTOM - 4 : TOP + 12}
              textAnchor="middle"
              className="axis-label"
            >
              {p.flag === "below_range" ? "Low" : "High"}
            </text>
          ))}
        <line
          x1={x(selected.minute)}
          x2={x(selected.minute)}
          y1={TOP}
          y2={H - BOTTOM}
          className="cursor-line"
        />
        {selectedValue !== null && kind !== "glucose" && (
          <circle
            cx={x(selected.minute)}
            cy={y(selectedValue)}
            r="3.5"
            fill="var(--cream)"
          />
        )}
        {kind === "glucose" &&
          selectedValue !== null &&
          (() => {
            const p = run.glucose.find(
              (p) =>
                p.minute >= selected.windowStart &&
                p.minute <= selected.windowEnd &&
                p.value === selectedValue,
            );
            return p ? (
              <g>
                <circle
                  cx={x(p.minute)}
                  cy={y(p.value)}
                  r="4"
                  fill="var(--cream)"
                />
                <text
                  x={Math.min(x(p.minute) + 9, W - 28)}
                  y={y(p.value) + 15}
                  className="point-label"
                >
                  {p.value}
                </text>
              </g>
            ) : null;
          })()}
      </svg>
    </div>
  );
}
export function Timeline({
  selected,
  onSelect,
}: {
  selected: DemoMoment;
  onSelect: (id: string) => void;
}) {
  const { currentRun: run } = useDemo();
  return (
    <section className="timeline-section" aria-labelledby="timeline-title">
      <div className="section-label">
        <div>
          <h2 id="timeline-title">Analiza biegu</h2>
          <p>Trzy wykresy, jedna oś czasu.</p>
        </div>
        <DataBadge synthetic={run.synthetic} />
      </div>
      <div className="chart-card">
        <Plot kind="glucose" selected={selected} onSelect={onSelect} />
        <Plot kind="pace" selected={selected} onSelect={onSelect} />
        <Plot kind="hr" selected={selected} onSelect={onSelect} />
        <div className="chart-legend">
          <span>
            <i className="legend-glucose" /> Glukoza
          </span>
          <span>
            <i className="legend-pace" /> Tempo
          </span>
          <span>
            <i className="legend-hr" /> Tętno
          </span>
          <span>
            <i className="legend-terrain" /> Teren
          </span>
          <span>{durationLabel(run.durationMinutes)}</span>
        </div>
      </div>
      <div className="moment-picker" role="group" aria-label="Wybierz moment biegu">
        {run.moments.map((m, i) => (
          <button
            key={m.id}
            onClick={() => onSelect(m.id)}
            aria-pressed={selected.id === m.id}
            className={selected.id === m.id ? "selected" : ""}
          >
            <span className="moment-number">
              {String(i + 1).padStart(2, "0")}
            </span>
            <span>
              {m.label}
              <small>
                {minuteLabel(m.minute)}. minuta
                {m.distanceKm !== null ? ` · ${decimal(m.distanceKm)} km` : ""}
              </small>
            </span>
            <span className={`moment-dot ${m.id}`} />
          </button>
        ))}
      </div>
      <p className="chart-note">
        Wybierz moment, aby zmienić podsumowanie. Możesz też kliknąć wykres.
        Tempo w min/km: niżej na
        wykresie oznacza wolniej.{" "}
        {run.synthetic
          ? "Wszystkie przebiegi są przykładowe."
          : "Brakujących pomiarów nie uzupełniamy."}
      </p>
      <div className="moment-evidence" aria-live="polite">
        <span className="eyebrow">
          Wybrane okno · {minuteLabel(selected.windowStart)}–{minuteLabel(selected.windowEnd)} min
        </span>
        <div>
          <span>
            Najniższa glukoza w oknie{" "}
            <strong>
              {selected.minGlucose === null
                ? "Brak danych"
                : `${selected.minGlucose} mg/dL`}
            </strong>
          </span>
          <span>
            Tempo w momencie{" "}
            <strong>
              {paceLabel(selected.pace)}
              {selected.pace !== null ? " min/km" : ""}
            </strong>
          </span>
          <span>
            Tętno w momencie{" "}
            <strong>
              {selected.hr === null
                ? "Brak danych"
                : `${Math.round(selected.hr)} ud./min`}
            </strong>
          </span>
        </div>
      </div>
    </section>
  );
}
