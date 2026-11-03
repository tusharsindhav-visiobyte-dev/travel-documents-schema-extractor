"""A passenger, which is a traveler with ticket and seat details."""

from __future__ import annotations

from schemas.base.base_models import F
from schemas.base.enums import CabinClass, PassengerType
from schemas.common.baggage import BaggageAllowanceSchema
from schemas.common.traveler import TravelerSchema


class PassengerSchema(TravelerSchema):
    """A passenger named on a transport document.

    Seat and ticket number live here when the document gives one value for the
    passenger. Segment-specific seats belong on a seat assignment.
    """

    passenger_type: PassengerType | None = F("Standardized passenger type. Leave null when it is unclear.")
    passenger_type_original: str | None = F("Passenger type exactly as printed.")
    ticket_number: str | None = F("Ticket number for this passenger when the document shows one.")
    seat: str | None = F("Seat when the document assigns one seat to this passenger.")
    cabin_class: CabinClass | None = F("Cabin class when it is known.")
    travel_class: str | None = F("Travel class as printed, including rail and bus classes.")
    baggage_allowance: BaggageAllowanceSchema | None = F("Baggage allowance for this passenger.")
    frequent_flyer_number: str | None = F("Frequent flyer number as printed.")
