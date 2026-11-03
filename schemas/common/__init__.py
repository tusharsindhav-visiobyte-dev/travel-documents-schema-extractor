"""Reusable travel entities shared by specialized document schemas."""

from schemas.common.accommodation import AccommodationSchema, GuestSchema
from schemas.common.baggage import BaggageAllowanceSchema, BaggageItemSchema
from schemas.common.booking import BookingSchema
from schemas.common.cancellation import CancellationPolicySchema
from schemas.common.contact import ContactSchema, EmergencyContactSchema
from schemas.common.datetime import DateTimeSchema, TimezoneSchema
from schemas.common.evidence import (
    DocumentEvidenceSchema,
    ExtractionMetadataSchema,
    SourceLocationSchema,
)
from schemas.common.identification import IdentificationSchema
from schemas.common.insurance import CoverageDetailSchema, InsuranceSchema
from schemas.common.location import (
    AddressSchema,
    AirportSchema,
    BusStationSchema,
    GeoPointSchema,
    LocationSchema,
    RailwayStationSchema,
)
from schemas.common.passenger import PassengerSchema
from schemas.common.payment import CurrencySchema, LineItemSchema, PartySchema, PaymentSchema
from schemas.common.person import PersonNameSchema, PersonSchema
from schemas.common.provider import OrganizationSchema, ProviderSchema
from schemas.common.transport import (
    RouteSchema,
    SeatAssignmentSchema,
    TransportSchema,
    VehicleSchema,
)
from schemas.common.traveler import LoyaltyProgramSchema, TravelerSchema

__all__ = [
    "AccommodationSchema",
    "AddressSchema",
    "AirportSchema",
    "BaggageAllowanceSchema",
    "BaggageItemSchema",
    "BookingSchema",
    "BusStationSchema",
    "CancellationPolicySchema",
    "ContactSchema",
    "CoverageDetailSchema",
    "CurrencySchema",
    "DateTimeSchema",
    "DocumentEvidenceSchema",
    "EmergencyContactSchema",
    "ExtractionMetadataSchema",
    "GeoPointSchema",
    "GuestSchema",
    "IdentificationSchema",
    "InsuranceSchema",
    "LineItemSchema",
    "LocationSchema",
    "LoyaltyProgramSchema",
    "OrganizationSchema",
    "PartySchema",
    "PassengerSchema",
    "PaymentSchema",
    "PersonNameSchema",
    "PersonSchema",
    "ProviderSchema",
    "RailwayStationSchema",
    "RouteSchema",
    "SeatAssignmentSchema",
    "SourceLocationSchema",
    "TimezoneSchema",
    "TransportSchema",
    "TravelerSchema",
    "VehicleSchema",
]
