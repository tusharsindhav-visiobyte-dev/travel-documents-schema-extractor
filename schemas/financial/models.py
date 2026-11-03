"""Invoices, receipts, refunds, expenses, and currency exchange documents."""

from __future__ import annotations

from decimal import Decimal

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F
from schemas.base.enums import PaymentStatus
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import LocationSchema
from schemas.common.payment import CurrencySchema, LineItemSchema, PartySchema, PaymentSchema


class FinancialDocumentSchema(BaseDocumentSchema):
    """A money document related to travel."""

    payer: PartySchema | None = F("Who pays.")
    payee: PartySchema | None = F("Who is paid.")
    line_items: list[LineItemSchema] | None = F("Charge, tax, or credit lines.")
    subtotal: CurrencySchema | None = F("Subtotal when stated.")
    tax_total: CurrencySchema | None = F("Tax total when stated.")
    total: CurrencySchema | None = F("Grand total when stated.")
    payment: PaymentSchema | None = F("Payment used to settle the document.")
    payment_status: PaymentStatus | None = F("Payment status.")
    related_booking_reference: str | None = F("Booking this financial document refers to.")
    service_period_start: DateTimeSchema | None = F("Start of the service period, when stated.")
    service_period_end: DateTimeSchema | None = F("End of the service period, when stated.")
    remarks: str | None = F("Financial remarks.")


_MODULE = __name__


def _money(name: str, document_type: str, description: str, **fields: tuple):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=FinancialDocumentSchema,
        description=description,
        module=_MODULE,
        category="financial",
        fields=fields or None,
    )


TravelInvoiceSchema = _money(
    "TravelInvoiceSchema",
    "travel_invoice",
    "An invoice for travel services. It asks for payment or records an amount due.",
    invoice_number=(str | None, F("Invoice number as printed.")),
    due_date=(DateTimeSchema | None, F("Payment due date when stated.")),
)

TravelPaymentReceiptSchema = _money(
    "TravelPaymentReceiptSchema",
    "travel_payment_receipt",
    "A receipt showing that a travel payment was received.",
    receipt_number=(str | None, F("Receipt number as printed.")),
    received_at=(DateTimeSchema | None, F("When the payment was received.")),
)

RefundConfirmationSchema = _money(
    "RefundConfirmationSchema",
    "refund_confirmation",
    "Confirmation that a refund was approved or paid.",
    refund_amount=(CurrencySchema | None, F("Amount refunded or to be refunded.")),
    original_transaction_reference=(str | None, F("Reference of the original charge.")),
    refunded_at=(DateTimeSchema | None, F("When the refund was completed, when stated.")),
)

BookingTransactionSchema = _money(
    "BookingTransactionSchema",
    "booking_transaction",
    "A payment authorization or transaction tied to a booking.",
    transaction_type=(str | None, F("Transaction type as printed, such as authorization or capture.")),
    authorization_code=(str | None, F("Authorization code when printed.")),
)

TravelExpenseSchema = _money(
    "TravelExpenseSchema",
    "travel_expense",
    "A single travel expense, such as a meal or local transport receipt.",
    expense_category=(str | None, F("Expense category as printed or assigned.")),
    incurred_at=(DateTimeSchema | None, F("When the expense was incurred.")),
    merchant=(str | None, F("Merchant name as printed.")),
)

CurrencyExchangeReceiptSchema = _money(
    "CurrencyExchangeReceiptSchema",
    "currency_exchange_receipt",
    "A receipt for exchanging one currency for another. Amounts are not calculated from each other.",
    source_amount=(CurrencySchema | None, F("Amount given to the exchanger.")),
    target_amount=(CurrencySchema | None, F("Amount received from the exchanger.")),
    exchange_rate_original=(str | None, F("Exchange rate exactly as printed.")),
    exchange_rate=(Decimal | None, F("Numeric exchange rate only when the receipt shows an unambiguous number.")),
    exchanged_at=(DateTimeSchema | None, F("When the exchange happened.")),
    exchange_location=(LocationSchema | None, F("Where the exchange happened.")),
)

FINANCIAL_SCHEMAS = (
    TravelInvoiceSchema,
    TravelPaymentReceiptSchema,
    RefundConfirmationSchema,
    BookingTransactionSchema,
    TravelExpenseSchema,
    CurrencyExchangeReceiptSchema,
)
