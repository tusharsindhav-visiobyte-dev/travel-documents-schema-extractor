"""Cancellation terms shared by bookings and tickets."""

from __future__ import annotations

from schemas.base.base_models import F, SchemaModel
from schemas.common.datetime import DateTimeSchema
from schemas.common.payment import CurrencySchema


class CancellationPolicySchema(SchemaModel):
    """Cancellation terms. The printed paragraph is kept even when the penalty is unclear."""

    refundable: bool | None = F("True or false only when the document states whether the booking can be refunded.")
    free_cancellation_until: DateTimeSchema | None = F("Free-cancellation deadline when one is stated.")
    penalty: CurrencySchema | None = F("Cancellation penalty when an amount is stated.")
    penalty_original: str | None = F("Penalty text exactly as printed.")
    description: str | None = F("Short description of the policy.")
    original_text: str | None = F("Policy text exactly as printed.")
