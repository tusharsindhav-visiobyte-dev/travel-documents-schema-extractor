"""Dates, times, and timezones as they appear on travel documents.

Normalized parts are filled only when the source value is unambiguous.
Original strings are kept so a later reviewer can see the printed text.
Departure and arrival each carry their own timezone fields.
"""

from __future__ import annotations

from datetime import date, datetime, time

from pydantic import Field, field_validator

from schemas.base.base_models import F, SchemaModel
from schemas.base.validators import (
    validate_iana_timezone,
    validate_naive_local_datetime,
    validate_utc_datetime,
    validate_utc_offset,
)


class TimezoneSchema(SchemaModel):
    """A timezone attached to a place or an event, independent of a clock time."""

    iana_name: str | None = F("IANA timezone name such as Asia/Kolkata. Null when unknown.")
    abbreviation_original: str | None = F(
        "Timezone abbreviation as printed. Abbreviations such as IST or CST are ambiguous and are not resolved."
    )
    utc_offset_original: str | None = F("UTC offset as printed, for example +05:30.")
    utc_offset_minutes: int | None = Field(
        default=None,
        ge=-840,
        le=840,
        description="UTC offset in minutes when the document states an offset. Range is -14:00 to +14:00.",
    )
    timezone_known: bool | None = F(
        "True only when the timezone is explicitly known. False when it is explicitly unknown. Null when unspecified."
    )
    original_label: str | None = F("Timezone label exactly as it appeared on the document.")

    @field_validator("iana_name")
    @classmethod
    def _iana_name(cls, value: str | None) -> str | None:
        return validate_iana_timezone(value)

    @field_validator("utc_offset_original")
    @classmethod
    def _offset(cls, value: str | None) -> str | None:
        return validate_utc_offset(value)


class DateTimeSchema(SchemaModel):
    """A date and time that may be partial, local, or tied to an unknown zone.

    Do not invent a normalized date from an ambiguous printed string.
    Do not invent a clock time when the document only shows a date.
    Do not assume this value shares a timezone with another leg of the journey.
    """

    original_date: str | None = F("Date text exactly as printed. Ambiguous forms stay here unparsed.")
    normalized_date: date | None = F("Calendar date only when the printed date has one unambiguous reading.")
    original_time: str | None = F("Time text exactly as printed.")
    normalized_local_time: time | None = F("Local clock time only when the printed time is unambiguous.")
    iana_timezone: str | None = F("IANA timezone for this instant. Null when the zone is unknown.")
    utc_offset: str | None = F("UTC offset as printed for this instant, such as +05:30.")
    utc_offset_minutes: int | None = Field(
        default=None,
        ge=-840,
        le=840,
        description="UTC offset in minutes when an offset is explicitly known.",
    )
    local_datetime: datetime | None = F(
        "Naive local date and time when both parts are known. This field never carries a timezone."
    )
    utc_datetime: datetime | None = F(
        "Absolute UTC instant when the local time and timezone are both known. Never guessed."
    )
    timezone_known: bool | None = F(
        "True only when this value's timezone is explicitly known. False when unknown. Null when unspecified."
    )
    original_timezone_label: str | None = F("Timezone text exactly as printed, including ambiguous abbreviations.")
    date_only: bool | None = F("True when the document provides a date and no clock time.")
    time_unknown: bool | None = F("True when the clock time was not on the document.")
    ambiguity_notes: str | None = F("Why a normalized date, time, or timezone was left empty.")

    @field_validator("iana_timezone")
    @classmethod
    def _iana_timezone(cls, value: str | None) -> str | None:
        return validate_iana_timezone(value)

    @field_validator("utc_offset")
    @classmethod
    def _utc_offset(cls, value: str | None) -> str | None:
        return validate_utc_offset(value)

    @field_validator("local_datetime")
    @classmethod
    def _local_datetime(cls, value: datetime | None) -> datetime | None:
        return validate_naive_local_datetime(value)

    @field_validator("utc_datetime")
    @classmethod
    def _utc_datetime(cls, value: datetime | None) -> datetime | None:
        return validate_utc_datetime(value)
