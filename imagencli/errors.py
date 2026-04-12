"""Typed CLI/application errors."""


class ImagenError(Exception):
    """Base application error for user-safe failures."""


class ConfigError(ImagenError):
    """Raised when runtime configuration is invalid."""


class ValidationError(ImagenError):
    """Raised when user input fails local validation."""


class ProviderError(ImagenError):
    """Raised when provider integration fails."""


class ResponseFormatError(ImagenError):
    """Raised when provider response payload is malformed."""


class InstallError(ImagenError):
    """Raised when local installation tasks fail."""
