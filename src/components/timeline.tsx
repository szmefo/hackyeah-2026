"use client";

import { useSyncExternalStore } from "react";
import { demo, type DemoMoment, paceLabel } from "@/lib/demo";
import { SyntheticBadge } from "./app-shell";

function plotGeometry(compact: boolean) {
  const W = compact ? 400 : 760,
    H = compact ? 130 : 116,
    LEFT = 42,
    RIGHT = 14,
    TOP = 13,
    BOTTOM = 27;
  const x = (minute: number) =>
    LEFT + (minute / demo.durationMinutes) * (W - LEFT - RIGHT);
  const y = (value: number, min: number, max: number, reverse = false) =>
    TOP +
    (reverse ? (value - min) / (max - min) : (max - value) / (max - min)) *
      (H - TOP - BOTTOM);
  const path = (
    points: { minute: number; value: number }[],
    min: number,
    max: number,
    reverse = false,
  ) =>
    points
      .map(
        (p, i) =>
          `${i ? "L" : "M"}${x(p.minute).toFixed(2)},${y(p.value, min, max, reverse).toFixed(2)}`,
      )
      .join(" ");
  return { W, H, LEFT, RIGHT, TOP, BOTTOM, x, y, path };
}

function subscribeViewport(onChange: () => void) {
  const media = window.matchMedia("(max-width: 780px)");
  media.addEventListener("change", onChange);
  return () => media.removeEventListener("change", onChange);
}
const compactViewport = () => window.matchMedia("(max-width: 780px)").matches;
const serverViewport = () => false;

function Plot({
  kind,
  selected,
  onSelect,
}: {
  kind: "glucose" | "pace" | "hr";
  selected: DemoMoment;
  onSelect: (id: string) => void;
}) {
  const compact = useSyncExternalStore(
    subscribeViewport,
    compactViewport,
    serverViewport,
  );
  const { W, H, LEFT, RIGHT, TOP, BOTTOM, x, y, path } = plotGeometry(compact);
  const min = kind === "glucose" ? 40 : kind === "pace" ? 4 : 90;
  const max = kind === "glucose" ? 200 : kind === "pace" ? 9 : 180;
  const ticks =
    kind === "glucose"
      ? [180, 120, 70]
      : kind === "pace"
        ? [4, 6, 8]
        : [180, 140, 100];
  const reverse = kind === "pace";
  const segments =
    kind === "glucose"
      ? demo.glucoseSegments
      : [
          demo.samples.map((s) => ({
            minute: s.minute,
            value: kind === "pace" ? s.pace : s.hr,
          })),
        ];
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
  return (
    <div className={`plot plot-${kind}`}>
      <div className="plot-heading">
        <span>
          {label}
          <small>{unit}</small>
        </span>
        {kind === "glucose" ? (
          <SyntheticBadge />
        ) : (
          <span className="plot-detail">
            {kind === "pace" ? "wysokość trasy w tle" : "dane przykładowe"}
          </span>
        )}
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={`${label} w czasie biegu; wybrany moment ${selected.minute}. minuta`}
        onClick={(event) => {
          const rect = event.currentTarget.getBoundingClientRect();
          const minute =
            ((((event.clientX - rect.left) / rect.width) * W - LEFT) /
              (W - LEFT - RIGHT)) *
            demo.durationMinutes;
          const nearest = demo.moments.reduce((a, b) =>
            Math.abs(a.minute - minute) < Math.abs(b.minute - minute) ? a : b,
          );
          onSelect(nearest.id);
        }}
      >
        {kind === "glucose" && (
          <rect
            x={LEFT}
            y={y(180, min, max)}
            width={W - LEFT - RIGHT}
            height={y(70, min, max) - y(180, min, max)}
            fill="var(--accent)"
            opacity=".035"
          />
        )}
        {[0, 20, 40, 60, 80, 94].map((t) => (
          <g key={t}>
            <line
              x1={x(t)}
              x2={x(t)}
              y1={TOP}
              y2={H - BOTTOM}
              className="grid-line"
            />
            <text x={x(t)} y={H - 5} textAnchor="middle" className="axis-label">
              {t === 94
                ? "1:34"
                : `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`}
            </text>
          </g>
        ))}
        {ticks.map((t) => (
          <g key={t}>
            <line
              x1={LEFT}
              x2={W - RIGHT}
              y1={y(t, min, max, reverse)}
              y2={y(t, min, max, reverse)}
              className={
                kind === "glucose" && (t === 70 || t === 180)
                  ? "range-line"
                  : "grid-line"
              }
            />
            <text
              x={LEFT - 10}
              y={y(t, min, max, reverse) + 4}
              textAnchor="end"
              className="axis-label"
            >
              {kind === "pace" ? `${t}:00` : t}
            </text>
          </g>
        ))}
        {kind === "pace" && (
          <path
            d={`${path(
              demo.samples.map((s) => ({
                minute: s.minute,
                value: s.altitude,
              })),
              195,
              270,
            )} L${x(94)},${H - BOTTOM} L${LEFT},${H - BOTTOM} Z`}
            className="terrain-area"
          />
        )}
        <rect
          x={x(selected.windowStart)}
          y={TOP}
          width={x(selected.windowEnd) - x(selected.windowStart)}
          height={H - BOTTOM - TOP}
          className="selection-window"
        />
        {kind === "glucose" &&
          demo.gaps.map((gap) => (
            <g key={gap.start}>
              <rect
                x={x(gap.start)}
                y={TOP}
                width={x(gap.end) - x(gap.start)}
                height={H - TOP - BOTTOM}
                fill="url(#missing-pattern)"
              />
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
                {gap.start}–{gap.end} min
              </text>
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
        {segments.map((segment, i) => (
          <path
            key={i}
            d={path(segment, min, max, reverse)}
            fill="none"
            className={`data-line ${kind === "glucose" ? "glucose-line" : "neutral-line"}`}
          />
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
            cy={y(selectedValue, min, max, reverse)}
            r="3.5"
            fill="var(--cream)"
          />
        )}
        {kind === "glucose" &&
          selectedValue !== null &&
          (() => {
            const point = demo.glucose.find(
              (p) =>
                p.minute >= selected.windowStart &&
                p.minute <= selected.windowEnd &&
                p.value === selectedValue,
            );
            return point ? (
              <g>
                <circle
                  cx={x(point.minute)}
                  cy={y(point.value, min, max)}
                  r="4"
                  fill="var(--cream)"
                />
                <text
                  x={x(point.minute) + 9}
                  y={y(point.value, min, max) + 15}
                  className="point-label"
                >
                  {point.value}
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
  return (
    <section className="timeline-section" aria-labelledby="timeline-title">
      <div className="section-label">
        <h2 id="timeline-title">Przebieg biegu</h2>
        <span>Wspólna oś czasu</span>
      </div>
      <div className="chart-card">
        <div className="chart-topline">
          <span>
            <span className="live-dot" /> Wybrany moment · {selected.minute}.
            minuta
          </span>
          <span>Okno ±10 min</span>
        </div>
        <Plot kind="glucose" selected={selected} onSelect={onSelect} />
        <Plot kind="pace" selected={selected} onSelect={onSelect} />
        <Plot kind="hr" selected={selected} onSelect={onSelect} />
        <div className="chart-legend">
          <span>
            <i className="legend-glucose" /> Glukoza
          </span>
          <span>
            <i className="legend-neutral" /> Tempo i tętno
          </span>
          <span>
            <i className="legend-terrain" /> Teren
          </span>
          <span>1:34:00</span>
        </div>
      </div>
      <div className="moment-picker" aria-label="Wybierz moment biegu">
        {demo.moments.map((m, i) => (
          <button
            key={m.id}
            onClick={() => onSelect(m.id)}
            aria-pressed={selected.id === m.id}
            className={selected.id === m.id ? "selected" : ""}
          >
            <span className="moment-number">0{i + 1}</span>
            <span>
              {m.label}
              <small>
                {m.minute}. minuta · {m.distanceKm.toLocaleString("pl-PL")} km
              </small>
            </span>
            <span className={`moment-dot ${m.id}`} />
          </button>
        ))}
      </div>
      <p className="chart-note">
        Wybierz moment poniżej lub kliknij wykres. Tempo w min/km: niżej na
        wykresie oznacza wolniej. Wszystkie przebiegi są przykładowe.
      </p>
      <div className="moment-evidence" aria-live="polite">
        <span className="eyebrow">W wybranym oknie</span>
        <div>
          <span>
            Glukoza{" "}
            <strong>
              {selected.minGlucose === null
                ? "Brak danych"
                : `${selected.minGlucose} mg/dL`}
            </strong>
          </span>
          <span>
            Tempo w momencie <strong>{paceLabel(selected.pace)} min/km</strong>
          </span>
          <span>
            Tętno w momencie <strong>{selected.hr} ud./min</strong>
          </span>
        </div>
      </div>
    </section>
  );
}
