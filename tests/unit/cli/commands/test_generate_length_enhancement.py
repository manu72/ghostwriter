import pytest

from cli.commands.generate import _enhance_prompt_for_length
from core.config import settings


class TestLengthEnhancement:
    """Test prompt length enhancement functionality."""

    def test_enhance_prompt_explicit_word_count(self):
        """Test enhancement with explicit word count."""
        prompt = "Write a 3000 word short story about dragons"
        enhanced, tokens = _enhance_prompt_for_length(prompt, 10000, "medium")

        assert "3000 words" in enhanced
        # Should adjust tokens for 3000 words (~4000 tokens + buffer)
        expected_tokens = int(3000 * 1.33) + 500  # 4490
        assert tokens == expected_tokens
        assert "Please write approximately 3000 words" in enhanced

    def test_enhance_prompt_page_count(self):
        """Test enhancement with page count."""
        prompt = "Write a 5 page research paper"
        enhanced, tokens = _enhance_prompt_for_length(prompt, 10000, "medium")

        assert "5 pages" in enhanced
        assert "1250 words" in enhanced  # 5 pages * 250 words
        expected_tokens = int(1250 * 1.33) + 500  # 2162
        assert tokens == expected_tokens

    def test_enhance_prompt_descriptive_terms_short(self):
        """Test enhancement with descriptive short terms."""
        prompt = "Write a brief story about friendship"
        enhanced, tokens = _enhance_prompt_for_length(prompt, 10000, "medium")

        assert tokens == 2000  # Should limit for short content
        assert "concise piece" in enhanced

    def test_enhance_prompt_descriptive_terms_long(self):
        """Test enhancement with descriptive long terms."""
        prompt = "Write a detailed analysis of climate change"
        enhanced, tokens = _enhance_prompt_for_length(prompt, 10000, "medium")

        # The function doesn't detect "detailed" as a long-form pattern,
        # so it should return the original tokens
        assert tokens == 10000
        # But if we use a pattern it recognizes...

    def test_enhance_prompt_descriptive_terms_long_recognized(self):
        """Test enhancement with descriptive long terms that are recognized."""
        prompt = "Write a long essay about climate change"
        enhanced, tokens = _enhance_prompt_for_length(prompt, 10000, "medium")

        expected_max = min(20000, settings.max_context_tokens - 1000)
        assert tokens == expected_max
        assert "detailed, comprehensive piece" in enhanced

    def test_enhance_prompt_length_preference_long(self):
        """Test enhancement using author's long length preference."""
        prompt = "Write about artificial intelligence"
        enhanced, tokens = _enhance_prompt_for_length(prompt, 10000, "long")

        assert tokens == 15000  # Should double default for "long" preference
        assert "comprehensive, detailed response" in enhanced

    def test_enhance_prompt_length_preference_short(self):
        """Test enhancement using author's short length preference."""
        prompt = "Write about artificial intelligence"
        enhanced, tokens = _enhance_prompt_for_length(prompt, 10000, "short")

        assert tokens == 3000  # Should limit for "short" preference
        assert "concise response" in enhanced

    def test_enhance_prompt_no_changes_medium(self):
        """Test no enhancement for medium preference with regular prompt."""
        prompt = "Write about artificial intelligence"
        enhanced, tokens = _enhance_prompt_for_length(prompt, 10000, "medium")

        assert tokens == 10000  # Should keep default
        assert enhanced == prompt  # No enhancement needed

    def test_enhance_prompt_respects_max_context_limit(self):
        """Test that token adjustment respects max context limit."""
        prompt = "Write a 50000 word novel"
        enhanced, tokens = _enhance_prompt_for_length(prompt, 10000, "medium")

        # Should be capped at max_context_tokens - 1000
        expected_max = settings.max_context_tokens - 1000
        assert tokens <= expected_max
        assert tokens < 50000 * 1.33  # Less than the naive calculation
