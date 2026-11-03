"""Validation that keeps valid extracted fields when other fields fail."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ValidationError

from validation.business_rules import BusinessFinding, run_business_rules

_DROP = object()


@dataclass(frozen=True)
class ValidationIssue:
    """One schema problem. ``input_value`` is the rejected value."""

    field_path: str
    message: str
    error_type: str
    input_value: Any = None


@dataclass
class ValidationResult:
    """Schema validation outcome.

    ``valid`` means the original payload satisfied the schema. Business
    findings are reported separately and do not delete fields. When the
    payload is invalid, ``preserved_data`` still contains every field that
    did validate, and ``partial_model`` is set when those fields can form
    a model.
    """

    valid: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    business_findings: list[BusinessFinding] = field(default_factory=list)
    model: BaseModel | None = None
    partial_model: BaseModel | None = None
    preserved_data: dict[str, Any] | None = None
    schema_name: str | None = None
    document_type: str | None = None
    schema_version: str | None = None


def generate_json_schema(schema: type[BaseModel]) -> dict[str, Any]:
    """Return the JSON Schema for a Pydantic model."""
    return schema.model_json_schema()


def serialize_model(model: BaseModel, *, exclude_none: bool = False) -> dict[str, Any]:
    """Serialize a model to JSON-compatible values."""
    return model.model_dump(mode="json", exclude_none=exclude_none)


def serialize_model_json(model: BaseModel, *, exclude_none: bool = False) -> str:
    """Serialize a model to a JSON string."""
    return model.model_dump_json(exclude_none=exclude_none)


def validate_model(
    schema: type[BaseModel],
    data: Any,
    *,
    run_rules: bool = True,
) -> ValidationResult:
    """Validate data against a schema and preserve fields that are valid."""
    schema_name = schema.__name__
    document_type = getattr(schema, "DOCUMENT_TYPE", None)
    schema_version = getattr(schema, "SCHEMA_VERSION", None)
    if isinstance(data, schema):
        model = data
        findings = run_business_rules(model) if run_rules else []
        return ValidationResult(
            valid=True,
            model=model,
            partial_model=model,
            preserved_data=serialize_model(model),
            business_findings=findings,
            schema_name=schema_name,
            document_type=document_type,
            schema_version=schema_version,
        )
    if not isinstance(data, dict):
        return ValidationResult(
            valid=False,
            errors=[
                ValidationIssue(
                    field_path="",
                    message=f"Expected an object for {schema_name}.",
                    error_type="model_type",
                    input_value=data,
                )
            ],
            schema_name=schema_name,
            document_type=document_type,
            schema_version=schema_version,
        )
    try:
        model = schema.model_validate(data)
    except ValidationError:
        cleaned, errors, partial = _salvage_model(schema, data)
        preserved = serialize_model(partial) if partial is not None else _jsonable(cleaned)
        findings = run_business_rules(partial) if run_rules and partial is not None else []
        return ValidationResult(
            valid=False,
            errors=errors,
            business_findings=findings,
            partial_model=partial,
            preserved_data=preserved if isinstance(preserved, dict) else None,
            schema_name=schema_name,
            document_type=document_type,
            schema_version=schema_version,
        )
    findings = run_business_rules(model) if run_rules else []
    return ValidationResult(
        valid=True,
        model=model,
        partial_model=model,
        preserved_data=serialize_model(model),
        business_findings=findings,
        errors=[],
        schema_name=schema_name,
        document_type=document_type,
        schema_version=schema_version,
    )


def validate_document(
    document_type: str,
    data: Any,
    *,
    version: str | None = None,
    run_rules: bool = True,
) -> ValidationResult:
    """Validate a payload against the schema registered for ``document_type``."""
    from registry.schema_registry import get_schema

    schema = get_schema(document_type, version=version)
    result = validate_model(schema, data, run_rules=run_rules)
    result.document_type = document_type
    result.schema_version = version or getattr(schema, "SCHEMA_VERSION", result.schema_version)
    return result


def _salvage_model(
    model_type: type[BaseModel],
    value: Any,
) -> tuple[Any, list[ValidationIssue], BaseModel | None]:
    """Drop only invalid leaves and list items, then validate what remains.

    Field validators such as IANA timezone checks run on the model, so a bad
    nested value is removed by its full path. Sibling fields stay in place.
    """
    if isinstance(value, model_type):
        return value.model_dump(), [], value
    if not isinstance(value, dict):
        return _DROP, [
            ValidationIssue(
                field_path="",
                message=f"Expected an object for {model_type.__name__}.",
                error_type="model_type",
                input_value=value,
            )
        ], None

    current = copy.deepcopy(value)
    errors: list[ValidationIssue] = []
    for key in list(current):
        if key not in model_type.model_fields:
            errors.append(
                ValidationIssue(
                    field_path=str(key),
                    message="Extra field is not permitted. Use provider_extensions for provider-specific scalars.",
                    error_type="extra_forbidden",
                    input_value=current.pop(key),
                )
            )

    for _ in range(64):
        try:
            model = model_type.model_validate(current)
            return current, errors, model
        except ValidationError as exc:
            removable = [
                error for error in exc.errors() if error.get("loc") and error.get("type") != "missing"
            ]
            if not removable:
                errors.extend(_issue_from_error(error) for error in exc.errors())
                break
            error = removable[0]
            if not _remove_at(current, tuple(error["loc"])):
                errors.append(_issue_from_error(error))
                break
            errors.append(_issue_from_error(error))
    return current, errors, None


def _remove_at(data: Any, location: tuple[Any, ...]) -> bool:
    if not location:
        return False
    parent = data
    for item in location[:-1]:
        if isinstance(item, int):
            if not isinstance(parent, list) or item >= len(parent):
                return False
            parent = parent[item]
        else:
            if not isinstance(parent, dict) or item not in parent:
                return False
            parent = parent[item]
    last = location[-1]
    if isinstance(last, int):
        if isinstance(parent, list) and 0 <= last < len(parent):
            parent.pop(last)
            return True
        return False
    if isinstance(parent, dict) and last in parent:
        parent.pop(last)
        return True
    return False


def _issue_from_error(error: dict[str, Any]) -> ValidationIssue:
    return ValidationIssue(
        field_path=_format_loc(error.get("loc", ())),
        message=str(error.get("msg", "Invalid value.")),
        error_type=str(error.get("type", "value_error")),
        input_value=error.get("input"),
    )


def _format_loc(location: tuple[Any, ...] | list[Any]) -> str:
    parts: list[str] = []
    for item in location:
        if isinstance(item, int):
            if parts:
                parts[-1] = f"{parts[-1]}[{item}]"
            else:
                parts.append(f"[{item}]")
        else:
            parts.append(str(item))
    return ".".join(parts)


def _jsonable(value: Any) -> Any:
    if value is _DROP or value is None:
        return None
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value
