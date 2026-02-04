"""Task Flow Configuration Management Module

This module provides automatic template integration for task-flow,
including project initialization, template loading, and content merging.
"""

from __future__ import annotations

from .manager import ConfigManager
from .template_loader import TemplateLoader
from .content_merger import ContentMerger
from .template_renderer import TemplateRenderer
from .exceptions import (
    ConfigError,
    TemplateNotFoundError,
    FileWriteError,
    VersionParseError,
)

__all__ = [
    'ConfigManager',
    'TemplateLoader',
    'ContentMerger',
    'TemplateRenderer',
    'ConfigError',
    'TemplateNotFoundError',
    'FileWriteError',
    'VersionParseError',
]

__version__ = '2.3.0'