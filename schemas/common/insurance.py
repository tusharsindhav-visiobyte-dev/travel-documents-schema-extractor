"""Insurance coverage shared by policies, certificates, and rental agreements."""

from __future__ import annotations

from schemas.base.base_models import F, SchemaModel
from schemas.common.contact import ContactSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.payment import CurrencySchema
from schemas.common.person import PersonSchema
from schemas.common.provider import ProviderSchema


class CoverageDetailSchema(SchemaModel):
    """One coverage benefit or limit."""

    coverage_type: str | None = F("Coverage type as printed, such as medical or baggage delay.")
    description: str | None = F("What this coverage includes.")
    limit: CurrencySchema | None = F("Coverage limit when an amount is stated.")
    deductible: CurrencySchema | None = F("Deductible or excess when an amount is stated.")
    original_text: str | None = F("Coverage sentence exactly as printed.")


class InsuranceSchema(SchemaModel):
    """A policy or coverage block that other documents can embed."""

    policy_number: str | None = F("Policy number when it is printed.")
    certificate_number: str | None = F("Certificate number when it is printed.")
    insurer: ProviderSchema | None = F("Insurer or coverage provider.")
    product_name: str | None = F("Insurance product name as printed.")
    coverage_start: DateTimeSchema | None = F("When coverage starts, when the document says so.")
    coverage_end: DateTimeSchema | None = F("When coverage ends, when the document says so.")
    insured_persons: list[PersonSchema] | None = F("People covered by the policy.")
    coverage_details: list[CoverageDetailSchema] | None = F("Benefits, limits, and exclusions that were itemized.")
    emergency_contact: ContactSchema | None = F("Assistance or claims contact printed on the policy.")
    geographic_coverage: str | None = F("Where the policy applies, as printed.")
    premium: CurrencySchema | None = F("Premium when an amount is stated.")
