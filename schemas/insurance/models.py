"""Insurance, medical, and vaccination travel documents."""

from __future__ import annotations

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import ClaimStatus
from schemas.common.contact import ContactSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.insurance import InsuranceSchema
from schemas.common.payment import CurrencySchema
from schemas.common.person import PersonSchema
from schemas.common.provider import ProviderSchema


class InsuranceClaimDetailSchema(SchemaModel):
    """A claim described on an insurance document."""

    claim_number: str | None = F("Claim number when it is printed.")
    claim_status: ClaimStatus | None = F("Standardized claim status. Leave null when the wording is unmapped.")
    claim_status_original: str | None = F("Claim status exactly as printed.")
    incident_date: DateTimeSchema | None = F("When the incident happened, when the document says so.")
    claimed_amount: CurrencySchema | None = F("Amount claimed.")
    approved_amount: CurrencySchema | None = F("Amount approved, when stated.")
    description: str | None = F("What the claim is for.")
    original_text: str | None = F("Claim text exactly as printed.")


class VaccinationDoseSchema(SchemaModel):
    """One recorded vaccination dose."""

    vaccine_name: str | None = F("Vaccine name as printed.")
    disease: str | None = F("Disease or target condition as printed.")
    dose_label: str | None = F("Dose label as printed, such as 1 of 2.")
    administration_date: DateTimeSchema | None = F("Date the dose was given.")
    batch_number: str | None = F("Batch or lot number when printed.")
    manufacturer: str | None = F("Manufacturer as printed.")
    provider_name: str | None = F("Clinic or provider that administered the dose.")
    original_text: str | None = F("Dose line exactly as printed.")


class InsuranceDocumentSchema(BaseDocumentSchema):
    """A travel insurance, medical, or assistance document."""

    policy: InsuranceSchema | None = F("Policy or coverage block.")
    insurer: ProviderSchema | None = F("Insurer when named outside the policy block.")
    insured_persons: list[PersonSchema] | None = F("People covered, when listed on the document itself.")
    coverage_start: DateTimeSchema | None = F("Coverage start when printed on the document.")
    coverage_end: DateTimeSchema | None = F("Coverage end when printed on the document.")
    emergency_contact: ContactSchema | None = F("Emergency or assistance contact.")
    remarks: str | None = F("Remarks printed on the insurance document.")


_MODULE = __name__


def _insurance(name: str, document_type: str, description: str, **fields: tuple):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=InsuranceDocumentSchema,
        description=description,
        module=_MODULE,
        category="insurance",
        fields=fields or None,
    )


TravelInsuranceSchema = _insurance(
    "TravelInsuranceSchema",
    "travel_insurance",
    "A travel insurance policy or schedule.",
    covered_trip=(str | None, F("Trip description the policy says it covers.")),
    trip_cost=(CurrencySchema | None, F("Trip cost used by the policy, when an amount is stated.")),
)

InsuranceCertificateSchema = _insurance(
    "InsuranceCertificateSchema",
    "insurance_certificate",
    "A certificate that coverage exists.",
    certificate_number=(str | None, F("Certificate number as printed.")),
    certificate_holder=(str | None, F("Who the certificate says it is issued for.")),
)

InsuranceClaimSchema = _insurance(
    "InsuranceClaimSchema",
    "insurance_claim",
    "A travel insurance claim or claim acknowledgement.",
    claim=(InsuranceClaimDetailSchema | None, F("Claim details.")),
)

MedicalTravelCertificateSchema = _insurance(
    "MedicalTravelCertificateSchema",
    "medical_travel_certificate",
    "A medical certificate related to travel fitness or a medical condition.",
    physician_name=(str | None, F("Physician name as printed.")),
    fitness_statement=(str | None, F("Fitness or medical statement exactly as printed.")),
    restrictions=(list[str] | None, F("Travel restrictions stated on the certificate.")),
)

VaccinationCertificateSchema = _insurance(
    "VaccinationCertificateSchema",
    "vaccination_certificate",
    "A certificate of vaccination for travel.",
    vaccinations=(list[VaccinationDoseSchema] | None, F("Doses recorded on the certificate.")),
    certificate_number=(str | None, F("Certificate number when it is printed.")),
)

MedicalAssistanceSchema = _insurance(
    "MedicalAssistanceSchema",
    "medical_assistance",
    "A medical assistance membership or service document.",
    assistance_provider=(ProviderSchema | None, F("Assistance company.")),
    membership_number=(str | None, F("Membership number when printed.")),
    hotline=(ContactSchema | None, F("Assistance hotline.")),
)

INSURANCE_SCHEMAS = (
    TravelInsuranceSchema,
    InsuranceCertificateSchema,
    InsuranceClaimSchema,
    MedicalTravelCertificateSchema,
    VaccinationCertificateSchema,
    MedicalAssistanceSchema,
)
