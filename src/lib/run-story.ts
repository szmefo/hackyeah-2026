export type Observation = { text: string; minute: number; kind: string };
export type Point = { minute: number; value: number };
export type RunMoment = {
  id: string;
  minute: number;
  label: string;
  title: string;
  distanceKm: number | null;
  windowStart: number;
  windowEnd: number;
  minGlucose: number | null;
  readingCount: number;
  pace: number | null;
  hr: number | null;
  altitudeChange: number | null;
  altitudeAscent?: number | null;
  factors: { id: string; label: string; evidence: string; factId: string }[];
  narrative: string;
  unknowns: string[];
  question: string;
  separable: boolean;
};
export type RunStory = {
  analysisToken?: string;
  schemaVersion: number;
  synthetic: boolean;
  seed?: number;
  title: string;
  date: string;
  start: string;
  timezone: string;
  durationMinutes: number;
  distanceKm: number | null;
  samples: {
    minute: number;
    pace: number | null;
    hr: number | null;
    altitude: number | null;
    distanceKm: number | null;
  }[];
  glucose: Point[];
  glucoseFlags?: { minute: number; flag: "below_range" | "above_range" }[];
  glucoseSegments: Point[][];
  gaps: { start: number; end: number }[];
  moments: RunMoment[];
  facts: {
    coveragePct: number;
    coveredMinutes: number;
    minGlucose: number | null;
    below70Count: number;
    below54Count: number;
    readingCount: number;
    averagePace: number | null;
    basis: string;
  };
  provenance: {
    kind: "synthetic" | "uploaded";
    engineUsed: boolean;
    clinicalValidation: false;
  };
  factRegistry?: Record<
    string,
    { value: number | string | null; unit: string; description: string }
  >;
  strengths?: string[];
  warnings?: string[];
};
export type AIInterpretation =
  | {
      status: "ai";
      claims: { text: string; factIds: string[] }[];
      alternatives: { text: string; factIds: string[] }[];
      unknowns: string[];
      questions: string[];
      review: "passed";
      provider: string;
      model: string;
    }
  | { status: "fallback"; reason: string };
