from typing import Any


class NightBreachError(Exception):
    """Base exception for expected NightBreach application errors."""

    code = "NIGHTBREACH_ERROR"
    message = "An application error occurred."
    status_code = 400

    def __init__(
        self,
        message: str | None = None,
        *,
        details: Any | None = None,
    ) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(NightBreachError):
    code = "RESOURCE_NOT_FOUND"
    message = "The requested resource was not found."
    status_code = 404


class AuthorizationError(NightBreachError):
    code = "ACCESS_DENIED"
    message = "Access to the requested resource is denied."
    status_code = 403


class AuthenticationError(NightBreachError):
    code = "AUTHENTICATION_REQUIRED"
    message = "Authentication is required."
    status_code = 401


class ValidationError(NightBreachError):
    code = "VALIDATION_ERROR"
    message = "The supplied data is invalid."
    status_code = 422


class ConflictError(NightBreachError):
    code = "CONFLICT"
    message = "The requested operation conflicts with the current state."
    status_code = 409
