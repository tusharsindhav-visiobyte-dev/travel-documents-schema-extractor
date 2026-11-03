"""Train and rail documents. A reservation, a ticket, and a rail pass are separate schemas."""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import BookingStatus
from schemas.common.booking import BookingSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import RailwayStationSchema
from schemas.common.passenger import PassengerSchema
from schemas.common.payment import CurrencySchema, PaymentSchema
from schemas.common.provider import ProviderSchema
from schemas.common.transport import SeatAssignmentSchema


class TrainSegmentSchema(SchemaModel):
    """One rail leg. Station timezones are independent of each other."""

    segment_id: str | None = F("Identifier for this rail segment.")
    train_number: str | None = F("Train number as printed.")
    train_name: str | None = F("Train name as printed.")
    departure_station: RailwayStationSchema | None = F("Station where this segment starts.")
    arrival_station: RailwayStationSchema | None = F("Station where this segment ends.")
    departure: DateTimeSchema | None = F("Departure date, time, and timezone.")
    arrival: DateTimeSchema | None = F("Arrival date, time, and timezone.")
    coach: str | None = F("Coach or carriage as printed.")
    seat: str | None = F("Seat or berth as printed.")
    travel_class: str | None = F("Class of travel as printed.")
    platform: str | None = F("Platform when the document prints one. Many tickets omit it.")
    boarding_point: str | None = F("Boarding point as printed when it differs from the departure station.")
    overnight_journey: bool | None = F("True when the segment is an overnight journey.")
    international: bool | None = F("True or false only when the segment's countries establish it.")
    distance_original: str | None = F("Distance exactly as printed.")


class TrainDocumentSchema(BaseDocumentSchema):
    """Fields shared by rail tickets, reservations, passes, and related notices."""

    operator: ProviderSchema | None = F("Railway operator.")
    train_number: str | None = F("Train number when the document covers one train.")
    train_name: str | None = F("Train name when the document covers one train.")
    pnr: str | None = F("PNR or reservation number as printed.")
    segments: list[TrainSegmentSchema] | None = F("Rail segments in journey order.")
    passengers: list[PassengerSchema] | None = F("Passengers named on the document.")
    seat_assignments: list[SeatAssignmentSchema] | None = F("Coach and seat assignments.")
    booking: BookingSchema | None = F("Booking reference.")
    booking_status: BookingStatus | None = F("Booking status.")
    payment: PaymentSchema | None = F("Payment information.")
    quota: str | None = F("Reservation quota exactly as printed.")
    travel_class: str | None = F("Class of travel as printed.")
    remarks: str | None = F("Remarks printed on the rail document.")


_CATEGORY = "train"
_MODULE = __name__


def _train(name: str, document_type: str, description: str, **fields: tuple) -> type[TrainDocumentSchema]:
    return declare_document_schema(
        name,
        document_type=document_type,
        base=TrainDocumentSchema,
        description=description,
        module=_MODULE,
        category=_CATEGORY,
        fields=fields or None,
    )


TrainTicketSchema = _train(
    "TrainTicketSchema",
    "train_ticket",
    "An issued train ticket. A ticket is not the same document as a reservation chart or a booking hold.",
    ticket_number=(str | None, F("Ticket number as printed.")),
    fare=(CurrencySchema | None, F("Fare when the ticket states an amount.")),
)

TrainBookingConfirmationSchema = _train(
    "TrainBookingConfirmationSchema",
    "train_booking_confirmation",
    "A confirmation that a rail booking exists. Ticketing may still be pending.",
    ticketing_deadline=(DateTimeSchema | None, F("Ticketing deadline when the confirmation states one.")),
    confirmation_number=(str | None, F("Confirmation number as printed.")),
)

RailwayReservationSchema = _train(
    "RailwayReservationSchema",
    "railway_reservation",
    "A railway reservation record, including waitlist or chart status when printed.",
    reservation_status=(str | None, F("Reservation status exactly as printed.")),
    chart_status=(str | None, F("Reservation chart status as printed.")),
    waitlist_position=(str | None, F("Waitlist position as printed. It is kept as text because formats vary.")),
    reservation_upto=(str | None, F("Station or point up to which the reservation applies, as printed.")),
)

RailPassSchema = _train(
    "RailPassSchema",
    "rail_pass",
    "A rail pass covering travel over a period or a set of regions.",
    pass_name=(str | None, F("Pass product name.")),
    validity_start=(DateTimeSchema | None, F("When the pass becomes valid.")),
    validity_end=(DateTimeSchema | None, F("When the pass stops being valid.")),
    covered_regions=(list[str] | None, F("Regions or networks the pass covers.")),
    travel_days_allowed=(int | None, Field(default=None, ge=0, description="Travel days allowed, when stated.")),
)

TrainCancellationSchema = _train(
    "TrainCancellationSchema",
    "train_cancellation",
    "A notice that a rail ticket or reservation was cancelled.",
    cancelled_at=(DateTimeSchema | None, F("When the cancellation was recorded.")),
    cancellation_reason=(str | None, F("Cancellation reason as printed.")),
    refund=(PaymentSchema | None, F("Refund described by the notice.")),
)

TrainRescheduleSchema = _train(
    "TrainRescheduleSchema",
    "train_reschedule",
    "A notice that a rail journey changed. Previous and revised segments are both kept.",
    previous_segments=(list[TrainSegmentSchema] | None, F("Segments before the change.")),
    revised_segments=(list[TrainSegmentSchema] | None, F("Segments after the change.")),
    changed_at=(DateTimeSchema | None, F("When the change was recorded.")),
    change_fee=(CurrencySchema | None, F("Change fee when an amount is stated.")),
)

TRAIN_SCHEMAS = (
    TrainTicketSchema,
    TrainBookingConfirmationSchema,
    RailwayReservationSchema,
    RailPassSchema,
    TrainCancellationSchema,
    TrainRescheduleSchema,
)
