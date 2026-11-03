"""A travel event derived from one or more documents.

This schema is intentionally not a document schema. A single uploaded
document can be the source of several events, and an event can cite
several source documents.
"""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from events.event_types import EventStatus, EventType
from schemas.base.base_models import ExtensionScalar, F, SchemaModel
from schemas.common.datetime import DateTimeSchema, TimezoneSchema
from schemas.common.location import LocationSchema

EVENT_SCHEMA_VERSION = "1.0.0"


class TravelEventSchema(SchemaModel):
    """An actionable trip activity such as a departure, check-in, or expiry.

    ``event_type`` is required so an event has a kind. Times, places, and
    traveler links stay optional because a derived event may be incomplete.
    """

    event_id: str | None = F("Application identifier for this event.")
    trip_id: str | None = F("Trip this event belongs to.")
    event_type: EventType = Field(..., description="Standardized kind of travel activity.")
    event_type_original: str | None = F(
        "Source label for the event when it does not map cleanly. Use event_type 'other' in that case."
    )
    title: str | None = F("Short event title.")
    description: str | None = F("Event description.")
    start_datetime: DateTimeSchema | None = F("When the event starts. Unknown clock times stay empty.")
    end_datetime: DateTimeSchema | None = F("When the event ends.")
    timezone: TimezoneSchema | None = F("Timezone of the event location. It is separate from each datetime.")
    location: LocationSchema | None = F("Where the event starts or takes place.")
    destination: LocationSchema | None = F("Where a departure event is going, when that place is known.")
    source_document_ids: list[str] | None = F("Documents this event was derived from.")
    traveler_ids: list[str] | None = F("Travelers this event applies to.")
    event_status: EventStatus | None = F("Status of the event.")
    schema_version: Literal["1.0.0"] = Field(
        default=EVENT_SCHEMA_VERSION,
        description="Schema version of the travel event record.",
    )
    provider_extensions: dict[str, ExtensionScalar] | None = F(
        "Provider-specific scalars. Nested objects are rejected."
    )

    SCHEMA_VERSION: ClassVar[str] = EVENT_SCHEMA_VERSION
    SCHEMA_DESCRIPTION: ClassVar[str] = (
        "An actionable travel activity derived from one or more documents."
    )
