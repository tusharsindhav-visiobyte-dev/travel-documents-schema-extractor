"""Train document schemas."""

from schemas.train.models import (
    TRAIN_SCHEMAS,
    RailPassSchema,
    RailwayReservationSchema,
    TrainBookingConfirmationSchema,
    TrainCancellationSchema,
    TrainDocumentSchema,
    TrainRescheduleSchema,
    TrainSegmentSchema,
    TrainTicketSchema,
)

__all__ = [
    "TRAIN_SCHEMAS",
    "RailPassSchema",
    "RailwayReservationSchema",
    "TrainBookingConfirmationSchema",
    "TrainCancellationSchema",
    "TrainDocumentSchema",
    "TrainRescheduleSchema",
    "TrainSegmentSchema",
    "TrainTicketSchema",
]
