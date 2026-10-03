"""Create a GPS-free synthetic FIT paired with demo-glucose.csv.

This fixture generator was authored during HackYeah 2026. All measurements come
from this repository's synthetic demo-run.json; no athlete/device identity or
UltraSoul fixture implementation is copied into the generated artifact.
Run with engine/.venv's Python from any directory.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from garmin_fit_sdk import Profile
from garmin_fit_sdk.encoder import Encoder

ROOT = Path(__file__).resolve().parents[1]


def build_fit(story: dict, *, sport: str = "running", timestamps: bool = True,
              omit_timestamp_minutes: set[int] | None = None) -> bytes:
    """Encode synthetic sampled measurements, with no GPS or serial number."""
    start = datetime.fromisoformat(story["start"]).astimezone(timezone.utc)
    duration = float(story["durationMinutes"]) * 60
    encoder = Encoder()
    numbers = Profile["mesg_num"]
    encoder.write_mesg({
        "mesg_num": numbers["FILE_ID"], "type": "activity",
        "manufacturer": "development", "time_created": start,
        "product_name": "HackYeah synthetic fixture",
    })
    for sample in story["samples"]:
        record = {"mesg_num": numbers["RECORD"]}
        if timestamps and sample["minute"] not in (omit_timestamp_minutes or set()):
            record["timestamp"] = start + timedelta(minutes=sample["minute"])
        fields = {"hr": "heart_rate", "altitude": "enhanced_altitude"}
        for source, target in fields.items():
            if sample.get(source) is not None:
                record[target] = sample[source]
        if sample.get("pace") is not None and sample["pace"] > 0:
            record["enhanced_speed"] = 1000 / (60 * sample["pace"])
        if sample.get("distanceKm") is not None:
            record["distance"] = sample["distanceKm"] * 1000
        encoder.write_mesg(record)
    session = {
        "mesg_num": numbers["SESSION"], "sport": sport,
        "sub_sport": "generic", "start_time": start,
        "timestamp": start + timedelta(seconds=duration),
        "total_elapsed_time": duration, "total_timer_time": duration,
    }
    if story.get("distanceKm") is not None:
        session["total_distance"] = story["distanceKm"] * 1000
    encoder.write_mesg(session)
    return encoder.close()


if __name__ == "__main__":
    story = json.loads((ROOT / "data" / "demo-run.json").read_text(encoding="utf-8"))
    destination = ROOT / "public" / "demo-run.fit"
    destination.write_bytes(build_fit(story))
    print(f"Generated synthetic FIT: {destination.name} ({destination.stat().st_size} bytes)")
