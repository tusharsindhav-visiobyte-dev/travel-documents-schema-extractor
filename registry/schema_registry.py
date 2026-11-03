"""Central registry of travel document schemas."""

from __future__ import annotations

from threading import RLock
from typing import Any

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from registry.schema_metadata import SchemaMetadata, build_schema_metadata
from schemas.base.base_document import BaseDocumentSchema


class SchemaRegistryError(Exception):
    """Base error for schema registration and lookup."""


class UnknownDocumentTypeError(SchemaRegistryError):
    """Raised when a document type has not been registered."""

    def __init__(self, document_type: str) -> None:
        self.document_type = document_type
        super().__init__(
            f"Unknown document type '{document_type}'. "
            "Call get_supported_document_types() for registered identifiers."
        )


class DuplicateSchemaRegistrationError(SchemaRegistryError):
    """Raised when a document type and version are registered twice."""

    def __init__(self, document_type: str, version: str) -> None:
        self.document_type = document_type
        self.version = version
        super().__init__(
            f"Schema '{document_type}' version '{version}' is already registered. "
            "Pass override=True to replace it."
        )


class SchemaVersionNotFoundError(SchemaRegistryError):
    """Raised when a document type exists but the requested version does not."""

    def __init__(self, document_type: str, version: str) -> None:
        self.document_type = document_type
        self.version = version
        super().__init__(
            f"Document type '{document_type}' has no registered schema version '{version}'."
        )


class _Registration:
    def __init__(
        self,
        *,
        document_type: str,
        version: str,
        schema: type[BaseDocumentSchema],
        description: str | None,
        category: str | None,
    ) -> None:
        self.document_type = document_type
        self.version = version
        self.schema = schema
        self.description = description
        self.category = category


_LOCK = RLock()
_REGISTRY: dict[str, dict[str, _Registration]] = {}
_BUILTINS_READY = False
_REGISTERING_BUILTINS = False


def _version_key(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in version.split("."):
        digits = ""
        for character in piece:
            if character.isdigit():
                digits += character
            else:
                break
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _schema_version(schema: type[BaseModel], explicit: str | None) -> str:
    if explicit:
        return explicit
    class_version = getattr(schema, "SCHEMA_VERSION", None)
    if isinstance(class_version, str) and class_version:
        return class_version
    field = schema.model_fields.get("schema_version")
    if field is not None and field.default is not PydanticUndefined and field.default is not None:
        return str(field.default)
    return "1.0.0"


def _schema_description(schema: type[BaseModel], explicit: str | None) -> str | None:
    if explicit:
        return explicit
    description = getattr(schema, "SCHEMA_DESCRIPTION", None)
    if isinstance(description, str) and description:
        return description
    if schema.__doc__:
        return " ".join(schema.__doc__.split())
    return None


def _declared_document_type(schema: type[BaseModel]) -> str | None:
    declared = getattr(schema, "DOCUMENT_TYPE", None)
    if isinstance(declared, str) and declared:
        return declared
    field = schema.model_fields.get("document_type")
    if field is None or field.default is PydanticUndefined:
        return None
    default = field.default
    value = getattr(default, "value", default)
    return str(value) if value is not None else None


def ensure_builtin_schemas() -> None:
    """Register every built-in document schema once."""
    global _BUILTINS_READY, _REGISTERING_BUILTINS
    if _BUILTINS_READY or _REGISTERING_BUILTINS:
        return
    with _LOCK:
        if _BUILTINS_READY or _REGISTERING_BUILTINS:
            return
        _REGISTERING_BUILTINS = True
        try:
            from schemas.catalog import iter_builtin_schemas

            for schema in iter_builtin_schemas():
                document_type = _declared_document_type(schema)
                if document_type is None:
                    raise SchemaRegistryError(
                        f"{schema.__name__} does not declare a document type."
                    )
                _register(
                    document_type,
                    schema,
                    version=_schema_version(schema, None),
                    description=_schema_description(schema, None),
                    override=False,
                )
        finally:
            _REGISTERING_BUILTINS = False
            _BUILTINS_READY = True


def _register(
    document_type: str,
    schema: type[BaseDocumentSchema],
    *,
    version: str,
    description: str | None,
    override: bool,
) -> None:
    if not isinstance(document_type, str) or not document_type.strip():
        raise SchemaRegistryError("document_type must be a non-empty string.")
    if not isinstance(schema, type) or not issubclass(schema, BaseDocumentSchema):
        raise SchemaRegistryError(
            "Only subclasses of BaseDocumentSchema can be registered as document schemas."
        )
    declared = _declared_document_type(schema)
    if declared is not None and declared != document_type:
        raise SchemaRegistryError(
            f"{schema.__name__} declares document type '{declared}', not '{document_type}'."
        )
    category = getattr(schema, "SCHEMA_CATEGORY", None)
    versions = _REGISTRY.setdefault(document_type, {})
    if version in versions and not override:
        raise DuplicateSchemaRegistrationError(document_type, version)
    versions[version] = _Registration(
        document_type=document_type,
        version=version,
        schema=schema,
        description=description,
        category=category if isinstance(category, str) else None,
    )


def register_schema(
    document_type: str,
    schema: type[BaseDocumentSchema],
    *,
    version: str | None = None,
    description: str | None = None,
    override: bool = False,
) -> None:
    """Register a document schema.

    Registering the same document type and version twice raises
    ``DuplicateSchemaRegistrationError`` unless ``override`` is true.
    """
    if not _REGISTERING_BUILTINS:
        ensure_builtin_schemas()
    resolved_version = _schema_version(schema, version)
    resolved_description = _schema_description(schema, description)
    with _LOCK:
        _register(
            document_type,
            schema,
            version=resolved_version,
            description=resolved_description,
            override=override,
        )


def unregister_schema(document_type: str, version: str | None = None) -> None:
    """Remove a registration. Built-in schemas can be restored with ``override``."""
    ensure_builtin_schemas()
    with _LOCK:
        versions = _REGISTRY.get(document_type)
        if not versions:
            raise UnknownDocumentTypeError(document_type)
        if version is None:
            _REGISTRY.pop(document_type, None)
            return
        if version not in versions:
            raise SchemaVersionNotFoundError(document_type, version)
        versions.pop(version)
        if not versions:
            _REGISTRY.pop(document_type, None)


def _latest(document_type: str) -> _Registration:
    ensure_builtin_schemas()
    versions = _REGISTRY.get(document_type)
    if not versions:
        raise UnknownDocumentTypeError(document_type)
    latest = max(versions, key=_version_key)
    return versions[latest]


def _exact(document_type: str, version: str | None) -> _Registration:
    if version is None:
        return _latest(document_type)
    ensure_builtin_schemas()
    versions = _REGISTRY.get(document_type)
    if not versions:
        raise UnknownDocumentTypeError(document_type)
    found = versions.get(version)
    if found is None:
        raise SchemaVersionNotFoundError(document_type, version)
    return found


def get_schema(document_type: str, version: str | None = None) -> type[BaseDocumentSchema]:
    """Return the schema class for a document type."""
    return _exact(document_type, version).schema


def get_supported_document_types() -> list[str]:
    """Return registered document type identifiers in sorted order."""
    ensure_builtin_schemas()
    return sorted(_REGISTRY)


def get_supported_document_types_by_category() -> dict[str, list[str]]:
    """Return document types grouped by category."""
    ensure_builtin_schemas()
    grouped: dict[str, list[str]] = {}
    for document_type in sorted(_REGISTRY):
        registration = _latest(document_type)
        category = registration.category or "uncategorized"
        grouped.setdefault(category, []).append(document_type)
    return grouped


def get_schema_version(document_type: str) -> str:
    """Return the latest registered version of a document type."""
    return _latest(document_type).version


def get_schema_versions(document_type: str) -> list[str]:
    """Return every registered version of a document type, oldest first."""
    ensure_builtin_schemas()
    versions = _REGISTRY.get(document_type)
    if not versions:
        raise UnknownDocumentTypeError(document_type)
    return sorted(versions, key=_version_key)


def validate_document_type(document_type: str) -> bool:
    """Return whether a document type identifier is registered."""
    if not isinstance(document_type, str):
        return False
    ensure_builtin_schemas()
    return document_type in _REGISTRY


def get_schema_metadata(document_type: str, version: str | None = None) -> SchemaMetadata:
    """Return descriptions, versions, and required and optional fields."""
    registration = _exact(document_type, version)
    return build_schema_metadata(
        document_type=registration.document_type,
        schema=registration.schema,
        version=registration.version,
        description=registration.description,
        category=registration.category,
    )


def export_json_schema(document_type: str, version: str | None = None) -> dict[str, Any]:
    """Generate a JSON Schema document for a registered document type."""
    return get_schema(document_type, version=version).model_json_schema()
