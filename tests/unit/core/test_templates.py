"""Tests for prompt templates."""

import pytest

from core.models import AuthorProfile, StyleGuide
from core.prompts.templates import build_chat_system_prompt, build_system_prompt


class TestPromptTemplates:
    """Test prompt template functions."""

    @pytest.fixture
    def sample_author_profile(self):
        """Create a sample author profile for testing."""
        style_guide = StyleGuide(
            tone="friendly",
            voice="first_person",
            formality="casual",
            length_preference="medium",
            topics=["technology", "productivity"],
            avoid_topics=["politics"],
            writing_style_notes="Uses humor and personal anecdotes",
        )

        return AuthorProfile(
            author_id="test_author",
            name="Test Author",
            description="A test author",
            style_guide=style_guide,
        )

    def test_build_system_prompt(self, sample_author_profile):
        """Test building standard system prompt."""
        prompt = build_system_prompt(sample_author_profile)

        assert "Test Author" in prompt
        assert "friendly" in prompt  # tone
        assert "first_person" in prompt  # voice
        assert "casual" in prompt  # formality
        assert "medium" in prompt  # length_preference
        assert "Uses humor and personal anecdotes" in prompt  # style notes
        assert "technology, productivity" in prompt  # topics
        assert "politics" in prompt  # avoid_topics
        assert (
            "Please write in a way that reflects these characteristics consistently"
            in prompt
        )

    def test_build_chat_system_prompt(self, sample_author_profile):
        """Test building chat-optimized system prompt."""
        prompt = build_chat_system_prompt(sample_author_profile)

        assert "Test Author" in prompt
        assert "friendly" in prompt  # tone
        assert "first_person" in prompt  # voice
        assert "casual" in prompt  # formality
        assert "medium" in prompt  # length_preference
        assert "Uses humor and personal anecdotes" in prompt  # style notes
        assert "technology, productivity" in prompt  # topics
        assert "politics" in prompt  # avoid_topics

        # Chat-specific content
        assert "having a conversation" in prompt
        assert "conversational and engaging" in prompt
        assert "friendly chat" in prompt

    def test_build_system_prompt_empty_topics(self):
        """Test system prompt with no topics specified."""
        style_guide = StyleGuide(
            tone="professional",
            voice="third_person",
            formality="formal",
            length_preference="long",
            topics=[],
            avoid_topics=[],
            writing_style_notes="",
        )

        profile = AuthorProfile(
            author_id="minimal_author",
            name="Minimal Author",
            style_guide=style_guide,
        )

        prompt = build_system_prompt(profile)

        assert "Minimal Author" in prompt
        assert "professional" in prompt
        assert "No additional notes" in prompt  # default when empty

    def test_build_chat_system_prompt_empty_topics(self):
        """Test chat system prompt with no topics specified."""
        style_guide = StyleGuide(
            tone="professional",
            voice="third_person",
            formality="formal",
            length_preference="long",
            topics=[],
            avoid_topics=[],
            writing_style_notes="",
        )

        profile = AuthorProfile(
            author_id="minimal_author",
            name="Minimal Author",
            style_guide=style_guide,
        )

        prompt = build_chat_system_prompt(profile)

        assert "Minimal Author" in prompt
        assert "professional" in prompt
        assert "No additional notes" in prompt  # default when empty
        assert "having a conversation" in prompt  # chat-specific

    def test_prompt_templates_are_different(self, sample_author_profile):
        """Test that chat and standard prompts are different."""
        standard_prompt = build_system_prompt(sample_author_profile)
        chat_prompt = build_chat_system_prompt(sample_author_profile)

        assert standard_prompt != chat_prompt
        assert "having a conversation" in chat_prompt
        assert "having a conversation" not in standard_prompt
        assert "friendly chat" in chat_prompt
        assert "friendly chat" not in standard_prompt
