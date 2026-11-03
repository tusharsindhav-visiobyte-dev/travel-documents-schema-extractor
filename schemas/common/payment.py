"""Money, line items, payments, and the parties who pay or get paid."""

from __future__ import annotations

from decimal import Decimal

from pydantic import field_validator

from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import PaymentMethod, PaymentStatus
from schemas.base.validators import validate_card_last_four, validate_currency_code
from schemas.common.contact import ContactSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.person import PersonSchema
from schemas.common.provider import OrganizationSchema


class CurrencySchema(SchemaModel):
    """An amount of money. Symbols and unparsed text stay beside the numeric amount."""

    amount: Decimal | None = F("Numeric amount only when the document shows an unambiguous number.")
    currency_code: str | None = F("ISO 4217 alphabetic code when the currency is known.")
    currency_original: str | None = F("Currency symbol or name exactly as printed.")
    original_amount_text: str | None = F("Amount exactly as printed, including separators and symbols.")

    @field_validator("currency_code")
    @classmethod
    def _currency_code(cls, value: str | None) -> str | None:
        return validate_currency_code(value)


class PartySchema(SchemaModel):
    """A person or organization that pays, bills, or receives money."""

    name: str | None = F("Party name as printed.")
    organization: OrganizationSchema | None = F("Organization details when the party is an organization.")
    person: PersonSchema | None = F("Person details when the party is a person.")
    contact: ContactSchema | None = F("Contact details for the party.")
    tax_identifier: str | None = F("Tax identifier when the document prints one. It is not required.")
    original_name: str | None = F("Party name exactly as printed.")


class LineItemSchema(SchemaModel):
    """One charge, tax, or credit line."""

    description: str | None = F("Line description as printed.")
    quantity: Decimal | None = F("Quantity when the document shows one.")
    unit_amount: CurrencySchema | None = F("Price per unit when it is shown.")
    total_amount: CurrencySchema | None = F("Line total when it is shown.")
    tax_amount: CurrencySchema | None = F("Tax on this line when it is shown separately.")
    category: str | None = F("Line category such as fare, tax, or fee.")
    original_text: str | None = F("Line text exactly as printed.")


class PaymentSchema(SchemaModel):
    """A payment recorded on a travel document. Card data is limited to the last four digits."""

    amount: CurrencySchema | None = F("Payment amount.")
    status: PaymentStatus | None = F("Standardized payment status. Leave null when the wording is unmapped.")
    status_original: str | None = F("Payment status exactly as printed.")
    method: PaymentMethod | None = F("Standardized payment method. Leave null when the wording is unmapped.")
    method_original: str | None = F("Payment method exactly as printed.")
    paid_at: DateTimeSchema | None = F("When payment was taken, when the document says so.")
    transaction_reference: str | None = F("Payment or transaction reference as printed.")
    payer: PartySchema | None = F("Who paid.")
    payee: PartySchema | None = F("Who received payment.")
    card_last_four: str | None = F("Last four digits of a card when those digits are printed. Full card numbers are rejected.")
    taxes: list[LineItemSchema] | None = F("Tax lines associated with this payment.")
    total: CurrencySchema | None = F("Total associated with this payment when it differs from amount.")

    @field_validator("card_last_four")
    @classmethod
    def _card_last_four(cls, value: str | None) -> str | None:
        return validate_card_last_four(value)
