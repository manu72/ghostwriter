"""
Display utilities for consistent CLI formatting.

This module provides helper functions for consistent display formatting
across different CLI commands and views.
"""

from typing import Union

from core.models import AuthorProfile, AuthorSource


def get_author_source_type(profile: AuthorProfile) -> str:
    """Get the author source type with fallback for older profiles.

    Args:
        profile: The author profile

    Returns:
        The source type as a string ("manual" or "historical")
    """
    return getattr(profile, "source_type", AuthorSource.MANUAL)


def get_author_type_short(profile_or_source: Union[AuthorProfile, str]) -> str:
    """Get short author type display string for table views.

    Args:
        profile_or_source: Either an AuthorProfile or source type string

    Returns:
        Short display string: "🏛️ Hist" for historical, "👤 Man" for manual
    """
    if isinstance(profile_or_source, str):
        source_type = profile_or_source
    else:
        source_type = get_author_source_type(profile_or_source)

    return "🏛️ Hist" if source_type == AuthorSource.HISTORICAL else "👤 Man"


def get_author_type_full(profile_or_source: Union[AuthorProfile, str]) -> str:
    """Get full author type display string for detailed views.

    Args:
        profile_or_source: Either an AuthorProfile or source type string

    Returns:
        Full display string: "🏛️ Historical Figure" or "👤 Manual Creation"
    """
    if isinstance(profile_or_source, str):
        source_type = profile_or_source
    else:
        source_type = get_author_source_type(profile_or_source)

    return (
        "🏛️ Historical Figure"
        if source_type == AuthorSource.HISTORICAL
        else "👤 Manual Creation"
    )
