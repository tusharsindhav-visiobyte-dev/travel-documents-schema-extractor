"""Evidence attached to extracted fields without polluting business objects."""

from __future__ import annotations

from pydantic import Field, field_validator

from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import ExtractionMethod, VerificationStatus


class SourceLocationSchema(SchemaModel):
    """Where in a source document an extracted value was found."""

    page: int | None = Field(default=None, ge=1, description="1-based page number when the source is paginated.")
    block_id: str | None = F("Stable identifier of a text block, when the extractor provides one.")
    line_start: int | None = Field(default=None, ge=0, description="Inclusive starting line, when known.")
    line_end: int | None = Field(default=None, ge=0, description="Inclusive ending line, when known.")
    char_start: int | None = Field(default=None, ge=0, description="Inclusive character offset, when known.")
    char_end: int | None = Field(default=None, ge=0, description="Exclusive character offset, when known.")
    bounding_box: list[float] | None = F(
        "Optional rectangle as left, top, right, bottom in the extractor's coordinate space."
    )
    original_label: str | None = F("Location description exactly as produced by the extractor.")

    @field_validator("bounding_box")
    @classmethod
    def _bounding_box(cls, value: list[float] | None) -> list[float] | None:
        if value is not None and len(value) != 4:
            raise ValueError("bounding_box must contain exactly four numbers when it is supplied.")
        return value


class DocumentEvidenceSchema(SchemaModel):
    """Evidence for one extracted field.

    Attach evidence through ``extraction_metadata`` on the document.
    ``confidence`` is an extractor-reported score, not a calibrated probability.
    """

    field_name: str = Field(
        ...,
        description="Dotted field path this evidence supports, such as segments[0].flight_number.",
    )
    extracted_value: str | None = F("Value captured for the field, preserved as text.")
    source_text: str | None = F("Surrounding source text used to read the value.")
    source_page: int | None = Field(default=None, ge=1, description="1-based source page.")
    source_location: SourceLocationSchema | None = F("Structured location inside the source document.")
    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Extractor-reported score from 0 to 1 inclusive. "
            "This value is not a calibrated probability and must not be treated as one."
        ),
    )
    extraction_method: ExtractionMethod | None = F("How the value was obtained.")
    verification_status: VerificationStatus | None = F("Whether a person or process has checked the value.")
    notes: str | None = F("Reviewer or extractor notes for this evidence item.")


class ExtractionMetadataSchema(SchemaModel):
    """Extractor bookkeeping for a document. This is not travel business data."""

    extracted_at: str | None = F(
        "Timestamp string supplied by the extractor. It is stored as given and is not completed."
    )
    extractor_name: str | None = F("Name of the extractor or importer that produced the record.")
    extractor_version: str | None = F("Version of the extractor or importer.")
    evidence: list[DocumentEvidenceSchema] | None = F(
        "Evidence items for important fields. Ordinary business objects do not embed this metadata."
    )
    warnings: list[str] | None = F("Extractor warnings that should travel with the document.")
    source_pages: list[int] | None = F("Pages consulted while reading the document.")
