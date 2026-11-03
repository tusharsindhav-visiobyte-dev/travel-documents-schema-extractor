"""Descriptions of registered schemas and their fields."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated, Union, get_args, get_origin

from pydantic import BaseModel, Field

from schemas.base.base_models import SchemaModel

try:
    from types import UnionType
except ImportError:  # pragma: no cover - Python 3.11 always provides this
    UnionType = ()  # type: ignore[assignment]


class FieldDescriptor(SchemaModel):
    """One field on a schema, including nested fields."""

    name: str = Field(description="Field name on its own model.")
    path: str = Field(description="Dotted path from the document root. Lists use [].")
    description: str | None = Field(default=None, description="Field description, when the schema defines one.")
    required: bool = Field(description="True when a caller must supply the field.")
    annotation: str = Field(description="Readable type annotation.")
    nullable: bool = Field(description="True when null is an accepted value.")


class SchemaMetadata(SchemaModel):
    """Registry metadata for one document schema version."""

    document_type: str = Field(description="Document type identifier.")
    schema_name: str = Field(description="Python class name.")
    schema_version: str = Field(description="Schema version.")
    description: str | None = Field(default=None, description="What this document schema represents.")
    category: str | None = Field(default=None, description="Document category, such as flight or hotel.")
    required_fields: list[str] = Field(description="Top-level fields the caller must supply.")
    optional_fields: list[str] = Field(description="Top-level fields the caller may omit.")
    field_descriptions: dict[str, str] = Field(description="Descriptions keyed by field path.")
    fields: list[FieldDescriptor] = Field(description="Top-level and nested fields.")


def _annotation_text(annotation: object) -> str:
    if annotation is None or annotation is type(None):
        return "None"
    origin = get_origin(annotation)
    if origin is Annotated:
        return _annotation_text(get_args(annotation)[0])
    if origin in (Union, UnionType):
        return " | ".join(_annotation_text(arg) for arg in get_args(annotation))
    if origin is not None:
        args = ", ".join(_annotation_text(arg) for arg in get_args(annotation))
        origin_name = getattr(origin, "__name__", str(origin)).replace("typing.", "")
        return f"{origin_name}[{args}]"
    return getattr(annotation, "__name__", str(annotation))


def _is_nullable(annotation: object) -> bool:
    origin = get_origin(annotation)
    if origin is Annotated:
        return _is_nullable(get_args(annotation)[0])
    if origin in (Union, UnionType):
        return any(arg is type(None) for arg in get_args(annotation))
    return False


def _nested_models(annotation: object) -> list[tuple[str, type[BaseModel]]]:
    """Return nested models as (path suffix, model type) pairs."""
    origin = get_origin(annotation)
    if origin is Annotated:
        return _nested_models(get_args(annotation)[0])
    if origin in (Union, UnionType):
        found: list[tuple[str, type[BaseModel]]] = []
        for arg in get_args(annotation):
            if arg is type(None):
                continue
            found.extend(_nested_models(arg))
        return found
    if origin in (list,):
        args = get_args(annotation)
        if not args:
            return []
        return [("[]" + suffix, model) for suffix, model in _nested_models(args[0])]
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return [("", annotation)]
    return []


def iter_field_descriptors(
    schema: type[BaseModel],
    *,
    prefix: str = "",
    depth: int = 0,
    stack: tuple[type[BaseModel], ...] = (),
) -> Iterator[FieldDescriptor]:
    """Yield field descriptors, descending into nested models and lists of models."""
    if depth > 8 or schema in stack:
        return
    stack = (*stack, schema)
    for name, field in schema.model_fields.items():
        path = f"{prefix}.{name}" if prefix else name
        description = field.description
        yield FieldDescriptor(
            name=name,
            path=path,
            description=description,
            required=field.is_required(),
            annotation=_annotation_text(field.annotation),
            nullable=_is_nullable(field.annotation),
        )
        for suffix, nested in _nested_models(field.annotation):
            nested_prefix = f"{path}{suffix}"
            yield from iter_field_descriptors(
                nested,
                prefix=nested_prefix,
                depth=depth + 1,
                stack=stack,
            )


def required_field_names(schema: type[BaseModel]) -> list[str]:
    """Return top-level fields that must be supplied."""
    return [name for name, field in schema.model_fields.items() if field.is_required()]


def optional_field_names(schema: type[BaseModel]) -> list[str]:
    """Return top-level fields that may be omitted."""
    return [name for name, field in schema.model_fields.items() if not field.is_required()]


def field_descriptions(schema: type[BaseModel]) -> dict[str, str]:
    """Return descriptions for top-level and nested fields."""
    return {
        item.path: item.description
        for item in iter_field_descriptors(schema)
        if item.description
    }


def build_schema_metadata(
    *,
    document_type: str,
    schema: type[BaseModel],
    version: str,
    description: str | None,
    category: str | None,
) -> SchemaMetadata:
    """Collect registry metadata from a schema class."""
    fields = list(iter_field_descriptors(schema))
    return SchemaMetadata(
        document_type=document_type,
        schema_name=schema.__name__,
        schema_version=version,
        description=description or _clean_doc(schema.__doc__),
        category=category,
        required_fields=required_field_names(schema),
        optional_fields=optional_field_names(schema),
        field_descriptions={item.path: item.description for item in fields if item.description},
        fields=fields,
    )


def _clean_doc(value: str | None) -> str | None:
    if value is None:
        return None
    text = " ".join(value.split())
    return text or None
