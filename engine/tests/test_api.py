"""Independent API guards for transient health-data processing."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette import formparsers

from main import MAX_FILE_BYTES, MAX_REQUEST_BYTES, app

ROOT = Path(__file__).resolve().parents[2]
TEST_SECRET = "qa-test-only-shared-secret"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("ENGINE_SHARED_SECRET", TEST_SECRET)
    with TestClient(app) as connection:
        yield connection


def files():
    return {"fit": ("synthetic.fit", (ROOT / "public" / "demo-run.fit").read_bytes(), "application/octet-stream"),
            "glucose": ("synthetic.csv", (ROOT / "public" / "demo-glucose.csv").read_bytes(), "text/csv")}


def post(client, *, consent="true", supplied=TEST_SECRET, upload=None, **data):
    return client.post("/analyze", files=upload if upload is not None else files(),
                       data={"timezone": "Europe/Warsaw", "consent": consent, **data},
                       headers={"X-Engine-Secret": supplied})


def test_health_is_public_without_echoing_configuration(client):
    response = client.get("/health")
    assert response.status_code == 200 and response.json()["storage"] == "none"
    assert TEST_SECRET not in response.text
    assert response.headers["cache-control"] == "no-store"


def test_missing_engine_configuration_fails_closed(client, monkeypatch):
    monkeypatch.delenv("ENGINE_SHARED_SECRET")
    response = post(client)
    assert response.status_code == 503
    assert response.json()["code"] == "engine_configuration"


@pytest.mark.parametrize("supplied", ["", "wrong-secret"])
def test_private_upload_requires_correct_secret(client, supplied):
    response = post(client, supplied=supplied)
    assert response.status_code == 403
    assert TEST_SECRET not in response.text


@pytest.mark.parametrize("consent", ["false", "", "1", "TRUE"])
def test_literal_consent_required(client, consent):
    response = post(client, consent=consent)
    assert response.status_code == 400
    assert response.json()["code"] == "consent_required"


def test_missing_files_is_safe_structured_failure(client):
    marker = "PERSONAL_HEALTH_DATA_MARKER_123"
    response = client.post("/analyze", data={"consent": "true", "fit": marker},
                           headers={"X-Engine-Secret": TEST_SECRET})
    assert response.status_code == 422
    assert set(response.json()) == {"code", "error"}
    assert marker not in response.text


def test_empty_file_rejected(client):
    upload = files()
    upload["fit"] = ("empty.fit", b"", "application/octet-stream")
    assert post(client, upload=upload).status_code == 422


def test_per_file_size_enforced(client):
    upload = files()
    upload["fit"] = ("large.fit", b"a" * (MAX_FILE_BYTES + 1), "application/octet-stream")
    response = post(client, upload=upload)
    assert response.status_code == 413 and response.json()["code"] == "file_too_large"


def test_actual_total_body_size_bounded_without_content_length(client):
    response = client.post("/analyze", content=b"a" * (MAX_REQUEST_BYTES + 1),
                           headers={"X-Engine-Secret": TEST_SECRET, "Content-Length": "0"})
    assert response.status_code == 413


def test_valid_public_pair_returns_uncached_engine_facts(client):
    response = post(client, synthetic="true")
    assert response.status_code == 200
    run = response.json()["run"]
    assert run["synthetic"] is True and run["provenance"]["engineUsed"] is True
    assert run["facts"]["minGlucose"] == 65
    assert response.headers["cache-control"] == "no-store"


def test_bad_fit_does_not_echo_content_filename_or_decoder_details(client):
    marker = "PERSONAL_HEALTH_DATA_MARKER_123"
    upload = files()
    upload["fit"] = (marker + ".fit", marker.encode(), "application/octet-stream")
    response = post(client, upload=upload)
    assert response.status_code == 422
    assert set(response.json()) == {"code", "error"}
    assert marker not in response.text
    assert "Traceback" not in response.text


def test_multipart_upload_larger_than_default_spool_limit_stays_in_ram(client, monkeypatch):
    # Starlette normally rolls >1 MB to a disk file. Exercise the configured
    # limit using a large invalid FIT: processing must reject it, never persist it.
    created = []
    original = formparsers.SpooledTemporaryFile

    def tracked(*args, **kwargs):
        temporary = original(*args, **kwargs)
        created.append(temporary)
        return temporary

    monkeypatch.setattr(formparsers, "SpooledTemporaryFile", tracked)
    upload = files()
    upload["fit"] = ("invalid.fit", b"x" * (1200 * 1024), "application/octet-stream")
    response = post(client, upload=upload)
    assert response.status_code == 422
    assert created and all(not temporary._rolled for temporary in created)
    assert all(temporary.closed for temporary in created)
