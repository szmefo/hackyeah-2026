import type { CSSProperties } from "react";

export type IconName =
  | "arrow"
  | "back"
  | "file"
  | "eye"
  | "question"
  | "chat"
  | "hill"
  | "drop"
  | "pen"
  | "close"
  | "check"
  | "clock"
  | "location"
  | "upload";
const paths: Record<IconName, React.ReactNode> = {
  arrow: (
    <>
      <path d="M4 12h15M13 6l6 6-6 6" />
    </>
  ),
  back: (
    <>
      <path d="M20 12H5m6-6-6 6 6 6" />
    </>
  ),
  file: (
    <>
      <path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6m-6 4h6" />
    </>
  ),
  eye: (
    <>
      <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z" />
      <circle cx="12" cy="12" r="3" />
    </>
  ),
  question: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 4m0 3h.01" />
    </>
  ),
  chat: (
    <>
      <path d="M21 11a8 8 0 0 1-8 8H5l-3 3V11a9 9 0 0 1 19 0zM7 9h10M7 13h6" />
    </>
  ),
  hill: (
    <>
      <path d="m2 20 7-14 5 9 3-6 5 11z" />
      <path d="m7 10 2 2 2-2" />
    </>
  ),
  drop: <path d="M12 2S5 11 5 15a7 7 0 0 0 14 0c0-4-7-13-7-13z" />,
  pen: (
    <>
      <path d="m4 16 12-12 4 4L8 20H4zM14 6l4 4" />
    </>
  ),
  close: <path d="m6 6 12 12M6 18 18 6" />,
  check: <path d="m5 12 4 4L19 6" />,
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 6v6l4 2" />
    </>
  ),
  location: (
    <>
      <path d="M19 10c0 6-7 12-7 12S5 16 5 10a7 7 0 1 1 14 0z" />
      <circle cx="12" cy="10" r="2" />
    </>
  ),
  upload: (
    <>
      <path d="M12 16V3m-5 5 5-5 5 5M4 16v5h16v-5" />
    </>
  ),
};
export function Icon({
  name,
  size = 20,
  style,
}: {
  name: IconName;
  size?: number;
  style?: CSSProperties;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={style}
    >
      {paths[name]}
    </svg>
  );
}
export function Logo() {
  return (
    <svg
      width="50"
      height="28"
      viewBox="0 0 50 28"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M1 19C9 19 12 4 19 6S28 26 35 22 43 12 49 12"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}
