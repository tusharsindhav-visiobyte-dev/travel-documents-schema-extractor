"""Universal base types for every travel document schema."""

from schemas.base.base_document import (
    CURRENT_SCHEMA_VERSION,
    BaseDocumentSchema,
    TravelContextSchema,
    declare_document_schema,
)
from schemas.base.base_models import DocumentMetadataSchema, SchemaModel
from schemas.base.enums import DocumentStatus, DocumentType
from schemas.common.evidence import ExtractionMetadataSchema

__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "BaseDocumentSchema",
    "DocumentMetadataSchema",
    "DocumentStatus",
    "DocumentType",
    "ExtractionMetadataSchema",
    "SchemaModel",
    "TravelContextSchema",
    "declare_document_schema",
]
