"use client";

import { createContext, useContext, useState } from "react";
import { demo } from "@/lib/demo";
import type { AIInterpretation, Observation, RunStory } from "@/lib/run-story";
export type { Observation } from "@/lib/run-story";
type DemoContext = {
  currentRun: RunStory;
  loadRun: (run: RunStory) => void;
  resetRun: () => void;
  revision: number;
  aiResult: AIInterpretation | null;
  setAIResult: (value: AIInterpretation | null) => void;
  selectedId: string;
  setSelectedId: (id: string) => void;
  observations: Observation[];
  addObservation: (value: Observation) => void;
};
const Context = createContext<DemoContext | null>(null);
export function DemoProvider({ children }: { children: React.ReactNode }) {
  const [currentRun, setCurrentRun] = useState<RunStory>(demo);
  const [revision, setRevision] = useState(0);
  const [aiResult, setAIResult] = useState<AIInterpretation | null>(null);
  const [selectedId, setSelectedId] = useState("together");
  const [observations, setObservations] = useState<Observation[]>([]);
  function invalidate() {
    setAIResult(null);
    setRevision((r) => r + 1);
  }
  function loadRun(run: RunStory) {
    setCurrentRun(run);
    const lowest = run.glucose.reduce<{ minute: number; value: number } | null>(
      (best, point) => (!best || point.value < best.value ? point : best),
      null,
    );
    const lead = lowest
      ? run.moments.reduce((best, moment) =>
          Math.abs(moment.minute - lowest.minute) <
          Math.abs(best.minute - lowest.minute)
            ? moment
            : best,
        )
      : run.moments[0];
    setSelectedId(lead.id);
    setObservations([]);
    invalidate();
  }
  return (
    <Context.Provider
      value={{
        currentRun,
        loadRun,
        resetRun: () => loadRun(demo),
        revision,
        aiResult,
        setAIResult,
        selectedId,
        setSelectedId: (id) => {
          if (id !== selectedId) {
            setSelectedId(id);
            invalidate();
          }
        },
        observations,
        addObservation: (value) => {
          setObservations((current) => [...current, value]);
          invalidate();
        },
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useDemo() {
  const context = useContext(Context);
  if (!context) throw new Error("DemoProvider missing");
  return context;
}
