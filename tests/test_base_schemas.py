"""Tests for the universal document schema and evidence metadata."""

from datetime import date

import pytest
from pydantic import ValidationError

from schemas.base.base_document import BaseDocumentSchema
from schemas.base.enums import DocumentStatus, DocumentType
from schemas.common.evidence import DocumentEvidenceSchema
from schemas.flight import FlightTicketSchema


def test_base_document_requires_document_type():
    with pytest.raises(ValidationError) as captured:
        BaseDocumentSchema()
    assert any(error["loc"] == ("document_type",) for error in captured.value.errors())


def test_base_document_accepts_null_optional_fields():
    document = BaseDocumentSchema(
        document_type=DocumentType.FLIGHT_TICKET,
        document_id=None,
        document_subtype=None,
        issuing_organization=None,
        document_reference=None,
        issue_date=None,
        document_status=None,
        language=None,
        travel_context=None,
        traveler_ids=None,
        related_document_ids=None,
        extraction_metadata=None,
        provider_extensions=None,
        original_values=None,
    )
    assert document.schema_version == "1.0.0"
    assert document.language is None


def test_base_document_rejects_unknown_status_and_extra_fields():
    with pytest.raises(ValidationError):
        BaseDocumentSchema(document_type="flight_ticket", document_status="not-a-status")
    with pytest.raises(ValidationError):
        BaseDocumentSchema(document_type="flight_ticket", unexpected=True)


def test_provider_extensions_allow_scalars_and_reject_nested_objects():
    document = BaseDocumentSchema(
        document_type="flight_ticket",
        provider_extensions={"fare_brand_code": "YFLEX", "priority": 1, "domestic": False},
        original_values={"issue_date": "02 Nov 2026"},
    )
    assert document.provider_extensions["fare_brand_code"] == "YFLEX"
    with pytest.raises(ValidationError):
        BaseDocumentSchema(
            document_type="flight_ticket",
            provider_extensions={"nested": {"code": "Y"}},
        )


def test_issue_date_keeps_normalized_value():
    document = BaseDocumentSchema(
        document_type="flight_ticket",
        document_status=DocumentStatus.ISSUED,
        issue_date={"original_date": "2026-11-02", "normalized_date": "2026-11-02", "date_only": True},
    )
    assert document.issue_date.normalized_date == date(2026, 11, 2)


def test_evidence_requires_field_name_and_describes_confidence():
    with pytest.raises(ValidationError):
        DocumentEvidenceSchema()
    evidence = DocumentEvidenceSchema(field_name="pnr", confidence=None, extracted_value=None)
    assert evidence.confidence is None
    description = DocumentEvidenceSchema.model_fields["confidence"].description
    assert description is not None
    assert "not a calibrated probability" in description
    with pytest.raises(ValidationError):
        DocumentEvidenceSchema(field_name="pnr", confidence=1.5)


def test_specialized_schema_fixes_document_type():
    ticket = FlightTicketSchema()
    assert ticket.document_type == "flight_ticket"
    assert ticket.schema_version == "1.0.0"
    with pytest.raises(ValidationError):
        FlightTicketSchema(document_type="hotel_booking")
