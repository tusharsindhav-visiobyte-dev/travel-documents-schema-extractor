"""Controlled vocabularies for document and travel fields.

Enum members are the standardized form. Printed wording that does not map
cleanly belongs in a companion ``*_original`` string and the enum stays null.
"""

from __future__ import annotations

from enum import Enum


class DocumentType(str, Enum):
    """Registered travel document type identifiers."""

    FLIGHT_TICKET = "flight_ticket"
    FLIGHT_BOOKING_CONFIRMATION = "flight_booking_confirmation"
    FLIGHT_BOARDING_PASS = "flight_boarding_pass"
    FLIGHT_ITINERARY = "flight_itinerary"
    FLIGHT_CANCELLATION = "flight_cancellation"
    FLIGHT_RESCHEDULE = "flight_reschedule"
    FLIGHT_UPGRADE_CONFIRMATION = "flight_upgrade_confirmation"
    FLIGHT_INVOICE = "flight_invoice"
    BAGGAGE_CONFIRMATION = "baggage_confirmation"

    HOTEL_BOOKING = "hotel_booking"
    HOTEL_CONFIRMATION = "hotel_confirmation"
    HOTEL_VOUCHER = "hotel_voucher"
    HOTEL_INVOICE = "hotel_invoice"
    HOTEL_CANCELLATION = "hotel_cancellation"
    HOTEL_RESCHEDULE = "hotel_reschedule"
    RESORT_BOOKING = "resort_booking"
    HOSTEL_BOOKING = "hostel_booking"
    VACATION_RENTAL = "vacation_rental"
    HOMESTAY_BOOKING = "homestay_booking"

    TRAIN_TICKET = "train_ticket"
    TRAIN_BOOKING_CONFIRMATION = "train_booking_confirmation"
    RAILWAY_RESERVATION = "railway_reservation"
    RAIL_PASS = "rail_pass"
    TRAIN_CANCELLATION = "train_cancellation"
    TRAIN_RESCHEDULE = "train_reschedule"

    BUS_TICKET = "bus_ticket"
    BUS_BOOKING_CONFIRMATION = "bus_booking_confirmation"
    BUS_PASS = "bus_pass"
    BUS_CANCELLATION = "bus_cancellation"
    BUS_RESCHEDULE = "bus_reschedule"

    CAR_RENTAL = "car_rental"
    CAR_RENTAL_CONFIRMATION = "car_rental_confirmation"
    CAR_RENTAL_AGREEMENT = "car_rental_agreement"
    TAXI_BOOKING = "taxi_booking"
    CHAUFFEUR_BOOKING = "chauffeur_booking"
    VEHICLE_PERMIT = "vehicle_permit"
    PARKING_RESERVATION = "parking_reservation"

    TRAVEL_ITINERARY = "travel_itinerary"
    MULTI_CITY_ITINERARY = "multi_city_itinerary"
    TRIP_PLAN = "trip_plan"
    DAY_WISE_ITINERARY = "day_wise_itinerary"
    BUSINESS_TRAVEL_ITINERARY = "business_travel_itinerary"
    GROUP_TRAVEL_ITINERARY = "group_travel_itinerary"
    TOUR_ITINERARY = "tour_itinerary"

    PASSPORT = "passport"
    VISA = "visa"
    EVISA = "evisa"
    RESIDENCE_PERMIT = "residence_permit"
    TRAVEL_AUTHORIZATION = "travel_authorization"
    ENTRY_PERMIT = "entry_permit"
    EXIT_PERMIT = "exit_permit"
    INTERNATIONAL_DRIVING_PERMIT = "international_driving_permit"

    TRAVEL_INSURANCE = "travel_insurance"
    INSURANCE_CERTIFICATE = "insurance_certificate"
    INSURANCE_CLAIM = "insurance_claim"
    MEDICAL_TRAVEL_CERTIFICATE = "medical_travel_certificate"
    VACCINATION_CERTIFICATE = "vaccination_certificate"
    MEDICAL_ASSISTANCE = "medical_assistance"

    CRUISE_BOOKING = "cruise_booking"
    CRUISE_TICKET = "cruise_ticket"
    CRUISE_ITINERARY = "cruise_itinerary"
    FERRY_TICKET = "ferry_ticket"
    SHIP_BOARDING_PASS = "ship_boarding_pass"
    SHORE_EXCURSION = "shore_excursion"

    TOUR_BOOKING = "tour_booking"
    ACTIVITY_BOOKING = "activity_booking"
    ATTRACTION_TICKET = "attraction_ticket"
    MUSEUM_TICKET = "museum_ticket"
    THEME_PARK_TICKET = "theme_park_ticket"
    EVENT_TICKET = "event_ticket"
    SAFARI_BOOKING = "safari_booking"
    TREKKING_PERMIT = "trekking_permit"
    CAMPING_RESERVATION = "camping_reservation"
    EXCURSION_VOUCHER = "excursion_voucher"

    AIRPORT_TRANSFER = "airport_transfer"
    AIRPORT_PICKUP = "airport_pickup"
    AIRPORT_DROPOFF = "airport_dropoff"
    SHUTTLE_BOOKING = "shuttle_booking"
    AIRPORT_LOUNGE_PASS = "airport_lounge_pass"
    MEET_AND_GREET = "meet_and_greet"

    TRAVEL_INVOICE = "travel_invoice"
    TRAVEL_PAYMENT_RECEIPT = "travel_payment_receipt"
    REFUND_CONFIRMATION = "refund_confirmation"
    BOOKING_TRANSACTION = "booking_transaction"
    TRAVEL_EXPENSE = "travel_expense"
    CURRENCY_EXCHANGE_RECEIPT = "currency_exchange_receipt"

    CORPORATE_TRAVEL_AUTHORIZATION = "corporate_travel_authorization"
    BUSINESS_TRIP_APPROVAL = "business_trip_approval"
    BUSINESS_INVITATION = "business_invitation"
    CONFERENCE_REGISTRATION = "conference_registration"
    EXHIBITION_PASS = "exhibition_pass"
    TRAVEL_REIMBURSEMENT = "travel_reimbursement"

    CHILD_TRAVEL_CONSENT = "child_travel_consent"
    PET_TRAVEL_CERTIFICATE = "pet_travel_certificate"
    PET_TRAVEL_BOOKING = "pet_travel_booking"
    SPECIAL_ASSISTANCE = "special_assistance"
    WHEELCHAIR_ASSISTANCE = "wheelchair_assistance"
    TRAVEL_EMERGENCY_CONTACT = "travel_emergency_contact"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    CONFIRMED = "confirmed"
    AMENDED = "amended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    USED = "used"
    REFUNDED = "refunded"
    UNKNOWN = "unknown"


class BookingStatus(str, Enum):
    PENDING = "pending"
    ON_HOLD = "on_hold"
    CONFIRMED = "confirmed"
    TICKETED = "ticketed"
    WAITLISTED = "waitlisted"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    MODIFIED = "modified"
    NO_SHOW = "no_show"
    UNKNOWN = "unknown"


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PENDING = "pending"
    AUTHORIZED = "authorized"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    VOUCHER = "voucher"
    CORPORATE_ACCOUNT = "corporate_account"
    OTHER = "other"
    UNKNOWN = "unknown"


class TransportMode(str, Enum):
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    CAR = "car"
    TAXI = "taxi"
    CHAUFFEUR = "chauffeur"
    FERRY = "ferry"
    CRUISE = "cruise"
    SHUTTLE = "shuttle"
    TRANSFER = "transfer"
    WALK = "walk"
    OTHER = "other"
    UNKNOWN = "unknown"


class ProviderType(str, Enum):
    AIRLINE = "airline"
    HOTEL = "hotel"
    HOSTEL = "hostel"
    RAIL = "rail"
    BUS = "bus"
    CAR_RENTAL = "car_rental"
    CRUISE = "cruise"
    FERRY = "ferry"
    INSURER = "insurer"
    TOUR_OPERATOR = "tour_operator"
    TRANSFER = "transfer"
    ACTIVITY = "activity"
    GOVERNMENT = "government"
    CORPORATE = "corporate"
    OTHER = "other"
    UNKNOWN = "unknown"


class CabinClass(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"
    UNKNOWN = "unknown"


class PassengerType(str, Enum):
    ADULT = "adult"
    CHILD = "child"
    INFANT = "infant"
    YOUTH = "youth"
    SENIOR = "senior"
    UNKNOWN = "unknown"


class PropertyType(str, Enum):
    HOTEL = "hotel"
    RESORT = "resort"
    HOSTEL = "hostel"
    VACATION_RENTAL = "vacation_rental"
    HOMESTAY = "homestay"
    APARTMENT = "apartment"
    OTHER = "other"
    UNKNOWN = "unknown"


class MealPlan(str, Enum):
    ROOM_ONLY = "room_only"
    BREAKFAST = "breakfast"
    HALF_BOARD = "half_board"
    FULL_BOARD = "full_board"
    ALL_INCLUSIVE = "all_inclusive"
    UNKNOWN = "unknown"


class EntryPermission(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    MULTIPLE = "multiple"
    UNKNOWN = "unknown"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    DENIED = "denied"
    PAID = "paid"
    WITHDRAWN = "withdrawn"
    UNKNOWN = "unknown"


class ExtractionMethod(str, Enum):
    UNKNOWN = "unknown"
    MANUAL = "manual"
    PARSER = "parser"
    MODEL = "model"
    IMPORTED = "imported"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
