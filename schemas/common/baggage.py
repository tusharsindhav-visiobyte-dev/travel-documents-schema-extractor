"""Checked and cabin baggage allowances shared by transport documents."""

from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from schemas.base.base_models import F, SchemaModel


class BaggageAllowanceSchema(SchemaModel):
    """A baggage allowance. The printed sentence is kept when the parts are unclear."""

    pieces: int | None = Field(default=None, ge=0, description="Number of pieces when the document states a count.")
    weight_kg: Decimal | None = Field(
        default=None,
        ge=0,
        description="Weight in kilograms only when the unit is kilograms.",
    )
    weight_original: str | None = F("Weight exactly as printed, including the unit.")
    cabin_pieces: int | None = Field(default=None, ge=0, description="Cabin bag count when stated.")
    checked_pieces: int | None = Field(default=None, ge=0, description="Checked bag count when stated.")
    description: str | None = F("Short allowance description.")
    original_text: str | None = F("Allowance sentence exactly as printed.")


class BaggageItemSchema(SchemaModel):
    """One bag or baggage record mentioned on a document."""

    baggage_id: str | None = F("Application or tag identifier for the bag.")
    tag_number: str | None = F("Baggage tag number as printed.")
    weight_kg: Decimal | None = Field(
        default=None,
        ge=0,
        description="Weight in kilograms only when the unit is kilograms.",
    )
    weight_original: str | None = F("Weight exactly as printed, including the unit.")
    pieces: int | None = Field(default=None, ge=0, description="Piece count for this item when stated.")
    description: str | None = F("Bag description as printed.")
    passenger_ref: str | None = F("Reference to the passenger this bag belongs to.")
    segment_ref: str | None = F("Reference to the travel segment this bag is checked on.")
    status: str | None = F("Baggage status as printed.")
