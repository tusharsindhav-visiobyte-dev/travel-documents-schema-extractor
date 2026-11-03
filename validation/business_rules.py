"""Business checks that report problems without discarding extracted data.

These rules never rewrite a document. A missing night count stays missing.
An ambiguous date is not reinterpreted. Departure and arrival are compared
only when both values can be placed on the same timeline.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, time
from typing import Protocol
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from schemas.base.validators import is_iso_date, is_iso_time
from schemas.common.datetime import DateTimeSchema


@dataclass(frozen=True)
class BusinessFinding:
    """A business-rule result. The source value is left unchanged."""

    code: str
    message: str
    field_path: str | None = None
    severity: str = "warning"


class BusinessRule(Protocol):
    """A hook that inspects a validated model and returns findings."""

    code: str

    def evaluate(self, model: BaseModel) -> list[BusinessFinding]:
        """Return findings for this model. Do not mutate the model."""


_INTERVALS = (
    ("departure", "arrival"),
    ("check_in", "check_out"),
    ("pickup", "return_datetime"),
    ("pickup", "dropoff"),
    ("coverage_start", "coverage_end"),
    ("start", "end"),
    ("valid_from", "valid_until"),
    ("validity_start", "validity_end"),
    ("trip_start", "trip_end"),
    ("service_period_start", "service_period_end"),
    ("previous_check_in", "previous_check_out"),
    ("revised_check_in", "revised_check_out"),
)

_CUSTOM: list[tuple[BusinessRule, set[str] | None]] = []


def register_business_rule(
    rule: BusinessRule,
    document_types: set[str] | None = None,
) -> None:
    """Register an additional rule. Built-in rules always run."""
    _CUSTOM.append((rule, document_types))


def reset_custom_business_rules() -> None:
    """Remove rules added with ``register_business_rule``."""
    _CUSTOM.clear()


def run_business_rules(model: BaseModel) -> list[BusinessFinding]:
    """Run built-in and custom rules. Findings do not change the model."""
    document_type = getattr(model, "DOCUMENT_TYPE", None)
    if document_type is None and hasattr(model, "document_type"):
        raw = model.document_type
        document_type = getattr(raw, "value", raw)
    findings: list[BusinessFinding] = []
    for rule in _BUILTIN_RULES:
        findings.extend(rule.evaluate(model))
    for rule, allowed in _CUSTOM:
        if allowed is None or document_type in allowed:
            findings.extend(rule.evaluate(model))
    return findings


def _walk(model: BaseModel, path: str = ""):
    yield path, model
    for name in model.__class__.model_fields:
        value = getattr(model, name)
        child = f"{path}.{name}" if path else name
        if isinstance(value, BaseModel):
            yield from _walk(value, child)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, BaseModel):
                    yield from _walk(item, f"{child}[{index}]")


def _aware(dt: DateTimeSchema) -> datetime | None:
    """Return a comparable instant only when the timezone is actually known."""
    if dt.utc_datetime is not None:
        return dt.utc_datetime
    if not dt.iana_timezone:
        return None
    if dt.local_datetime is not None:
        return dt.local_datetime.replace(tzinfo=ZoneInfo(dt.iana_timezone))
    if dt.normalized_date is not None and dt.normalized_local_time is not None:
        local = datetime.combine(dt.normalized_date, dt.normalized_local_time)
        return local.replace(tzinfo=ZoneInfo(dt.iana_timezone))
    return None


def _date_only(dt: DateTimeSchema) -> bool:
    return (
        dt.normalized_date is not None
        and dt.normalized_local_time is None
        and dt.local_datetime is None
        and dt.utc_datetime is None
    )


class DateTimeConsistencyRule:
    """Report contradictions inside one date-time value."""

    code = "datetime_consistency"

    def evaluate(self, model: BaseModel) -> list[BusinessFinding]:
        findings: list[BusinessFinding] = []
        for path, current in _walk(model):
            if not isinstance(current, DateTimeSchema):
                continue
            findings.extend(self._check(path, current))
        return findings

    def _check(self, path: str, value: DateTimeSchema) -> list[BusinessFinding]:
        findings: list[BusinessFinding] = []
        zone_known = value.timezone_known is True
        has_zone = any(
            (
                value.iana_timezone,
                value.utc_offset,
                value.utc_offset_minutes is not None,
            )
        )
        if zone_known and not has_zone:
            findings.append(
                BusinessFinding(
                    code="timezone_marked_known_without_zone",
                    field_path=path or "datetime",
                    message="timezone_known is true but no IANA timezone or UTC offset is present.",
                )
            )
        if (
            value.normalized_date is not None
            and value.local_datetime is not None
            and value.local_datetime.date() != value.normalized_date
        ):
            findings.append(
                BusinessFinding(
                    code="normalized_date_mismatch",
                    field_path=path or "datetime",
                    message="normalized_date does not match the date in local_datetime.",
                )
            )
        if (
            value.normalized_local_time is not None
            and value.local_datetime is not None
            and value.local_datetime.time().replace(microsecond=0)
            != value.normalized_local_time.replace(microsecond=0)
        ):
            findings.append(
                BusinessFinding(
                    code="normalized_time_mismatch",
                    field_path=path or "datetime",
                    message="normalized_local_time does not match the time in local_datetime.",
                )
            )
        if is_iso_date(value.original_date) and value.normalized_date is not None:
            if value.original_date != value.normalized_date.isoformat():
                findings.append(
                    BusinessFinding(
                        code="original_iso_date_mismatch",
                        field_path=path or "datetime",
                        message=(
                            "original_date is an ISO date and does not match normalized_date. "
                            "Ambiguous non-ISO dates are not compared."
                        ),
                    )
                )
        if is_iso_time(value.original_time) and value.normalized_local_time is not None:
            if not _iso_time_matches(value.original_time, value.normalized_local_time):
                findings.append(
                    BusinessFinding(
                        code="original_iso_time_mismatch",
                        field_path=path or "datetime",
                        message="original_time is an ISO time and does not match normalized_local_time.",
                    )
                )
        return findings


class IntervalOrderRule:
    """Warn when two comparable endpoints are out of order.

    Local times in unknown or different unknown zones are not compared.
    """

    code = "interval_order"

    def evaluate(self, model: BaseModel) -> list[BusinessFinding]:
        findings: list[BusinessFinding] = []
        for path, current in _walk(model):
            fields = current.__class__.model_fields
            for start_name, end_name in _INTERVALS:
                if start_name not in fields or end_name not in fields:
                    continue
                start = getattr(current, start_name)
                end = getattr(current, end_name)
                if not isinstance(start, DateTimeSchema) or not isinstance(end, DateTimeSchema):
                    continue
                finding = self._compare(path, start_name, end_name, start, end)
                if finding is not None:
                    findings.append(finding)
        return findings

    def _compare(
        self,
        path: str,
        start_name: str,
        end_name: str,
        start: DateTimeSchema,
        end: DateTimeSchema,
    ) -> BusinessFinding | None:
        start_instant = _aware(start)
        end_instant = _aware(end)
        field_path = f"{path}.{end_name}" if path else end_name
        if start_instant is not None and end_instant is not None:
            if end_instant < start_instant:
                return BusinessFinding(
                    code="interval_ends_before_start",
                    field_path=field_path,
                    message=(
                        f"{end_name} is earlier than {start_name} when both are placed on a known timeline."
                    ),
                )
            return None
        if _date_only(start) and _date_only(end) and end.normalized_date < start.normalized_date:
            return BusinessFinding(
                code="interval_ends_before_start",
                field_path=field_path,
                message=f"{end_name} date is earlier than {start_name} date.",
            )
        return None


class StayCountRule:
    """Report disagreements between stated counts and stated dates or guest lists."""

    code = "stay_counts"

    def evaluate(self, model: BaseModel) -> list[BusinessFinding]:
        findings: list[BusinessFinding] = []
        for path, current in _walk(model):
            fields = current.__class__.model_fields
            if "guest_count" in fields and "guests" in fields:
                count = current.guest_count
                guests = current.guests
                if count is not None and guests is not None and count != len(guests):
                    findings.append(
                        BusinessFinding(
                            code="guest_count_mismatch",
                            field_path=f"{path}.guest_count" if path else "guest_count",
                            message="guest_count does not match the number of guest records.",
                        )
                    )
            if "number_of_nights" in fields and "check_in" in fields and "check_out" in fields:
                nights = current.number_of_nights
                check_in = current.check_in
                check_out = current.check_out
                if (
                    nights is not None
                    and isinstance(check_in, DateTimeSchema)
                    and isinstance(check_out, DateTimeSchema)
                    and check_in.normalized_date is not None
                    and check_out.normalized_date is not None
                ):
                    stated_span = (check_out.normalized_date - check_in.normalized_date).days
                    if nights != stated_span:
                        findings.append(
                            BusinessFinding(
                                code="night_count_mismatch",
                                field_path=f"{path}.number_of_nights" if path else "number_of_nights",
                                message=(
                                    "number_of_nights does not match the normalized check-in and check-out dates. "
                                    "The stated night count was kept."
                                ),
                            )
                        )
        return findings


def _iso_time_matches(original: str | None, clock: time) -> bool:
    if not original:
        return True
    parts = original.split(":")
    if len(parts) < 2:
        return True
    if int(parts[0]) != clock.hour or int(parts[1]) != clock.minute:
        return False
    if len(parts) > 2 and int(parts[2]) != clock.second:
        return False
    return True


_BUILTIN_RULES: tuple[BusinessRule, ...] = (
    DateTimeConsistencyRule(),
    IntervalOrderRule(),
    StayCountRule(),
)

# Imported by tests that want a tiny callable rule without a class.
RuleFunction = Callable[[BaseModel], list[BusinessFinding]]
