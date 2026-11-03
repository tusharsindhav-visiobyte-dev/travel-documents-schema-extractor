"""Universal base schema inherited by every travel document."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, create_model

from schemas.base.base_models import DocumentMetadataSchema, ExtensionScalar, F, SchemaModel
from schemas.base.enums import DocumentStatus, DocumentType
from schemas.common.datetime import DateTimeSchema
from schemas.common.evidence import ExtractionMetadataSchema
from schemas.common.location import LocationSchema
from schemas.common.provider import OrganizationSchema

CURRENT_SCHEMA_VERSION = "1.0.0"


class TravelContextSchema(SchemaModel):
    """Trip context linked to a document.

    Origin and destination are independent places. Their timezones are not
    assumed to match, and missing times are left empty.
    """

    trip_id: str | None = F("Identifier of the trip this document belongs to.")
    trip_name: str | None = F("Trip name as shown or assigned.")
    purpose: str | None = F("Travel purpose when stated, such as leisure or business.")
    purpose_original: str | None = F("Purpose wording exactly as printed when it is not normalized.")
    origin: LocationSchema | None = F("Trip origin when the document names one.")
    destination: LocationSchema | None = F("Trip destination when the document names one.")
    trip_start: DateTimeSchema | None = F("Trip start. A missing clock time stays missing.")
    trip_end: DateTimeSchema | None = F("Trip end. A missing clock time stays missing.")
    international: bool | None = F(
        "True or false only when the document or an upstream decision establishes it."
    )
    group_name: str | None = F("Travelling group name when the document names one.")
    traveler_count: int | None = Field(
        default=None,
        ge=0,
        description="Traveler count only when the document states one.",
    )


class BaseDocumentSchema(SchemaModel):
    """Metadata shared by every travel document.

    Specialized schemas override ``document_type`` with their own identifier.
    Business fields stay optional because a source document may omit them.
    """

    document_id: str | None = F("Stable identifier assigned by the owning application.")
    document_type: DocumentType = Field(
        ...,
        description="Document type identifier. Specialized schemas fix this to one value.",
    )
    document_subtype: str | None = F("Finer document label, such as e_ticket or paper_ticket.")
    schema_version: Literal["1.0.0"] = Field(
        default=CURRENT_SCHEMA_VERSION,
        description="Schema version of this document record.",
    )
    document_metadata: DocumentMetadataSchema | None = F("File and catalog metadata.")
    issuing_organization: OrganizationSchema | None = F("Organization that issued the document.")
    document_reference: str | None = F(
        "Primary reference printed on the document, such as a ticket, voucher, or policy number."
    )
    issue_date: DateTimeSchema | None = F("Issue date and time as printed and, when unambiguous, normalized.")
    document_status: DocumentStatus | None = F("Standardized document status. Leave null when unmapped.")
    language: str | None = F("Document language as a BCP 47 tag when it is known.")
    travel_context: TravelContextSchema | None = F("Trip context associated with this document.")
    traveler_ids: list[str] | None = F("Identifiers of travelers this document mentions.")
    related_document_ids: list[str] | None = F("Identifiers of related documents in the same trip.")
    extraction_metadata: ExtractionMetadataSchema | None = F(
        "Extraction evidence and warnings. This does not replace business fields."
    )
    provider_extensions: dict[str, ExtensionScalar] | None = F(
        "Provider-specific scalars. Values may be strings, booleans, numbers, or null. Nested objects are rejected."
    )
    original_values: dict[str, str] | None = F(
        "Original extracted text for fields whose normalized form is ambiguous or incomplete."
    )


def declare_document_schema(
    class_name: str,
    *,
    document_type: str,
    base: type[BaseDocumentSchema],
    description: str,
    module: str,
    category: str,
    fields: dict[str, Any] | None = None,
) -> type[BaseDocumentSchema]:
    """Create a dedicated document schema with a fixed document type."""
    definitions: dict[str, Any] = dict(fields or {})
    definitions["document_type"] = (
        Literal[document_type],
        Field(
            default=document_type,
            description=f"Document type identifier '{document_type}'.",
        ),
    )
    model = create_model(
        class_name,
        __base__=base,
        __module__=module,
        __doc__=description,
        **definitions,
    )
    model.DOCUMENT_TYPE = document_type
    model.SCHEMA_VERSION = CURRENT_SCHEMA_VERSION
    model.SCHEMA_DESCRIPTION = description
    model.SCHEMA_CATEGORY = category
    return model
