"""Hotel and other accommodation documents.

A booking, a confirmation, a voucher, and an invoice are different documents.
They share stay fields and add the details that distinguish each one.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import BookingStatus, MealPlan, PaymentStatus
from schemas.common.accommodation import AccommodationSchema, GuestSchema
from schemas.common.booking import BookingSchema
from schemas.common.cancellation import CancellationPolicySchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import AddressSchema
from schemas.common.payment import CurrencySchema, LineItemSchema, PaymentSchema
from schemas.common.person import PersonSchema


class RoomStaySchema(SchemaModel):
    """One room or bed product inside a stay."""

    room_type: str | None = F("Room or bed type.")
    room_type_original: str | None = F("Room type exactly as printed.")
    room_quantity: int | None = Field(default=None, ge=0, description="How many rooms of this type were booked.")
    bed_type: str | None = F("Bed type as printed.")
    occupancy: int | None = Field(default=None, ge=0, description="Occupancy stated for the room.")
    room_numbers: list[str] | None = F("Assigned room numbers when they are printed.")
    rate_plan: str | None = F("Rate plan name as printed.")
    meal_plan: MealPlan | None = F("Meal plan for this room when it differs from the stay.")
    guests: list[GuestSchema] | None = F("Guests assigned to this room.")


class HotelStayDocumentSchema(BaseDocumentSchema):
    """A stay at a hotel, resort, hostel, rental, or homestay."""

    property: AccommodationSchema | None = F("Property where the stay takes place.")
    property_address: AddressSchema | None = F("Property address when it is printed separately from the property.")
    booking: BookingSchema | None = F("Booking reference for the stay.")
    booking_status: BookingStatus | None = F("Status of the stay booking.")
    guests: list[GuestSchema] | None = F("Guests named on the document.")
    rooms: list[RoomStaySchema] | None = F("Rooms or beds included in the stay.")
    check_in: DateTimeSchema | None = F("Check-in date and time. The clock time stays empty when it was not printed.")
    check_out: DateTimeSchema | None = F("Check-out date and time, with its own timezone fields.")
    guest_count: int | None = Field(default=None, ge=0, description="Guest count only when the document states one.")
    number_of_nights: int | None = Field(
        default=None,
        ge=0,
        description="Number of nights only when the document states it. It is not calculated when the dates are missing.",
    )
    meal_plan: MealPlan | None = F("Meal plan when it maps to the standard list.")
    meal_plan_original: str | None = F("Meal plan exactly as printed.")
    payment: PaymentSchema | None = F("Payment information.")
    payment_status: PaymentStatus | None = F("Payment status of the stay.")
    cancellation_policy: CancellationPolicySchema | None = F("Cancellation terms printed for the stay.")
    special_requests: list[str] | None = F("Special requests as printed.")
    remarks: str | None = F("Other stay remarks.")


_CATEGORY = "hotel"
_MODULE = __name__


def _stay(name: str, document_type: str, description: str, **fields: tuple) -> type[HotelStayDocumentSchema]:
    return declare_document_schema(
        name,
        document_type=document_type,
        base=HotelStayDocumentSchema,
        description=description,
        module=_MODULE,
        category=_CATEGORY,
        fields=fields or None,
    )


HotelBookingSchema = _stay(
    "HotelBookingSchema",
    "hotel_booking",
    "A hotel reservation request or booking record. It is not by itself a voucher or an invoice.",
    rate_quote=(CurrencySchema | None, F("Quoted rate when the booking states one.")),
    requested_at=(DateTimeSchema | None, F("When the booking was requested.")),
)

HotelConfirmationSchema = _stay(
    "HotelConfirmationSchema",
    "hotel_confirmation",
    "A hotel confirmation that a stay has been accepted. It is not a payment invoice.",
    confirmation_number=(str | None, F("Hotel confirmation number as printed.")),
    confirmed_at=(DateTimeSchema | None, F("When the stay was confirmed.")),
)

HotelVoucherSchema = _stay(
    "HotelVoucherSchema",
    "hotel_voucher",
    "A voucher the guest presents at the property. It is not the same document as a confirmation email.",
    voucher_number=(str | None, F("Voucher number as printed.")),
    voucher_instructions=(str | None, F("Instructions for presenting or redeeming the voucher.")),
    payable_by=(str | None, F("Who pays the property, such as guest or company, as printed.")),
)

HotelInvoiceSchema = _stay(
    "HotelInvoiceSchema",
    "hotel_invoice",
    "An invoice for accommodation charges.",
    invoice_number=(str | None, F("Invoice number as printed.")),
    line_items=(list[LineItemSchema] | None, F("Invoice lines.")),
    amount_due=(CurrencySchema | None, F("Amount due when the invoice states one.")),
)

HotelCancellationSchema = _stay(
    "HotelCancellationSchema",
    "hotel_cancellation",
    "A notice that a stay was cancelled.",
    cancelled_at=(DateTimeSchema | None, F("When the cancellation was recorded.")),
    cancellation_reason=(str | None, F("Cancellation reason as printed.")),
    refund=(PaymentSchema | None, F("Refund described by the cancellation.")),
)

HotelRescheduleSchema = _stay(
    "HotelRescheduleSchema",
    "hotel_reschedule",
    "A notice that stay dates changed. Previous and revised dates are both kept.",
    previous_check_in=(DateTimeSchema | None, F("Check-in before the change.")),
    previous_check_out=(DateTimeSchema | None, F("Check-out before the change.")),
    revised_check_in=(DateTimeSchema | None, F("Check-in after the change.")),
    revised_check_out=(DateTimeSchema | None, F("Check-out after the change.")),
    changed_at=(DateTimeSchema | None, F("When the change was recorded.")),
)

ResortBookingSchema = _stay(
    "ResortBookingSchema",
    "resort_booking",
    "A booking for a resort stay, including resort-specific amenities and board basis.",
    amenities=(list[str] | None, F("Resort amenities named on the booking.")),
    all_inclusive=(bool | None, F("True when the booking states that the stay is all inclusive.")),
)

HostelBookingSchema = _stay(
    "HostelBookingSchema",
    "hostel_booking",
    "A hostel booking. Bed and dormitory details stay optional.",
    bed_type=(str | None, F("Bed type as printed, such as bunk or single.")),
    dormitory=(bool | None, F("True when the booking is for a shared dormitory.")),
    bed_count=(int | None, Field(default=None, ge=0, description="Number of beds when the booking states it.")),
)

VacationRentalSchema = _stay(
    "VacationRentalSchema",
    "vacation_rental",
    "A vacation rental booking, including house rules and the host when they are named.",
    house_rules=(list[str] | None, F("House rules as printed.")),
    host=(PersonSchema | None, F("Host named on the booking.")),
    property_unit=(str | None, F("Unit, apartment, or listing name as printed.")),
)

HomestayBookingSchema = _stay(
    "HomestayBookingSchema",
    "homestay_booking",
    "A homestay booking. Host and meal arrangements are optional.",
    host=(PersonSchema | None, F("Host named on the booking.")),
    meals_with_host=(bool | None, F("True when the booking says meals are shared with the host.")),
)

HOTEL_SCHEMAS = (
    HotelBookingSchema,
    HotelConfirmationSchema,
    HotelVoucherSchema,
    HotelInvoiceSchema,
    HotelCancellationSchema,
    HotelRescheduleSchema,
    ResortBookingSchema,
    HostelBookingSchema,
    VacationRentalSchema,
    HomestayBookingSchema,
)
