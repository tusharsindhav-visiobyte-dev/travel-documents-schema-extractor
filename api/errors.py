"""Errors raised while reading or classifying a document."""


class DocumentInputError(Exception):
    """The caller did not supply readable document text."""


class UnsupportedFileError(DocumentInputError):
    """The upload is not a text file or a PDF."""


class UnrecognizedDocumentTypeError(Exception):
    """The model did not return a registered document type."""

    def __init__(self, candidate: str | None) -> None:
        self.candidate = candidate
        shown = candidate if candidate else "an empty value"
        super().__init__(f"The model returned {shown}, which is not a registered document type.")


class ModelUnavailableError(Exception):
    """The language model could not be reached or did not return a usable response."""
