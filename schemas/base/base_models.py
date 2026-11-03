"""Shared model configuration and non-cyclic document containers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

ExtensionScalar = str | bool | int | float | None


def F(description: str, default: Any = None, **kwargs: Any) -> Any:
    """Build an optional field with a description."""
    return Field(default=default, description=description, **kwargs)


class SchemaModel(BaseModel):
    """Base model for every schema object in this package.

    Unknown keys are rejected. Provider-specific data belongs in
    ``provider_extensions`` or ``original_values``.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )


class DocumentMetadataSchema(SchemaModel):
    """File and catalog metadata that is not travel business content."""

    title: str | None = F("Human-readable document title when one is known.")
    description: str | None = F("Short description of the document.")
    file_name: str | None = F("Original file name of an uploaded document, when available.")
    media_type: str | None = F("Media type of the uploaded file, such as application/pdf.")
    page_count: int | None = Field(
        default=None,
        ge=0,
        description="Number of pages when the source file reports it.",
    )
    tags: list[str] | None = F("Optional labels supplied with the document.")
    notes: str | None = F("Free-form notes that do not belong on a business field.")
