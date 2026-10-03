"use client";

import { createContext, useContext, useState } from "react";
export type Observation = { text: string; minute: number; kind: string };
type DemoContext = { selectedId: string; setSelectedId: (id: string) => void; observations: Observation[]; addObservation: (value: Observation) => void };
const Context = createContext<DemoContext | null>(null);
export function DemoProvider({ children }: { children: React.ReactNode }) {
  const [selectedId, setSelectedId] = useState("together");
  const [observations, setObservations] = useState<Observation[]>([]);
  return <Context.Provider value={{ selectedId, setSelectedId, observations, addObservation: value => setObservations(current => [...current, value]) }}>{children}</Context.Provider>;
}
export function useDemo() {
  const context = useContext(Context);
  if (!context) throw new Error("DemoProvider missing");
  return context;
}
