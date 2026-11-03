"""Insurance and medical travel document schemas."""

from schemas.insurance.models import (
    INSURANCE_SCHEMAS,
    InsuranceCertificateSchema,
    InsuranceClaimDetailSchema,
    InsuranceClaimSchema,
    InsuranceDocumentSchema,
    MedicalAssistanceSchema,
    MedicalTravelCertificateSchema,
    TravelInsuranceSchema,
    VaccinationCertificateSchema,
    VaccinationDoseSchema,
)

__all__ = [
    "INSURANCE_SCHEMAS",
    "InsuranceCertificateSchema",
    "InsuranceClaimDetailSchema",
    "InsuranceClaimSchema",
    "InsuranceDocumentSchema",
    "MedicalAssistanceSchema",
    "MedicalTravelCertificateSchema",
    "TravelInsuranceSchema",
    "VaccinationCertificateSchema",
    "VaccinationDoseSchema",
]
