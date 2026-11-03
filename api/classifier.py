"""Classify document text into a registered schema type."""

from __future__ import annotations

import json
from functools import lru_cache

import httpx

from api.config import Settings
from api.errors import DocumentInputError, ModelUnavailableError, UnrecognizedDocumentTypeError
from registry import get_schema_metadata, get_supported_document_types_by_category, validate_document_type


@lru_cache(maxsize=1)
def _grouped_document_types() -> tuple[tuple[str, tuple[str, ...]], ...]:
    grouped = get_supported_document_types_by_category()
    return tuple((category, tuple(grouped[category])) for category in sorted(grouped))


@lru_cache(maxsize=1)
def document_type_catalog() -> str:
    """One line per registered document type, using the schema description."""
    lines: list[str] = []
    for _category, document_types in _grouped_document_types():
        for document_type in document_types:
            metadata = get_schema_metadata(document_type)
            lines.append(f"- {document_type}: {metadata.description or ''}")
    return "\n".join(lines)


def classify_text(text: str, settings: Settings) -> str:
    """Ask the configured model for one registered document type.

    The model first picks a schema category, then one document type in that
    category. Both answers are constrained to identifiers from the registry.
    """
    document = text.strip()
    if not document:
        raise DocumentInputError("Document text is empty.")
    if len(document) > settings.max_text_chars:
        document = document[: settings.max_text_chars]

    grouped = dict(_grouped_document_types())
    category = _choose(
        settings,
        _category_prompt(document),
        key="category",
        allowed=tuple(grouped),
    )
    if category not in grouped:
        raise UnrecognizedDocumentTypeError(category)

    document_type = _choose(
        settings,
        _type_prompt(category, grouped[category], document),
        key="document_type",
        allowed=grouped[category],
    )
    if not validate_document_type(document_type):
        raise UnrecognizedDocumentTypeError(document_type)
    return document_type


def _category_prompt(document: str) -> str:
    lines = [
        f"- {category}: {', '.join(document_types)}"
        for category, document_types in _grouped_document_types()
    ]
    return (
        "Pick the category whose document types match this travel document.\n"
        "Use the document contents. An airline ticket, PNR, coupon, or boarding pass "
        "is flight. A passport, visa, or residence permit is identity.\n\n"
        + "\n".join(lines)
        + f"\n\nDocument:\n{document}"
    )


def _type_prompt(category: str, document_types: tuple[str, ...], document: str) -> str:
    lines = []
    for document_type in document_types:
        metadata = get_schema_metadata(document_type)
        lines.append(f"- {document_type}: {metadata.description or ''}")
    return (
        f"Choose the single {category} document type that matches this document.\n"
        "Copy the identifier exactly.\n\n"
        + "\n".join(lines)
        + f"\n\nDocument:\n{document}"
    )


def _choose(settings: Settings, prompt: str, *, key: str, allowed: tuple[str, ...]) -> str:
    try:
        response = httpx.post(
            f"{settings.ollama_url}/api/chat",
            json={
                "model": settings.model,
                "stream": False,
                "format": {
                    "type": "object",
                    "properties": {key: {"type": "string", "enum": list(allowed)}},
                    "required": [key],
                },
                "options": {"temperature": 0},
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=settings.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        raise ModelUnavailableError("The language model could not classify the document.") from exc

    message = payload.get("message") if isinstance(payload, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    candidate = _field(content, key)
    normalized = _normalize(candidate)
    if normalized is None or normalized not in allowed:
        raise UnrecognizedDocumentTypeError(candidate)
    return normalized


def _field(content: object, key: str) -> str | None:
    if isinstance(content, dict):
        value = content.get(key)
        return str(value).strip() if value is not None else None
    if not isinstance(content, str) or not content.strip():
        return None
    raw = content.strip()
    if raw.startswith("```"):
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(parsed, dict) and parsed.get(key) is not None:
        return str(parsed[key]).strip()
    return raw


def _normalize(candidate: str | None) -> str | None:
    if not candidate:
        return None
    return candidate.strip().strip("\"'").lower().replace(" ", "_").replace("-", "_")
