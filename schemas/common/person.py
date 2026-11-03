"""A person named on a travel document."""

from __future__ import annotations

from schemas.base.base_models import F, SchemaModel
from schemas.common.contact import ContactSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.identification import IdentificationSchema


class PersonNameSchema(SchemaModel):
    """A personal name. Split parts only when the document shows them separately."""

    original_name: str | None = F("Full name exactly as printed.")
    full_name: str | None = F("Display name when the document shows a single name line.")
    title: str | None = F("Courtesy title as printed.")
    given_names: str | None = F("Given names only when the split is shown or otherwise unambiguous.")
    middle_names: str | None = F("Middle names only when they are separately shown.")
    family_name: str | None = F("Family name only when the split is shown or otherwise unambiguous.")


class PersonSchema(SchemaModel):
    """A person. Every field is optional so a partial name can still be stored."""

    person_id: str | None = F("Application identifier for this person.")
    name: PersonNameSchema | None = F("Name of the person.")
    date_of_birth: DateTimeSchema | None = F("Date of birth when the document shows one.")
    gender: str | None = F("Gender text as printed. It is not forced into a fixed list.")
    contact: ContactSchema | None = F("Contact details for this person.")
    identification_documents: list[IdentificationSchema] | None = F(
        "Identification documents mentioned for this person. Numbers stay optional."
    )
