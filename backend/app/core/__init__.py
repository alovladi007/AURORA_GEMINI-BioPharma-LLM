"""
Core module for Pharma AI Platform.

Contains configuration, security, database setup, and shared utilities.
"""

from app.core.config import settings, get_settings

__all__ = ["settings", "get_settings"]
