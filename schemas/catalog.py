"""Built-in document schemas in registration order."""

from __future__ import annotations

from collections.abc import Iterator

from schemas.activities.models import ACTIVITY_SCHEMAS
from schemas.bus.models import BUS_SCHEMAS
from schemas.corporate.models import CORPORATE_SCHEMAS
from schemas.cruise.models import CRUISE_SCHEMAS
from schemas.financial.models import FINANCIAL_SCHEMAS
from schemas.flight.models import FLIGHT_SCHEMAS
from schemas.hotel.models import HOTEL_SCHEMAS
from schemas.identity.models import IDENTITY_SCHEMAS
from schemas.insurance.models import INSURANCE_SCHEMAS
from schemas.itinerary.models import ITINERARY_SCHEMAS
from schemas.road.models import ROAD_SCHEMAS
from schemas.special.models import SPECIAL_SCHEMAS
from schemas.train.models import TRAIN_SCHEMAS
from schemas.transfers.models import TRANSFER_SCHEMAS

ALL_DOCUMENT_SCHEMAS = (
    *FLIGHT_SCHEMAS,
    *HOTEL_SCHEMAS,
    *TRAIN_SCHEMAS,
    *BUS_SCHEMAS,
    *ROAD_SCHEMAS,
    *ITINERARY_SCHEMAS,
    *IDENTITY_SCHEMAS,
    *INSURANCE_SCHEMAS,
    *CRUISE_SCHEMAS,
    *ACTIVITY_SCHEMAS,
    *TRANSFER_SCHEMAS,
    *FINANCIAL_SCHEMAS,
    *CORPORATE_SCHEMAS,
    *SPECIAL_SCHEMAS,
)


def iter_builtin_schemas() -> Iterator[type]:
    """Yield each specialized document schema class once."""
    yield from ALL_DOCUMENT_SCHEMAS
