"""Exceptions for Task Flow configuration management"""

from typing import Optional


class ConfigError(Exception):
    """Base exception for configuration-related errors"""

    def __init__(self, message: str, context: Optional[dict[str, str]] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        msg = self.message
        if self.context:
            details = ", ".join(f"{k}={v}" for k, v in self.context.items())
            msg = f"{msg} ({details})"
        return msg


class TemplateNotFoundError(ConfigError):
    """Raised when a template file cannot be found"""

    def __init__(self, template_name: str, template_dir: str, available: list[str]):
        super().__init__(
            f"Template '{template_name}' not found",
            {
                "template_dir": template_dir,
                "available": ", ".join(available),
            }
        )
        self.template_name = template_name
        self.template_dir = template_dir
        self.available = available


class FileWriteError(ConfigError):
    """Raised when writing to a file fails"""

    def __init__(self, file_path: str, reason: str):
        super().__init__(
            f"Failed to write to file",
            {
                "file": file_path,
                "reason": reason,
            }
        )
        self.file_path = file_path
        self.reason = reason


class VersionParseError(ConfigError):
    """Raised when version parsing fails"""

    def __init__(self, version_string: str, reason: str):
        super().__init__(
            f"Invalid version format",
            {
                "version": version_string,
                "reason": reason,
            }
        )
        self.version_string = version_string
        self.reason = reason
