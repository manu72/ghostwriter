"""
Unit tests for CLI display utilities.
"""

import pytest

from cli.display_utils import (
    get_author_source_type,
    get_author_type_short,
    get_author_type_full,
)
from core.models import AuthorProfile, AuthorSource, StyleGuide


class TestDisplayUtils:
    """Test display utility functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.historical_profile = AuthorProfile(
            author_id="test_historical",
            name="Test Historical Author",
            source_type=AuthorSource.HISTORICAL,
            style_guide=StyleGuide(),
        )

        self.manual_profile = AuthorProfile(
            author_id="test_manual",
            name="Test Manual Author",
            source_type=AuthorSource.MANUAL,
            style_guide=StyleGuide(),
        )

        # Create a profile without source_type to test fallback
        self.legacy_profile = AuthorProfile(
            author_id="test_legacy",
            name="Test Legacy Author",
            style_guide=StyleGuide(),
        )
        # Remove source_type to simulate older profiles
        if hasattr(self.legacy_profile, "source_type"):
            delattr(self.legacy_profile, "source_type")

    def test_get_author_source_type_historical(self):
        """Test source type extraction for historical profile."""
        source_type = get_author_source_type(self.historical_profile)
        assert source_type == AuthorSource.HISTORICAL

    def test_get_author_source_type_manual(self):
        """Test source type extraction for manual profile."""
        source_type = get_author_source_type(self.manual_profile)
        assert source_type == AuthorSource.MANUAL

    def test_get_author_source_type_fallback(self):
        """Test source type extraction fallback for legacy profiles."""
        source_type = get_author_source_type(self.legacy_profile)
        assert source_type == AuthorSource.MANUAL

    def test_get_author_type_short_with_profile_historical(self):
        """Test short display string with historical profile."""
        display = get_author_type_short(self.historical_profile)
        assert display == "🏛️ Hist"

    def test_get_author_type_short_with_profile_manual(self):
        """Test short display string with manual profile."""
        display = get_author_type_short(self.manual_profile)
        assert display == "👤 Man"

    def test_get_author_type_short_with_profile_legacy(self):
        """Test short display string with legacy profile."""
        display = get_author_type_short(self.legacy_profile)
        assert display == "👤 Man"

    def test_get_author_type_short_with_string_historical(self):
        """Test short display string with historical string."""
        display = get_author_type_short(AuthorSource.HISTORICAL)
        assert display == "🏛️ Hist"

    def test_get_author_type_short_with_string_manual(self):
        """Test short display string with manual string."""
        display = get_author_type_short(AuthorSource.MANUAL)
        assert display == "👤 Man"

    def test_get_author_type_short_with_raw_string_historical(self):
        """Test short display string with raw string 'historical'."""
        display = get_author_type_short("historical")
        assert display == "🏛️ Hist"

    def test_get_author_type_short_with_raw_string_manual(self):
        """Test short display string with raw string 'manual'."""
        display = get_author_type_short("manual")
        assert display == "👤 Man"

    def test_get_author_type_full_with_profile_historical(self):
        """Test full display string with historical profile."""
        display = get_author_type_full(self.historical_profile)
        assert display == "🏛️ Historical Figure"

    def test_get_author_type_full_with_profile_manual(self):
        """Test full display string with manual profile."""
        display = get_author_type_full(self.manual_profile)
        assert display == "👤 Manual Creation"

    def test_get_author_type_full_with_profile_legacy(self):
        """Test full display string with legacy profile."""
        display = get_author_type_full(self.legacy_profile)
        assert display == "👤 Manual Creation"

    def test_get_author_type_full_with_string_historical(self):
        """Test full display string with historical string."""
        display = get_author_type_full(AuthorSource.HISTORICAL)
        assert display == "🏛️ Historical Figure"

    def test_get_author_type_full_with_string_manual(self):
        """Test full display string with manual string."""
        display = get_author_type_full(AuthorSource.MANUAL)
        assert display == "👤 Manual Creation"

    def test_get_author_type_full_with_raw_string_historical(self):
        """Test full display string with raw string 'historical'."""
        display = get_author_type_full("historical")
        assert display == "🏛️ Historical Figure"

    def test_get_author_type_full_with_raw_string_manual(self):
        """Test full display string with raw string 'manual'."""
        display = get_author_type_full("manual")
        assert display == "👤 Manual Creation"

    def test_consistency_between_short_and_full(self):
        """Test that short and full versions are consistent."""
        # Test with various inputs to ensure consistency
        test_inputs = [
            self.historical_profile,
            self.manual_profile,
            AuthorSource.HISTORICAL,
            AuthorSource.MANUAL,
            "historical",
            "manual",
        ]

        for input_data in test_inputs:
            short = get_author_type_short(input_data)
            full = get_author_type_full(input_data)

            # Both should use same emoji
            if "🏛️" in short:
                assert "🏛️" in full
            elif "👤" in short:
                assert "👤" in full
            else:
                pytest.fail(f"Unexpected emoji in short display: {short}")
