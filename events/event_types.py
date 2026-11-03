"""Actionable travel event types.

Events are derived travel activities. They are not document types and they
are not a substitute for a flight ticket, hotel voucher, or other document.
"""

from __future__ import annotations

from enum import Enum


class EventType(str, Enum):
    """Standard event types a trip timeline can store."""

    FLIGHT_DEPARTURE = "flight_departure"
    FLIGHT_ARRIVAL = "flight_arrival"
    TRAIN_DEPARTURE = "train_departure"
    TRAIN_ARRIVAL = "train_arrival"
    BUS_DEPARTURE = "bus_departure"
    BUS_ARRIVAL = "bus_arrival"
    HOTEL_CHECKIN = "hotel_checkin"
    HOTEL_CHECKOUT = "hotel_checkout"
    CAR_PICKUP = "car_pickup"
    CAR_RETURN = "car_return"
    TOUR_START = "tour_start"
    TOUR_END = "tour_end"
    CRUISE_DEPARTURE = "cruise_departure"
    CRUISE_ARRIVAL = "cruise_arrival"
    FERRY_DEPARTURE = "ferry_departure"
    FERRY_ARRIVAL = "ferry_arrival"
    VISA_EXPIRY = "visa_expiry"
    PASSPORT_EXPIRY = "passport_expiry"
    ACTIVITY_START = "activity_start"
    TRANSFER_PICKUP = "transfer_pickup"
    INSURANCE_COVERAGE_START = "insurance_coverage_start"
    INSURANCE_COVERAGE_END = "insurance_coverage_end"
    PARKING_START = "parking_start"
    PARKING_END = "parking_end"
    MEETING_START = "meeting_start"
    OTHER = "other"


class EventStatus(str, Enum):
    """Status of a derived travel event."""

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TENTATIVE = "tentative"
    DELAYED = "delayed"
    UNKNOWN = "unknown"
