"""Derived travel events. These are not travel document schemas."""

from events.event_schema import EVENT_SCHEMA_VERSION, TravelEventSchema
from events.event_types import EventStatus, EventType

__all__ = [
    "EVENT_SCHEMA_VERSION",
    "EventStatus",
    "EventType",
    "TravelEventSchema",
]
