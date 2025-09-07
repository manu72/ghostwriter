from datetime import datetime
from unittest.mock import patch

import pytest

from core.storage import AuthorStorage


class TestAuthorStorageContent:
    """Test content-related functionality of AuthorStorage."""

    def test_content_directory_created_on_init(self, temp_data_dir, mock_settings):
        """Test that content directory is created when AuthorStorage is initialized."""
        with patch("core.storage.settings", mock_settings):
            storage = AuthorStorage("test_author")

            # Content directory should exist
            content_dir = storage.content_dir
            assert content_dir.exists()
            assert content_dir.is_dir()
            assert content_dir.parent == storage.author_dir

    def test_content_dir_property(self, temp_data_dir, mock_settings):
        """Test content_dir property returns correct path."""
        with patch("core.storage.settings", mock_settings):
            storage = AuthorStorage("test_author")

            expected_path = storage.author_dir / "content"
            assert storage.content_dir == expected_path

    def test_save_generated_content(self, temp_data_dir, mock_settings):
        """Test saving generated content."""
        with patch("core.storage.settings", mock_settings):
            storage = AuthorStorage("test_author")

            timestamp = datetime(2023, 1, 15, 14, 30, 45)

            content_path = storage.save_generated_content(
                prompt="Write about productivity",
                response="Productivity is key to success.",
                author_name="Test Author",
                model_id="ft:gpt-3.5-turbo:model:123",
                timestamp=timestamp,
            )

            # Check file was created
            assert content_path.exists()
            assert content_path.name == "test_author_20230115_143045_write_abou.md"

            # Check file content
            content = content_path.read_text(encoding="utf-8")
            assert "# Generated Content" in content
            assert "**Author:** Test Author" in content
            assert "**Model:** ft:gpt-3.5-turbo:model:123" in content
            assert "**Prompt:** Write about productivity" in content
            assert "Productivity is key to success." in content

    def test_save_generated_content_current_time(self, temp_data_dir, mock_settings):
        """Test saving generated content with current time."""
        with patch("core.storage.settings", mock_settings):
            storage = AuthorStorage("test_author")

            content_path = storage.save_generated_content(
                prompt="Test prompt",
                response="Test response",
                author_name="Test Author",
                model_id="test-model",
            )

            # Check file was created (filename will have current timestamp)
            assert content_path.exists()
            assert content_path.name.startswith("test_author_")
            assert content_path.name.endswith("_test_promp.md")

    def test_save_generated_content_error_handling(self, temp_data_dir, mock_settings):
        """Test that content saving errors are handled gracefully."""
        with patch("core.storage.settings", mock_settings):
            storage = AuthorStorage("test_author")

            # Mock the save_content_as_markdown to raise an exception
            with patch(
                "core.storage.save_content_as_markdown",
                side_effect=Exception("Test error"),
            ):
                with pytest.raises(Exception, match="Test error"):
                    storage.save_generated_content(
                        prompt="Test prompt",
                        response="Test response",
                        author_name="Test Author",
                        model_id="test-model",
                    )
