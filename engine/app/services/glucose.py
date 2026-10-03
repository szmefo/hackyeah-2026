"""Transient Dexcom-style EGV CSV parsing. No patient metadata leaves this module."""

from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class GlucoseParseError(ValueError):
    def __init__(self, code: str, detail_pl: str) -> None:
        super().__init__(code)
        self.code = code
        self.detail_pl = detail_pl


@dataclass(frozen=True)
class GlucoseReading:
    timestamp: datetime
    value: float | None
    flag: str | None = None
    source_unit: str = "mg/dL"


def resolve_timezone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise GlucoseParseError(
            "invalid_timezone", "Wybierz poprawną strefę czasową, np. Europe/Warsaw."
        ) from exc


def _timestamp(raw: str, zone: ZoneInfo) -> datetime:
    if not re.match(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", raw.strip()):
        raise GlucoseParseError(
            "invalid_timestamp", "CSV musi zawierać pełną datę i godzinę YYYY-MM-DDThh:mm:ss."
        )
    try:
        parsed = datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise GlucoseParseError(
            "invalid_timestamp", "CSV musi zawierać daty w formacie YYYY-MM-DDThh:mm:ss."
        ) from exc
    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc)
    # Round trips distinguish nonexistent spring times and repeated autumn times.
    candidates = []
    for fold in (0, 1):
        aware = parsed.replace(tzinfo=zone, fold=fold)
        utc = aware.astimezone(timezone.utc)
        if utc.astimezone(zone).replace(tzinfo=None) == parsed and utc not in candidates:
            candidates.append(utc)
    if not candidates:
        raise GlucoseParseError(
            "nonexistent_local_time",
            "CSV zawiera godzinę nieistniejącą podczas zmiany czasu. Podaj daty z przesunięciem UTC.",
        )
    if len(candidates) > 1:
        raise GlucoseParseError(
            "ambiguous_local_time",
            "CSV zawiera powtórzoną godzinę podczas zmiany czasu. Podaj daty z przesunięciem UTC.",
        )
    return candidates[0]


def parse_glucose_csv(content: bytes, timezone_name: str = "Europe/Warsaw") -> list[GlucoseReading]:
    """Read EGV only; deduplicate equal readings and reject contradictory timestamps.

    Accepts UTF-8 or BOM-labelled UTF-16, comma/semicolon/tab delimiters, and
    Dexcom metadata preceding the actual header. Numeric mmol/L is converted
    to mg/dL with the declared conversion factor 18.0182. Low/High remain flags.
    """
    zone = resolve_timezone(timezone_name)
    if not content or len(content) > 2 * 1024 * 1024:
        raise GlucoseParseError("csv_size", "CSV musi być niepusty i mieć najwyżej 2 MB.")
    try:
        encoding = "utf-16" if content.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
        text = content.decode(encoding)
    except UnicodeError as exc:
        raise GlucoseParseError("csv_encoding", "Zapisz CSV jako UTF-8 i spróbuj ponownie.") from exc
    if "\x00" in text:
        raise GlucoseParseError("csv_encoding", "Zapisz CSV jako UTF-8 i spróbuj ponownie.")
    lines = text.splitlines()
    header_index = next(
        (i for i, line in enumerate(lines[:100]) if "timestamp" in line.lower() and "glucose" in line.lower()),
        None,
    )
    if header_index is None:
        raise GlucoseParseError(
            "csv_header", "Brak kolumn Timestamp, Event Type i Glucose Value. Użyj eksportu Dexcom Clarity."
        )
    header = lines[header_index]
    delimiter = max((",", ";", "\t"), key=header.count)
    try:
        rows = csv.reader(StringIO("\n".join(lines[header_index:])), delimiter=delimiter, strict=True)
        fields = [field.strip().lower() for field in next(rows)]
        time_index = next(i for i, field in enumerate(fields) if field.startswith("timestamp"))
        event_index = fields.index("event type")
        value_index = next(i for i, field in enumerate(fields) if field.startswith("glucose value"))
        value_header = fields[value_index]
        if "mg/dl" in value_header:
            source_unit, multiplier = "mg/dL", 1.0
        elif "mmol/l" in value_header:
            source_unit, multiplier = "mmol/L", 18.0182
        else:
            raise GlucoseParseError("glucose_unit", "Kolumna glukozy musi podawać jednostkę mg/dL lub mmol/L.")
        readings: dict[datetime, GlucoseReading] = {}
        for row_number, row in enumerate(rows, 1):
            if row_number > 100_000:
                raise GlucoseParseError("csv_rows", "CSV jest zbyt długi. Wyeksportuj krótszy okres.")
            if not row or not any(field.strip() for field in row):
                continue
            if len(row) <= event_index:
                raise GlucoseParseError("csv_row", "CSV zawiera niepełny wiersz. Wyeksportuj plik ponownie.")
            if row[event_index].strip().upper() != "EGV":
                continue
            if len(row) <= max(time_index, value_index):
                raise GlucoseParseError("csv_row", "CSV zawiera niepełny odczyt EGV.")
            timestamp = _timestamp(row[time_index], zone)
            raw = row[value_index].strip()
            flag = {"low": "below_range", "high": "above_range"}.get(raw.lower())
            value = None
            if flag is None:
                try:
                    value = float(raw.replace(",", ".")) * multiplier
                except ValueError as exc:
                    raise GlucoseParseError("invalid_glucose", "Odczyt EGV musi być liczbą albo flagą Low/High.") from exc
                if not math.isfinite(value) or value <= 0 or value > 2000:
                    raise GlucoseParseError("invalid_glucose", "CSV zawiera nieprawidłową wartość glukozy.")
                value = round(value, 4)
            reading = GlucoseReading(timestamp, value, flag, source_unit)
            previous = readings.get(timestamp)
            if previous is not None and (previous.value != reading.value or previous.flag != reading.flag):
                raise GlucoseParseError(
                    "conflicting_readings", "Dla jednej godziny CSV zawiera różne odczyty. Sprawdź eksport."
                )
            readings[timestamp] = reading
            if len(readings) > 50_000:
                raise GlucoseParseError("csv_readings", "Zbyt wiele odczytów EGV. Wyeksportuj krótszy okres.")
    except (csv.Error, StopIteration, ValueError) as exc:
        if isinstance(exc, GlucoseParseError):
            raise
        raise GlucoseParseError("csv_header", "Nie można odczytać struktury CSV. Użyj eksportu Dexcom Clarity.") from exc
    if not readings:
        raise GlucoseParseError("no_egv", "CSV nie zawiera odczytów glukozy typu EGV.")
    return sorted(readings.values(), key=lambda reading: reading.timestamp)
