"""Schema registry public API."""

from registry.schema_metadata import (
    FieldDescriptor,
    SchemaMetadata,
    field_descriptions,
    optional_field_names,
    required_field_names,
)
from registry.schema_registry import (
    DuplicateSchemaRegistrationError,
    SchemaRegistryError,
    SchemaVersionNotFoundError,
    UnknownDocumentTypeError,
    ensure_builtin_schemas,
    export_json_schema,
    get_schema,
    get_schema_metadata,
    get_schema_version,
    get_schema_versions,
    get_supported_document_types,
    get_supported_document_types_by_category,
    register_schema,
    unregister_schema,
    validate_document_type,
)

__all__ = [
    "DuplicateSchemaRegistrationError",
    "FieldDescriptor",
    "SchemaMetadata",
    "SchemaRegistryError",
    "SchemaVersionNotFoundError",
    "UnknownDocumentTypeError",
    "ensure_builtin_schemas",
    "export_json_schema",
    "field_descriptions",
    "get_schema",
    "get_schema_metadata",
    "get_schema_version",
    "get_schema_versions",
    "get_supported_document_types",
    "get_supported_document_types_by_category",
    "optional_field_names",
    "register_schema",
    "required_field_names",
    "unregister_schema",
    "validate_document_type",
]
