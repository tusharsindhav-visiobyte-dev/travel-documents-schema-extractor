"""Validation, JSON serialization, and business-rule hooks."""

from validation.business_rules import (
    BusinessFinding,
    BusinessRule,
    register_business_rule,
    reset_custom_business_rules,
    run_business_rules,
)
from validation.schema_validator import (
    ValidationIssue,
    ValidationResult,
    generate_json_schema,
    serialize_model,
    serialize_model_json,
    validate_document,
    validate_model,
)

__all__ = [
    "BusinessFinding",
    "BusinessRule",
    "ValidationIssue",
    "ValidationResult",
    "generate_json_schema",
    "register_business_rule",
    "reset_custom_business_rules",
    "run_business_rules",
    "serialize_model",
    "serialize_model_json",
    "validate_document",
    "validate_model",
]
