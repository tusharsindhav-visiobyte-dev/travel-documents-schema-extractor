"""Corporate travel approvals, invitations, and reimbursement documents."""

from __future__ import annotations

from schemas.base.base_document import (
    BaseDocumentSchema,
    TravelContextSchema,
    declare_document_schema,
)
from schemas.base.base_models import F
from schemas.base.enums import ApprovalStatus
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import LocationSchema
from schemas.common.payment import CurrencySchema, LineItemSchema
from schemas.common.person import PersonSchema
from schemas.common.provider import OrganizationSchema
from schemas.common.traveler import TravelerSchema


class CorporateDocumentSchema(BaseDocumentSchema):
    """A document produced by an employer, host, or conference organizer."""

    company: OrganizationSchema | None = F("Company or organization responsible for the document.")
    employee: TravelerSchema | None = F("Employee or traveler the document concerns.")
    purpose: str | None = F("Purpose as printed.")
    cost_center: str | None = F("Cost center as printed.")
    department: str | None = F("Department as printed.")
    trip: TravelContextSchema | None = F("Trip context when the document describes one.")
    approval_status: ApprovalStatus | None = F("Standardized approval status. Leave null when unmapped.")
    approval_status_original: str | None = F("Approval status exactly as printed.")
    valid_from: DateTimeSchema | None = F("When the document becomes effective.")
    valid_until: DateTimeSchema | None = F("When the document stops being effective.")
    remarks: str | None = F("Remarks.")


_MODULE = __name__


def _corporate(name: str, document_type: str, description: str, **fields: tuple):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=CorporateDocumentSchema,
        description=description,
        module=_MODULE,
        category="corporate",
        fields=fields or None,
    )


CorporateTravelAuthorizationSchema = _corporate(
    "CorporateTravelAuthorizationSchema",
    "corporate_travel_authorization",
    "Authorization for an employee to travel.",
    authorization_number=(str | None, F("Authorization number as printed.")),
    authorized_amount=(CurrencySchema | None, F("Amount the traveler is authorized to spend.")),
    destinations=(list[LocationSchema] | None, F("Destinations covered by the authorization.")),
)

BusinessTripApprovalSchema = _corporate(
    "BusinessTripApprovalSchema",
    "business_trip_approval",
    "An approval decision for a business trip.",
    approver=(PersonSchema | None, F("Person who approved or rejected the trip.")),
    approved_at=(DateTimeSchema | None, F("When the decision was made.")),
    decision=(str | None, F("Decision text exactly as printed.")),
)

BusinessInvitationSchema = _corporate(
    "BusinessInvitationSchema",
    "business_invitation",
    "An invitation from a host organization for a business visit.",
    host_organization=(OrganizationSchema | None, F("Organization issuing the invitation.")),
    invitee=(PersonSchema | None, F("Person invited.")),
    event_name=(str | None, F("Meeting or event name.")),
    event_start=(DateTimeSchema | None, F("Event start.")),
    event_end=(DateTimeSchema | None, F("Event end.")),
    venue=(LocationSchema | None, F("Event venue.")),
)

ConferenceRegistrationSchema = _corporate(
    "ConferenceRegistrationSchema",
    "conference_registration",
    "A conference registration confirmation.",
    conference_name=(str | None, F("Conference name.")),
    registration_number=(str | None, F("Registration number as printed.")),
    venue=(LocationSchema | None, F("Conference venue.")),
    sessions=(list[str] | None, F("Sessions the attendee is registered for.")),
)

ExhibitionPassSchema = _corporate(
    "ExhibitionPassSchema",
    "exhibition_pass",
    "A pass for an exhibition or trade show.",
    exhibition_name=(str | None, F("Exhibition name.")),
    pass_number=(str | None, F("Pass number as printed.")),
    venue=(LocationSchema | None, F("Exhibition venue.")),
)

TravelReimbursementSchema = _corporate(
    "TravelReimbursementSchema",
    "travel_reimbursement",
    "A request or statement for reimbursing travel expenses.",
    expenses=(list[LineItemSchema] | None, F("Expense lines.")),
    claimed_amount=(CurrencySchema | None, F("Amount claimed.")),
    approved_amount=(CurrencySchema | None, F("Amount approved, when stated.")),
)

CORPORATE_SCHEMAS = (
    CorporateTravelAuthorizationSchema,
    BusinessTripApprovalSchema,
    BusinessInvitationSchema,
    ConferenceRegistrationSchema,
    ExhibitionPassSchema,
    TravelReimbursementSchema,
)
