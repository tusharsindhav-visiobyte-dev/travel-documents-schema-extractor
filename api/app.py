"""HTTP API that returns a registered travel document type."""

from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError

from api.classifier import classify_text
from api.config import Settings, load_settings
from api.errors import (
    DocumentInputError,
    ModelUnavailableError,
    UnrecognizedDocumentTypeError,
    UnsupportedFileError,
)
from api.extract import extract_upload

_OPENAPI_REQUEST_BODY = {
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Document text to classify.",
                        }
                    },
                },
                "example": {
                    "text": "E-TICKET\nPassenger name record HX4Q2P\nFlight EX101 London to Delhi",
                },
            },
            "application/x-www-form-urlencoded": {
                "schema": {
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Document text to classify.",
                        }
                    },
                }
            },
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Document text. Used when no file is uploaded.",
                        },
                        "file": {
                            "type": "string",
                            "format": "binary",
                            "description": "A text file or PDF. Used instead of text when both are sent.",
                        },
                    },
                }
            },
        },
    }
}


class TextBody(BaseModel):
    text: str = Field(description="Document text to classify.")


class DocumentTypeResponse(BaseModel):
    document_type: str = Field(
        description="Registered document type identifier, such as flight_ticket or hotel_booking."
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(
        title="Travel Document Type",
        version="1.0.0",
        description=(
            "Classifies pasted text or an uploaded text file or PDF into one "
            "document type from the travel schema registry."
        ),
    )
    app.state.settings = settings or load_settings()

    @app.post(
        "/document-type",
        response_model=DocumentTypeResponse,
        summary="Identify the travel document type",
        description=(
            "Send document text as JSON or as a form field, or upload a text file or PDF. "
            "When a file and text are both present, the file is classified. "
            "The response document_type is one of the registered schema identifiers."
        ),
        responses={
            400: {"description": "No readable text was provided."},
            415: {"description": "The file is not a text file or a PDF."},
            422: {"description": "The model did not return a registered document type."},
            502: {"description": "The language model could not be reached."},
        },
        openapi_extra=_OPENAPI_REQUEST_BODY,
    )
    async def identify_document_type(request: Request) -> DocumentTypeResponse:
        active: Settings = request.app.state.settings
        try:
            text = await _read_input(request, active)
            document_type = await asyncio.to_thread(classify_text, text, active)
        except UnsupportedFileError as exc:
            raise HTTPException(status_code=415, detail=str(exc)) from exc
        except DocumentInputError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except UnrecognizedDocumentTypeError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ModelUnavailableError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return DocumentTypeResponse(document_type=document_type)

    return app


async def _read_input(request: Request, settings: Settings) -> str:
    media = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if media == "application/json":
        return await _text_from_json(request)
    if media in {"multipart/form-data", "application/x-www-form-urlencoded"}:
        return await _text_from_form(request, settings)
    raise DocumentInputError(
        "Send JSON or form data with a text field, or multipart form data with a file."
    )


async def _text_from_json(request: Request) -> str:
    try:
        payload = await request.json()
    except json.JSONDecodeError as exc:
        raise DocumentInputError("Request body must be JSON with a text field.") from exc
    try:
        body = TextBody.model_validate(payload)
    except ValidationError as exc:
        raise DocumentInputError("JSON body must include a text string.") from exc
    if not body.text.strip():
        raise DocumentInputError("Document text is empty.")
    return body.text


async def _text_from_form(request: Request, settings: Settings) -> str:
    form = await request.form()
    upload = form.get("file")
    pasted = form.get("text")
    if upload is not None and hasattr(upload, "read"):
        data = await upload.read()
        if data:
            filename = getattr(upload, "filename", None)
            content_type = getattr(upload, "content_type", None)
            return await asyncio.to_thread(
                extract_upload,
                filename,
                content_type,
                data,
                max_bytes=settings.max_upload_bytes,
            )
    if isinstance(pasted, str) and pasted.strip():
        return pasted
    raise DocumentInputError("Provide a file or text.")


app = create_app()
