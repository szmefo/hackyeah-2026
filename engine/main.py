"""Transient FIT/CGM API. No persistence, GPS or request-content logging."""
from __future__ import annotations

import hmac
import logging
import os
from typing import Annotated

from fastapi import FastAPI, File, Form, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.formparsers import MultiPartParser

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_REQUEST_BYTES = 4 * 1024 * 1024 + 32 * 1024
# All accepted uploads stay below this spool threshold, so multipart parsing
# cannot roll the original health-data file to a temporary disk file.
MultiPartParser.spool_max_size = MAX_REQUEST_BYTES
# Suppress decoder error details so malformed uploaded health data cannot enter logs.
logging.getLogger("app.services.fit_parser").disabled = True
app = FastAPI(title="Cukier w biegu — transient engine", docs_url=None, redoc_url=None)


def failure(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse({"error": message, "code": code}, status_code=status,
                        headers={"Cache-Control": "no-store"})


@app.middleware("http")
async def protect_engine(request: Request, call_next):
    if request.url.path == "/analyze":
        expected = os.environ.get("ENGINE_SHARED_SECRET", "")
        if not expected:
            return failure(503, "engine_configuration", "Import jest chwilowo niedostępny.")
        supplied = request.headers.get("x-engine-secret", "")
        if not hmac.compare_digest(supplied, expected):
            return failure(403, "forbidden", "Brak dostępu do importu.")
        try:
            length = int(request.headers.get("content-length", "0"))
        except ValueError:
            return failure(400, "request_invalid", "Nieprawidłowe żądanie.")
        if length > MAX_REQUEST_BYTES:
            return failure(413, "file_too_large", "Pliki są zbyt duże. Maksymalnie 2 MB na plik.")
        # Bound the actual stream too, not only the caller-supplied header.
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > MAX_REQUEST_BYTES:
                return failure(413, "file_too_large", "Pliki są zbyt duże. Maksymalnie 2 MB na plik.")
        request._body = bytes(body)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(_request, _exc):
    # FastAPI's usual validation response may echo request bodies; avoid it.
    return failure(422, "missing_files", "Wybierz plik FIT, CSV i potwierdź zgodę na przetwarzanie.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "cukier-w-biegu-engine", "storage": "none"}


@app.post("/analyze")
def analyze(
    fit: Annotated[bytes, File()],
    glucose: Annotated[bytes, File()],
    timezone: Annotated[str, Form()] = "Europe/Warsaw",
    consent: Annotated[str, Form()] = "false",
    synthetic: Annotated[str, Form()] = "false",
):
    if consent != "true":
        return failure(400, "consent_required", "Potwierdź zgodę na przetwarzanie danych z plików.")
    if not fit or not glucose:
        return failure(422, "empty_file", "Plik jest pusty. Wybierz FIT i CSV z odczytami.")
    if max(len(fit), len(glucose)) > MAX_FILE_BYTES:
        return failure(413, "file_too_large", "Maksymalnie 2 MB na plik.")
    if len(timezone) > 64 or synthetic not in {"true", "false"}:
        return failure(400, "invalid_options", "Sprawdź opcje importu.")
    from app.services.analysis import AnalysisError, analyze_upload
    try:
        run = analyze_upload(fit, glucose, timezone_name=timezone, synthetic=synthetic == "true")
        return JSONResponse({"run": run}, headers={"Cache-Control": "no-store"})
    except AnalysisError as exc:
        return failure(422, exc.code, exc.detail_pl)
    except Exception:
        # No parser exception, file bytes or health data escape into logs/client.
        return failure(422, "analysis_failed", "Nie udało się połączyć danych. Sprawdź pliki i strefę czasową.")
