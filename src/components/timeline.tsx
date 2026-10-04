"use client";
import { useSyncExternalStore } from "react";
import {
  type DemoMoment,
  paceLabel,
  minuteLabel,
  durationLabel,
  decimal,
} from "@/lib/demo";
import type { Point, RunStory } from "@/lib/run-story";
import { useDemo } from "./demo-context";
import { DataBadge, SyntheticBadge } from "./app-shell";

/** A run counts as synthetic when either the flag or its provenance says so. */
export function isSyntheticRun(run: RunStory) {
  return run.synthetic === true || run.provenance?.kind === "synthetic";
}
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
/**
 * Keeps required ticks (e.g. the 70 and 180 mg/dL range lines) and adds
 * optional ones only when their labels cannot touch any label already kept.
 */
function spacedTicks(
  required: number[],
  optional: number[],
  position: (value: number) => number,
  minGap: number,
) {
  const kept: number[] = [];
  for (const value of [...required, ...optional]) {
    if (!Number.isFinite(value)) continue;
    if (kept.some((t) => Math.abs(position(t) - position(value)) < minGap))
      continue;
    kept.push(value);
  }
  return kept.sort((a, b) => a - b);
}
/** Same idea for the time axis: estimated label widths must not touch. */
function spacedTimeTicks(
  candidates: number[],
  duration: number,
  position: (minute: number) => number,
  text: (minute: number) => string,
  charWidth: number,
) {
  const span = (t: number) => {
    const w = text(t).length * charWidth;
    const x = position(t);
    if (t === 0) return [x, x + w];
    if (t === duration) return [x - w, x];
    return [x - w / 2, x + w / 2];
  };
  const ordered = [0, duration, ...candidates.filter((t) => t > 0 && t < duration)];
  const kept: number[] = [];
  for (const t of ordered) {
    const [a, b] = span(t);
    if (kept.some((k) => {
      const [c, d] = span(k);
      return a < d + 10 && c < b + 10;
    }))
      continue;
    kept.push(t);
  }
  return kept.sort((a, b) => a - b);
}
const timeText = (t: number) => durationLabel(t).replace(/^0:/, "");
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
  const synthetic = isSyntheticRun(run);
  const compact = useSyncExternalStore(
    subscribeViewport,
    compactViewport,
    serverViewport,
  );
  // Glucose is the primary chart, so it gets more height for the 70–180 band.
  const W = compact ? 400 : 760,
    H =
      kind === "glucose" ? (compact ? 196 : 172) : compact ? 150 : 132,
    LEFT = 42,
    RIGHT = 14,
    TOP = 13,
    BOTTOM = 30;
  // Axis labels are 13–14 user units tall; keep their centres further apart.
  const LABEL_GAP = 21;
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
  const dataMin = values.reduce((lo, v) => Math.min(lo, v), Infinity);
  const dataMax = values.reduce((hi, v) => Math.max(hi, v), -Infinity);
  // Round the axis domain so the outer tick labels are readable numbers.
  const [min, max] =
    kind === "glucose"
      ? [
          Math.min(40, Math.floor(dataMin / 10) * 10),
          Math.max(200, Math.ceil(dataMax / 50) * 50),
        ]
      : kind === "pace"
        ? [
            Math.min(4, Math.floor(dataMin * 2) / 2),
            Math.max(9, Math.ceil(dataMax * 2) / 2),
          ]
        : [
            Math.min(90, Math.floor(dataMin / 10) * 10),
            Math.max(180, Math.ceil(dataMax / 10) * 10),
          ];
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
  const mid =
    kind === "pace"
      ? Math.round(min + max) / 2
      : Math.round((min + max) / 10) * 5;
  const ticks =
    kind === "glucose"
      ? spacedTicks(
          [70, 180],
          [min, max, ...[250, 300, 350].filter((v) => v > 180 && v < max)],
          (v) => y(v),
          LABEL_GAP,
        )
      : spacedTicks([], [min, max, mid], (v) => y(v), LABEL_GAP);
  // Round tick intervals keep labels scannable; positions still use elapsed time.
  const tickStep =
    [1 / 60, 5 / 60, 0.25, 0.5, 1, 2, 5, 10, 15, 20, 30, 60, 120, 240, 480, 1440]
      .find((step) => step >= duration / (compact ? 3 : 5)) ?? duration / 5;
  const timeTicks = spacedTimeTicks(
    Array.from(
      { length: Math.floor(duration / tickStep) + 1 },
      (_, i) => i * tickStep,
    ),
    duration,
    x,
    timeText,
    compact ? 8 : 8.5,
  );
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
  // A minimum 60 m span keeps a few metres of altitude noise visually flat,
  // so a flat run never draws as hills; real climbs still fill the chart.
  const hMax = Math.max(
    heights.reduce((hi, v) => Math.max(hi, v), heights[0] ?? 0) + 5,
    hMin + 60,
  );
  const plotMid = TOP + (H - TOP - BOTTOM) / 2;
  // Low/High flags: a marker for every flag, a text label only where it fits.
  const flagLabels: { minute: number; flag: string }[] = [];
  for (const f of run.glucoseFlags ?? []) {
    if (
      flagLabels.every(
        (p) => p.flag !== f.flag || Math.abs(x(p.minute) - x(f.minute)) >= 40,
      )
    )
      flagLabels.push(f);
  }
  return (
    <div className={`plot plot-${kind}`}>
      <div className="plot-heading">
        <span>
          {label}
          <small>{unit}</small>
        </span>
        {kind === "glucose" ? (
          synthetic && <SyntheticBadge />
        ) : (
          <span className="plot-detail">
            {kind === "pace" && heights.length
              ? "wysokość trasy w tle"
              : synthetic
                ? "dane przykładowe"
                : "pomiar z zegarka"}
          </span>
        )}
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={`${label} w czasie biegu${synthetic ? " (dane syntetyczne)" : ""}; wybrany moment ${minuteLabel(selected.minute)}. minuta`}
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
            className="range-band"
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
            <text
              x={x(t)}
              y={H - 6}
              textAnchor={t === 0 ? "start" : t === duration ? "end" : "middle"}
              className="axis-label"
            >
              {timeText(t)}
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
              x={LEFT - 8}
              y={y(t)}
              dominantBaseline="middle"
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
              {x(gap.end) - x(gap.start) > 84 && (
                <>
                  <text
                    x={x((gap.start + gap.end) / 2)}
                    y={plotMid - 10}
                    textAnchor="middle"
                    className="gap-label"
                  >
                    Brak danych
                  </text>
                  <text
                    x={x((gap.start + gap.end) / 2)}
                    y={plotMid + 12}
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
          <text x={W / 2} y={plotMid} textAnchor="middle" className="gap-label">
            Brak pomiarów {label.toLowerCase()}
          </text>
        )}
        {kind === "glucose" &&
          run.glucoseFlags?.map((p) => (
            <line
              key={`m-${p.minute}-${p.flag}`}
              x1={x(p.minute)}
              x2={x(p.minute)}
              y1={p.flag === "below_range" ? H - BOTTOM - 6 : TOP}
              y2={p.flag === "below_range" ? H - BOTTOM : TOP + 6}
              className="flag-mark"
            />
          ))}
        {kind === "glucose" &&
          flagLabels.map((p) => (
            <text
              key={`${p.minute}-${p.flag}`}
              x={Math.max(LEFT + 14, Math.min(W - RIGHT - 14, x(p.minute)))}
              y={p.flag === "below_range" ? H - BOTTOM - 10 : TOP + 18}
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
            if (!p) return null;
            // Below the point unless that would reach the time axis.
            const below = y(p.value) + 17 <= H - BOTTOM - 2;
            return (
              <g>
                <circle
                  cx={x(p.minute)}
                  cy={y(p.value)}
                  r="4"
                  fill="var(--cream)"
                />
                <text
                  x={Math.min(x(p.minute) + 9, W - RIGHT - 26)}
                  y={below ? y(p.value) + 15 : y(p.value) - 9}
                  className="point-label"
                >
                  {p.value}
                </text>
              </g>
            );
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
  const synthetic = isSyntheticRun(run);
  return (
    <section className="timeline-section" aria-labelledby="timeline-title">
      <div className="section-label">
        <div>
          <h2 id="timeline-title">Analiza biegu</h2>
          <p>Trzy wykresy, jedna oś czasu.</p>
        </div>
        {/* Synthetic runs carry the badge on the glucose chart itself. */}
        {!synthetic && <DataBadge synthetic={false} />}
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
            <i className="legend-band" /> Zakres 70–180 mg/dL
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
        {run.moments.map((m, i) => {
          const where =
            m.distanceKm !== null
              ? `${decimal(m.distanceKm)} km`
              : "dystans nieznany";
          return (
            <button
              key={m.id}
              onClick={() => onSelect(m.id)}
              aria-pressed={selected.id === m.id}
              aria-label={`Moment ${i + 1}: ${m.label}, ${minuteLabel(m.minute)}. minuta, ${where}`}
              title={m.title}
              className={selected.id === m.id ? "selected" : ""}
            >
              <span className="moment-number">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="moment-text">
                <strong className="moment-label">{m.label}</strong>
                <small className="moment-where">
                  <span>{minuteLabel(m.minute)}. min</span>
                  <span aria-hidden="true">·</span>
                  <span>{where}</span>
                </small>
              </span>
              <span className={`moment-dot ${m.id}`} />
            </button>
          );
        })}
      </div>
      <p className="chart-note">
        Wybierz moment, aby zmienić podsumowanie. Możesz też kliknąć wykres.
        Tempo w min/km: niżej na
        wykresie oznacza wolniej.{" "}
        {synthetic
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
