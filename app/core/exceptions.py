from typing import Any, Optional


class ClimateTwinException(Exception):
    """Base exception for all ClimateTwin AI backend errors."""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details


class DataIngestionError(ClimateTwinException):
    """Raised when an external environmental API query fails."""
    pass


class MissingDataError(ClimateTwinException):
    """Raised when essential environmental data is missing and cannot be imputed."""
    pass


class ModelInferenceError(ClimateTwinException):
    """Raised when ML engine prediction fails."""
    pass


class LocationNotFoundError(ClimateTwinException):
    """Raised when requested coordinates or city/ward are unknown."""
    pass

