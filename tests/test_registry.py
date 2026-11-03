"""Tests for the schema registry."""

import pytest
from pydantic import Field

from registry.schema_registry import (
    DuplicateSchemaRegistrationError,
    SchemaVersionNotFoundError,
    UnknownDocumentTypeError,
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
from registry.schema_metadata import optional_field_names, required_field_names
from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.enums import DocumentType
from schemas.catalog import ALL_DOCUMENT_SCHEMAS
from schemas.common.evidence import DocumentEvidenceSchema
from schemas.flight import FlightTicketSchema


def test_registry_matches_the_document_type_enum():
    enum_values = {item.value for item in DocumentType}
    registered = get_supported_document_types()
    declared = [schema.DOCUMENT_TYPE for schema in ALL_DOCUMENT_SCHEMAS]
    assert len(declared) == len(set(declared)) == 98
    assert set(declared) == enum_values
    assert registered == sorted(enum_values)


def test_lookup_version_and_metadata():
    schema = get_schema("flight_ticket")
    assert schema is FlightTicketSchema
    assert get_schema_version("flight_ticket") == "1.0.0"
    assert get_schema_versions("flight_ticket") == ["1.0.0"]
    metadata = get_schema_metadata("flight_ticket")
    assert metadata.schema_name == "FlightTicketSchema"
    assert metadata.category == "flight"
    assert metadata.description
    assert "pnr" in metadata.optional_fields
    assert "document_type" not in metadata.required_fields
    assert "Passenger name record" in metadata.field_descriptions["pnr"]
    assert "segments[].flight_number" in metadata.field_descriptions
    assert validate_document_type("flight_ticket") is True
    assert validate_document_type("not_a_document") is False
    assert validate_document_type(None) is False


def test_unknown_document_type_has_a_clear_error():
    with pytest.raises(UnknownDocumentTypeError) as captured:
        get_schema("space_ticket")
    assert "space_ticket" in str(captured.value)
    assert "get_supported_document_types" in str(captured.value)
    with pytest.raises(SchemaVersionNotFoundError):
        get_schema("flight_ticket", version="9.9.9")


def test_categories_cover_every_registered_type():
    grouped = get_supported_document_types_by_category()
    flattened = [item for values in grouped.values() for item in values]
    assert set(flattened) == set(get_supported_document_types())
    assert "flight_ticket" in grouped["flight"]
    assert "hotel_booking" in grouped["hotel"]
    assert "passport" in grouped["identity"]


def test_duplicate_registration_requires_override_and_can_be_removed():
    with pytest.raises(DuplicateSchemaRegistrationError):
        register_schema("flight_ticket", FlightTicketSchema, version="1.0.0")

    replacement = declare_document_schema(
        "FlightTicketSchemaV11",
        document_type="flight_ticket",
        base=FlightTicketSchema,
        description="Test replacement for version 1.1.0.",
        module=__name__,
        category="flight",
        fields={"upgrade_note": (str | None, Field(default=None, description="Test-only note."))},
    )
    register_schema("flight_ticket", replacement, version="1.1.0", override=False)
    try:
        assert get_schema_version("flight_ticket") == "1.1.0"
        assert get_schema("flight_ticket", version="1.0.0") is FlightTicketSchema
        with pytest.raises(DuplicateSchemaRegistrationError):
            register_schema("flight_ticket", replacement, version="1.1.0")
        register_schema(
            "flight_ticket",
            replacement,
            version="1.1.0",
            description="Replaced test schema.",
            override=True,
        )
        assert get_schema_metadata("flight_ticket", version="1.1.0").description == "Replaced test schema."
    finally:
        unregister_schema("flight_ticket", version="1.1.0")
    assert get_schema_version("flight_ticket") == "1.0.0"


def test_custom_schema_registration_and_json_schema_export():
    custom = declare_document_schema(
        "BalloonRideTicketSchema",
        document_type="balloon_ride_ticket",
        base=BaseDocumentSchema,
        description="A ticket for a balloon ride.",
        module=__name__,
        category="activities",
        fields={"launch_site": (str | None, Field(default=None, description="Where the balloon launches."))},
    )
    register_schema("balloon_ride_ticket", custom, description="A ticket for a balloon ride.")
    try:
        assert validate_document_type("balloon_ride_ticket") is True
        assert get_schema("balloon_ride_ticket") is custom
        exported = export_json_schema("balloon_ride_ticket")
        assert exported["properties"]["document_type"]["const"] == "balloon_ride_ticket"
        assert "launch_site" in exported["properties"]
    finally:
        unregister_schema("balloon_ride_ticket")
    assert validate_document_type("balloon_ride_ticket") is False


def test_base_metadata_lists_document_type_as_required():
    assert "document_type" in required_field_names(BaseDocumentSchema)
    assert "language" in optional_field_names(BaseDocumentSchema)
    assert "field_name" in required_field_names(DocumentEvidenceSchema)
