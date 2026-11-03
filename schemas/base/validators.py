"""Small validators shared by schema fields.

Validators reject values that are structurally impossible. They do not
rewrite ambiguous document text into a normalized form.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_CURRENCY_CODE = re.compile(r"^[A-Za-z]{3}$")
_COUNTRY_CODE = re.compile(r"^[A-Za-z]{2}$")
_IATA_AIRPORT = re.compile(r"^[A-Za-z]{3}$")
_ICAO_AIRPORT = re.compile(r"^[A-Za-z]{4}$")
_IATA_AIRLINE = re.compile(r"^[A-Za-z0-9]{2}$")
_ICAO_AIRLINE = re.compile(r"^[A-Za-z]{3}$")
_UTC_OFFSET = re.compile(r"^[+-](?:0\d|1[0-4]):[0-5]\d$")
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ISO_TIME = re.compile(r"^\d{2}:\d{2}(?::\d{2})?$")
_CARD_LAST_FOUR = re.compile(r"^\d{4}$")


def reject_blank(value: str | None, field_label: str) -> str | None:
    """Reject empty strings without trimming a non-empty extracted value."""
    if value is None:
        return None
    if value.strip() == "":
        raise ValueError(
            f"{field_label} cannot be blank. Omit the field when the value is unknown."
        )
    return value


def validate_iana_timezone(value: str | None) -> str | None:
    """Accept a real IANA name and leave unknown timezones unfilled."""
    if value is None:
        return None
    if value.strip() == "":
        raise ValueError(
            "IANA timezone cannot be blank. Leave it null when the timezone is unknown."
        )
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f"Unknown IANA timezone '{value}'. "
            "Leave the timezone null when it is unknown or ambiguous."
        ) from exc
    return value


def validate_utc_offset(value: str | None) -> str | None:
    if value is None:
        return None
    if not _UTC_OFFSET.fullmatch(value):
        raise ValueError(
            "UTC offset must look like +05:30 or -04:00 and stay within -14:00 to +14:00."
        )
    return value


def validate_currency_code(value: str | None) -> str | None:
    if value is None:
        return None
    if not _CURRENCY_CODE.fullmatch(value):
        raise ValueError(
            "currency_code must be a 3-letter ISO 4217 code when it is known. "
            "Preserve symbols and local names in currency_original instead."
        )
    return value


def validate_country_code(value: str | None) -> str | None:
    if value is None:
        return None
    if not _COUNTRY_CODE.fullmatch(value):
        raise ValueError(
            "Country code must be a 2-letter ISO code when supplied. "
            "Preserve the printed country name separately."
        )
    return value


def validate_iata_airport(value: str | None) -> str | None:
    if value is None:
        return None
    if not _IATA_AIRPORT.fullmatch(value):
        raise ValueError("IATA airport code must be three letters when supplied.")
    return value


def validate_icao_airport(value: str | None) -> str | None:
    if value is None:
        return None
    if not _ICAO_AIRPORT.fullmatch(value):
        raise ValueError("ICAO airport code must be four letters when supplied.")
    return value


def validate_iata_airline(value: str | None) -> str | None:
    if value is None:
        return None
    if not _IATA_AIRLINE.fullmatch(value):
        raise ValueError("IATA airline code must be two letters or digits when supplied.")
    return value


def validate_icao_airline(value: str | None) -> str | None:
    if value is None:
        return None
    if not _ICAO_AIRLINE.fullmatch(value):
        raise ValueError("ICAO airline code must be three letters when supplied.")
    return value


def validate_card_last_four(value: str | None) -> str | None:
    if value is None:
        return None
    if not _CARD_LAST_FOUR.fullmatch(value):
        raise ValueError("card_last_four must be exactly four digits when supplied.")
    return value


def validate_naive_local_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None:
        raise ValueError(
            "local_datetime must be timezone-naive. "
            "Store an IANA timezone or UTC offset beside it, and store an absolute "
            "instant only in utc_datetime."
        )
    return value


def validate_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(
            "utc_datetime must be timezone-aware and expressed in UTC. "
            "Do not guess a timezone for a naive datetime."
        )
    return value


def is_iso_date(value: str | None) -> bool:
    return bool(value and _ISO_DATE.fullmatch(value))


def is_iso_time(value: str | None) -> bool:
    return bool(value and _ISO_TIME.fullmatch(value))
