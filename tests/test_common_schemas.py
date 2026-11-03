"""Tests for reusable travel entities."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from schemas.common.datetime import DateTimeSchema, TimezoneSchema
from schemas.common.identification import IdentificationSchema
from schemas.common.location import AirportSchema
from schemas.common.passenger import PassengerSchema
from schemas.common.payment import CurrencySchema, PaymentSchema
from schemas.common.person import PersonSchema
from schemas.flight import FlightSegmentSchema


def test_ambiguous_date_is_preserved_without_a_guess():
    value = DateTimeSchema(original_date="03/04/2026", original_time="evening")
    assert value.original_date == "03/04/2026"
    assert value.normalized_date is None
    assert value.normalized_local_time is None
    assert value.iana_timezone is None


def test_unknown_timezone_is_valid_and_invalid_iana_names_are_rejected():
    unknown = DateTimeSchema(original_date="15 Nov 2026", timezone_known=False)
    assert unknown.timezone_known is False
    with pytest.raises(ValidationError):
        DateTimeSchema(iana_timezone="IST")
    with pytest.raises(ValidationError):
        DateTimeSchema(iana_timezone="Not/AZone")
    known = TimezoneSchema(iana_name="Asia/Kolkata", timezone_known=True)
    assert known.iana_name == "Asia/Kolkata"


def test_local_and_utc_datetimes_keep_their_roles():
    local = DateTimeSchema(local_datetime="2026-11-15T21:30:00")
    assert local.local_datetime.tzinfo is None
    with pytest.raises(ValidationError):
        DateTimeSchema(local_datetime="2026-11-15T21:30:00+05:30")
    with pytest.raises(ValidationError):
        DateTimeSchema(utc_datetime="2026-11-15T16:00:00")
    utc = DateTimeSchema(utc_datetime="2026-11-15T16:00:00Z")
    assert utc.utc_datetime == datetime(2026, 11, 15, 16, 0, tzinfo=timezone.utc)


def test_departure_and_arrival_timezones_are_independent():
    segment = FlightSegmentSchema(
        flight_number="EX101",
        departure={"iana_timezone": "Europe/London", "original_date": "15 Nov 2026"},
        arrival={"iana_timezone": "Asia/Kolkata", "original_date": "16 Nov 2026"},
        overnight_journey=True,
        international=True,
    )
    assert segment.departure.iana_timezone == "Europe/London"
    assert segment.arrival.iana_timezone == "Asia/Kolkata"


def test_person_and_identification_fields_are_optional():
    assert PersonSchema().name is None
    identification = IdentificationSchema()
    assert identification.identification_number is None
    assert identification.nationality is None


def test_passenger_can_be_partial():
    passenger = PassengerSchema(name={"original_name": "Ada Lovelace"}, ticket_number=None, seat=None)
    assert passenger.name.original_name == "Ada Lovelace"
    assert passenger.passenger_type is None


def test_currency_preserves_original_text_and_checks_codes():
    amount = CurrencySchema(original_amount_text="Rs 1,250", currency_original="Rs")
    assert amount.amount is None
    assert amount.currency_code is None
    with pytest.raises(ValidationError):
        CurrencySchema(currency_code="RUPEE")
    coded = CurrencySchema(amount="1250.50", currency_code="INR")
    assert str(coded.amount) == "1250.50"


def test_airport_codes_and_card_last_four_are_checked_only_when_present():
    assert AirportSchema(name="Indira Gandhi International").iata_code is None
    with pytest.raises(ValidationError):
        AirportSchema(iata_code="DELHI")
    with pytest.raises(ValidationError):
        PaymentSchema(card_last_four="4111111111111111")
    payment = PaymentSchema(card_last_four="4242")
    assert payment.card_last_four == "4242"


def test_utc_offset_must_be_explicit():
    value = DateTimeSchema(utc_offset="+05:30", utc_offset_minutes=330)
    assert value.utc_offset_minutes == 330
    with pytest.raises(ValidationError):
        DateTimeSchema(utc_offset="5:30")
    with pytest.raises(ValidationError):
        DateTimeSchema(utc_offset_minutes=900)
