import fixture from "../../data/demo-run.json";
import type { RunMoment, RunStory } from "./run-story";

export const demo = fixture as RunStory;
export type DemoMoment = RunMoment;
export function momentUnknowns(
  moment: DemoMoment,
  observations: { kind: string; minute: number }[],
) {
  const nearby = observations.filter(
    (o) => o.minute >= moment.windowStart && o.minute <= moment.windowEnd,
  );
  return moment.unknowns.filter(
    (unknown) =>
      !(
        unknown === "Brak informacji o posiłku." &&
        nearby.some((o) => o.kind === "Posiłek")
      ) &&
      !(
        unknown === "Nie zapisano odczuć biegacza." &&
        nearby.some((o) => o.kind === "Odczucia")
      ),
  );
}
export const disclaimer =
  "To nie jest porada medyczna. Decyzje o lekach i jedzeniu w cukrzycy podejmuj z lekarzem.";
export const decimal = (value: number | null) =>
  value === null
    ? "—"
    : value.toLocaleString("pl-PL", {
        maximumFractionDigits: 1,
        minimumFractionDigits: 1,
      });
export const paceLabel = (value: number | null) => {
  if (value === null) return "Brak danych";
  const seconds = Math.round(value * 60);
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
};
export const minuteLabel = (minute: number) =>
  Number(minute.toFixed(1)).toLocaleString("pl-PL");
export function durationLabel(minutes: number) {
  const seconds = Math.round(minutes * 60);
  return `${Math.floor(seconds / 3600)}:${String(Math.floor(seconds / 60) % 60).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
}
export function dateLabel(run: RunStory) {
  return new Intl.DateTimeFormat("pl-PL", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    timeZone: run.timezone,
  }).format(new Date(run.start));
}
export function readingTime(run: RunStory, minute: number) {
  return new Intl.DateTimeFormat("pl-PL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: run.timezone,
  }).format(new Date(new Date(run.start).getTime() + minute * 60000));
}
export function factReferenceLabel(run: RunStory, ids: string[]) {
  const labels: Record<string, string> = {
    coveragePct: "Pokrycie glukozy w biegu",
    coveredMinutes: "Czas pokryty odczytami",
    minGlucose: "Najniższy odczyt w biegu",
    below70Count: "Liczba odczytów poniżej 70 mg/dL",
    below54Count: "Liczba odczytów poniżej 54 mg/dL",
    readingCount: "Liczba odczytów w biegu",
    averagePace: "Średnie tempo biegu",
    belowRangeCount: "Oznaczenia Low",
    aboveRangeCount: "Oznaczenia High",
    duration: "Czas biegu",
    distance: "Dystans biegu",
    "glucose.minimum": "Najniższy odczyt w oknie",
    "glucose.count": "Liczba odczytów w oknie",
    "altitude.change": "Zmiana wysokości w oknie",
    "altitude.ascent": "Suma podbiegów w oknie",
    heartrate: "Tętno w momencie",
    minute: "Minuta biegu",
    pace: "Tempo w momencie",
    hr: "Tętno w momencie",
    "window.start": "Początek okna",
    "window.end": "Koniec okna",
    "glucose.first": "Pierwszy odczyt w oknie",
    "glucose.last": "Ostatni odczyt w oknie",
    "glucose.first.minute": "Czas pierwszego odczytu",
    "glucose.last.minute": "Czas ostatniego odczytu",
    "glucose.delta": "Zmiana między pierwszym i ostatnim odczytem",
    "pace.firstHalf.average": "Średnie tempo przed momentem",
    "pace.secondHalf.average": "Średnie tempo po momencie",
    "hr.firstHalf.average": "Średnie tętno przed momentem",
    "hr.secondHalf.average": "Średnie tętno po momencie",
    "pace.baseline.average": "Średnie tempo z wcześniejszych 5 minut",
  };
  return ids
    .map((id) => {
      const fact = run.factRegistry?.[id];
      if (fact) {
        const suffix = id.substring(id.indexOf(".") + 1);
        const label =
          labels[suffix] ??
          (suffix.startsWith("signal.")
            ? "Sygnał z danych biegu"
            : "Obliczony fakt z danych");
        const unit =
          {
            readings: "odczytów",
            samples: "pomiarów",
            flags: "oznaczeń",
            bpm: "ud./min",
          }[fact.unit] ?? fact.unit;
        const value =
          fact.value === null
            ? "brak danych"
            : typeof fact.value === "number"
              ? unit === "min/km"
                ? paceLabel(fact.value)
                : Number(fact.value.toFixed(2)).toLocaleString("pl-PL")
              : "zarejestrowany";
        return `${label}: ${value}${fact.value !== null && unit ? ` ${unit}` : ""}`;
      }
      return (
        run.moments.flatMap((m) => m.factors).find((f) => f.factId === id)
          ?.evidence ?? "Obliczony kontekst biegu"
      );
    })
    .filter((value, index, all) => all.indexOf(value) === index)
    .join(" · ");
}
