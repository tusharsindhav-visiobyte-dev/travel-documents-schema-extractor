"""Trip itineraries. These describe a plan found in a document, not derived travel events."""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F, SchemaModel
from schemas.common.accommodation import AccommodationSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import LocationSchema
from schemas.common.person import PersonSchema
from schemas.common.provider import OrganizationSchema, ProviderSchema
from schemas.common.transport import TransportSchema
from schemas.common.traveler import TravelerSchema


class ActivityItemSchema(SchemaModel):
    """An activity, transfer, or scheduled item inside an itinerary."""

    activity_id: str | None = F("Identifier for this item.")
    title: str | None = F("Item title.")
    description: str | None = F("What happens during the item.")
    start: DateTimeSchema | None = F("Start date and time. A missing clock time stays missing.")
    end: DateTimeSchema | None = F("End date and time.")
    location: LocationSchema | None = F("Where the item happens.")
    provider: ProviderSchema | None = F("Provider of the item.")
    booking_reference: str | None = F("Booking reference printed for the item.")
    included: bool | None = F("True when the document says the item is included.")


class ItineraryDaySchema(SchemaModel):
    """One day of an itinerary."""

    day_number: int | None = Field(default=None, ge=1, description="Day number when the document numbers the days.")
    date: DateTimeSchema | None = F("Calendar date of this day.")
    title: str | None = F("Day title as printed.")
    locations: list[LocationSchema] | None = F("Places visited on this day.")
    activities: list[ActivityItemSchema] | None = F("Activities scheduled on this day.")
    transportation: list[TransportSchema] | None = F("Transport used on this day.")
    accommodation: AccommodationSchema | None = F("Where travelers stay on this day.")
    meals: list[str] | None = F("Meals named for this day.")
    notes: str | None = F("Day notes exactly as printed.")


class ItineraryDocumentSchema(BaseDocumentSchema):
    """A document that lays out destinations, days, transport, stays, and activities."""

    trip_name: str | None = F("Trip or itinerary name.")
    destinations: list[LocationSchema] | None = F("Destinations covered by the itinerary.")
    days: list[ItineraryDaySchema] | None = F("Day-by-day plan.")
    travelers: list[TravelerSchema] | None = F("Travelers named in the itinerary.")
    transportation: list[TransportSchema] | None = F("Transport services included in the itinerary.")
    accommodations: list[AccommodationSchema] | None = F("Places to stay included in the itinerary.")
    activities: list[ActivityItemSchema] | None = F("Activities included in the itinerary.")
    scheduled_events: list[ActivityItemSchema] | None = F("Scheduled events such as meetings or tours.")
    start: DateTimeSchema | None = F("Itinerary start.")
    end: DateTimeSchema | None = F("Itinerary end.")
    remarks: str | None = F("Itinerary remarks.")


_MODULE = __name__


def _itinerary(name: str, document_type: str, description: str, **fields: tuple):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=ItineraryDocumentSchema,
        description=description,
        module=_MODULE,
        category="itinerary",
        fields=fields or None,
    )


TravelItinerarySchema = _itinerary(
    "TravelItinerarySchema",
    "travel_itinerary",
    "A general travel itinerary covering destinations, dates, transport, stays, and activities.",
)

MultiCityItinerarySchema = _itinerary(
    "MultiCityItinerarySchema",
    "multi_city_itinerary",
    "An itinerary that visits more than one city. Destinations are a list, not a single field.",
    city_count=(int | None, Field(default=None, ge=0, description="City count when the document states one.")),
)

TripPlanSchema = _itinerary(
    "TripPlanSchema",
    "trip_plan",
    "A trip plan, which may still be tentative.",
    planning_status=(str | None, F("Planning status as printed, such as draft or final.")),
    alternatives=(list[str] | None, F("Alternative arrangements mentioned in the plan.")),
)

DayWiseItinerarySchema = _itinerary(
    "DayWiseItinerarySchema",
    "day_wise_itinerary",
    "An itinerary organized day by day.",
    day_count=(int | None, Field(default=None, ge=0, description="Number of days when the document states it.")),
)

BusinessTravelItinerarySchema = _itinerary(
    "BusinessTravelItinerarySchema",
    "business_travel_itinerary",
    "An itinerary for a business trip, including the company and cost center when printed.",
    company=(OrganizationSchema | None, F("Company the traveler represents.")),
    cost_center=(str | None, F("Cost center as printed.")),
    purpose=(str | None, F("Business purpose as printed.")),
)

GroupTravelItinerarySchema = _itinerary(
    "GroupTravelItinerarySchema",
    "group_travel_itinerary",
    "An itinerary for a group of travelers.",
    group_name=(str | None, F("Group name.")),
    group_size=(int | None, Field(default=None, ge=0, description="Group size when the document states it.")),
    leader=(PersonSchema | None, F("Group leader when one is named.")),
)

TourItinerarySchema = _itinerary(
    "TourItinerarySchema",
    "tour_itinerary",
    "A tour operator's itinerary, including inclusions and exclusions when they are listed.",
    tour_name=(str | None, F("Tour name.")),
    tour_operator=(ProviderSchema | None, F("Tour operator.")),
    inclusions=(list[str] | None, F("Items the tour says are included.")),
    exclusions=(list[str] | None, F("Items the tour says are excluded.")),
)

ITINERARY_SCHEMAS = (
    TravelItinerarySchema,
    MultiCityItinerarySchema,
    TripPlanSchema,
    DayWiseItinerarySchema,
    BusinessTravelItinerarySchema,
    GroupTravelItinerarySchema,
    TourItinerarySchema,
)
