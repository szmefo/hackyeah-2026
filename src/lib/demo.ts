import fixture from "../../data/demo-run.json";

export const demo = fixture;
export type DemoMoment = (typeof demo.moments)[number];
export function momentUnknowns(
  moment: DemoMoment,
  observations: { kind: string }[],
) {
  return moment.unknowns.filter(
    (unknown) =>
      !(
        unknown === "Brak informacji o posiłku." &&
        observations.some((o) => o.kind === "Posiłek")
      ) &&
      !(
        unknown === "Nie zapisano odczuć biegacza." &&
        observations.some((o) => o.kind === "Odczucia")
      ),
  );
}
export const disclaimer =
  "To nie jest porada medyczna. Decyzje o lekach i jedzeniu w cukrzycy podejmuj z lekarzem.";
export const decimal = (value: number) =>
  value.toLocaleString("pl-PL", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 1,
  });
export const paceLabel = (value: number) => {
  const seconds = Math.round(value * 60);
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
};
