class AppError(Exception):
    """Base class for all app-level exceptions."""

    pass


class ValidationError(AppError):
    """Raised when user input or domain rules are violated."""

    pass


class NotFoundError(AppError):
    """Raised when a requested entity doesn't exist."""

    pass
