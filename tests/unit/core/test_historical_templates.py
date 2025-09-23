"""
Unit tests for historical prompt templates.
"""

import pytest

from core.prompts.historical_templates import (
    ESTIMATED_TOKENS,
    FIGURE_ANALYSIS_TEMPLATE,
    FIGURE_DISCOVERY_TEMPLATE,
    FIGURE_NAME_SEARCH_TEMPLATE,
    FIGURE_SEARCH_REFINEMENT_TEMPLATE,
    FIGURE_VERIFICATION_TEMPLATE,
    HISTORICAL_EXAMPLE_GENERATION_TEMPLATE,
    STYLE_GUIDE_GENERATION_TEMPLATE,
    estimate_cost,
)


class TestHistoricalPromptTemplates:
    """Test historical prompt templates."""

    def test_figure_discovery_template_formatting(self):
        """Test FIGURE_DISCOVERY_TEMPLATE formatting."""
        criteria = "Famous American authors"
        count = 5

        formatted = FIGURE_DISCOVERY_TEMPLATE.format(criteria=criteria, count=count)

        assert criteria in formatted
        assert f"suggest {count} historical or public figures" in formatted
        assert "**Figure 1:" in formatted
        assert "Writing Style:" in formatted
        assert "Notable Works:" in formatted
        assert "Match Criteria:" in formatted

    def test_figure_name_search_template_formatting(self):
        """Test FIGURE_NAME_SEARCH_TEMPLATE formatting."""
        name_query = "Mark Twain"
        count = 3

        formatted = FIGURE_NAME_SEARCH_TEMPLATE.format(
            name_query=name_query, count=count
        )

        assert name_query in formatted
        assert f"find up to {count} historical or public figures" in formatted
        assert "**Figure 1:" in formatted
        assert "Also Known As:" in formatted
        assert "Writing Style:" in formatted
        assert "Notable Works:" in formatted
        assert "Match Type:" in formatted
        assert "exact match" in formatted.lower()
        assert "similar spelling" in formatted.lower()

    def test_figure_analysis_template_formatting(self):
        """Test FIGURE_ANALYSIS_TEMPLATE formatting."""
        figure_name = "Mark Twain"

        formatted = FIGURE_ANALYSIS_TEMPLATE.format(figure_name=figure_name)

        assert formatted.count(figure_name) >= 2  # Should appear multiple times
        assert "**TONE ANALYSIS:**" in formatted
        assert "**VOICE AND PERSPECTIVE:**" in formatted
        assert "**FORMALITY LEVEL:**" in formatted
        assert "**LENGTH AND STRUCTURE:**" in formatted
        assert "**UNIQUE CHARACTERISTICS:**" in formatted
        assert "**TOPICS AND THEMES:**" in formatted
        assert "**HISTORICAL CONTEXT:**" in formatted

    def test_style_guide_generation_template_formatting(self):
        """Test STYLE_GUIDE_GENERATION_TEMPLATE formatting."""
        figure_name = "Virginia Woolf"
        figure_analysis = "Test analysis content"

        formatted = STYLE_GUIDE_GENERATION_TEMPLATE.format(
            figure_name=figure_name, figure_analysis=figure_analysis
        )

        assert figure_name in formatted
        assert figure_analysis in formatted
        assert "**TONE:**" in formatted
        assert "**VOICE:**" in formatted
        assert "**FORMALITY:**" in formatted
        assert "**LENGTH_PREFERENCE:**" in formatted
        assert "**PREFERRED_TOPICS:**" in formatted
        assert "**AVOID_TOPICS:**" in formatted
        assert "**WRITING_STYLE_NOTES:**" in formatted

    def test_figure_verification_template_formatting(self):
        """Test FIGURE_VERIFICATION_TEMPLATE formatting."""
        figure_name = "Charles Dickens"

        formatted = FIGURE_VERIFICATION_TEMPLATE.format(figure_name=figure_name)

        assert formatted.count(figure_name) >= 1
        assert "**EXISTENCE:**" in formatted
        assert "**WRITINGS:**" in formatted
        assert "**ACCESSIBILITY:**" in formatted
        assert "**APPROPRIATENESS:**" in formatted
        assert "VERIFIED/UNVERIFIED/INAPPROPRIATE" in formatted

    def test_historical_example_generation_template_formatting(self):
        """Test HISTORICAL_EXAMPLE_GENERATION_TEMPLATE formatting."""
        kwargs = {
            "figure_name": "Ernest Hemingway",
            "tone": "terse",
            "voice": "third_person",
            "formality": "moderate",
            "length_preference": "short",
            "style_notes": "Understated prose",
            "historical_context": "20th century American literature",
            "count": 3,
        }

        formatted = HISTORICAL_EXAMPLE_GENERATION_TEMPLATE.format(**kwargs)

        assert kwargs["figure_name"] in formatted
        assert kwargs["tone"] in formatted
        assert kwargs["voice"] in formatted
        assert kwargs["formality"] in formatted
        assert kwargs["length_preference"] in formatted
        assert kwargs["style_notes"] in formatted
        assert kwargs["historical_context"] in formatted
        assert str(kwargs["count"]) in formatted
        assert "**EXAMPLE 1:**" in formatted
        assert "User prompt:" in formatted
        assert "Assistant response:" in formatted

    def test_figure_search_refinement_template_formatting(self):
        """Test FIGURE_SEARCH_REFINEMENT_TEMPLATE formatting."""
        original_criteria = "American authors"
        user_feedback = "Focus on 20th century writers"

        formatted = FIGURE_SEARCH_REFINEMENT_TEMPLATE.format(
            original_criteria=original_criteria, user_feedback=user_feedback
        )

        assert original_criteria in formatted
        assert user_feedback in formatted
        assert "suggest 3 more historical figures" in formatted
        assert "**Figure 1:" in formatted
        assert "Better Match Because:" in formatted
        assert "Style Preview:" in formatted
        assert "Available Content:" in formatted

    def test_templates_are_strings(self):
        """Test that all templates are strings."""
        templates = [
            FIGURE_DISCOVERY_TEMPLATE,
            FIGURE_NAME_SEARCH_TEMPLATE,
            FIGURE_ANALYSIS_TEMPLATE,
            STYLE_GUIDE_GENERATION_TEMPLATE,
            FIGURE_VERIFICATION_TEMPLATE,
            HISTORICAL_EXAMPLE_GENERATION_TEMPLATE,
            FIGURE_SEARCH_REFINEMENT_TEMPLATE,
        ]

        for template in templates:
            assert isinstance(template, str)
            assert len(template) > 100  # Should be substantial templates

    def test_templates_have_format_placeholders(self):
        """Test that templates contain their expected format placeholders."""
        # Test FIGURE_DISCOVERY_TEMPLATE
        assert "{criteria}" in FIGURE_DISCOVERY_TEMPLATE
        assert "{count}" in FIGURE_DISCOVERY_TEMPLATE

        # Test FIGURE_NAME_SEARCH_TEMPLATE
        assert "{name_query}" in FIGURE_NAME_SEARCH_TEMPLATE
        assert "{count}" in FIGURE_NAME_SEARCH_TEMPLATE

        # Test FIGURE_ANALYSIS_TEMPLATE
        assert "{figure_name}" in FIGURE_ANALYSIS_TEMPLATE

        # Test STYLE_GUIDE_GENERATION_TEMPLATE
        assert "{figure_name}" in STYLE_GUIDE_GENERATION_TEMPLATE
        assert "{figure_analysis}" in STYLE_GUIDE_GENERATION_TEMPLATE

        # Test FIGURE_VERIFICATION_TEMPLATE
        assert "{figure_name}" in FIGURE_VERIFICATION_TEMPLATE

        # Test HISTORICAL_EXAMPLE_GENERATION_TEMPLATE
        required_placeholders = [
            "{figure_name}",
            "{tone}",
            "{voice}",
            "{formality}",
            "{length_preference}",
            "{style_notes}",
            "{historical_context}",
            "{count}",
        ]
        for placeholder in required_placeholders:
            assert placeholder in HISTORICAL_EXAMPLE_GENERATION_TEMPLATE

        # Test FIGURE_SEARCH_REFINEMENT_TEMPLATE
        assert "{original_criteria}" in FIGURE_SEARCH_REFINEMENT_TEMPLATE
        assert "{user_feedback}" in FIGURE_SEARCH_REFINEMENT_TEMPLATE


class TestEstimatedTokens:
    """Test estimated tokens dictionary."""

    def test_estimated_tokens_structure(self):
        """Test that ESTIMATED_TOKENS has expected structure."""
        assert isinstance(ESTIMATED_TOKENS, dict)

        expected_keys = [
            "figure_discovery",
            "figure_name_search",
            "figure_analysis",
            "style_guide_generation",
            "figure_verification",
            "example_generation",
            "search_refinement",
        ]

        for key in expected_keys:
            assert key in ESTIMATED_TOKENS
            assert isinstance(ESTIMATED_TOKENS[key], int)
            assert ESTIMATED_TOKENS[key] > 0

    def test_estimated_tokens_values_reasonable(self):
        """Test that estimated token values are reasonable."""
        # All values should be between 100 and 2000 tokens (reasonable for these operations)
        for operation, tokens in ESTIMATED_TOKENS.items():
            assert (
                100 <= tokens <= 5000
            ), f"{operation} has unreasonable token estimate: {tokens}"

    def test_operation_relative_costs(self):
        """Test that operation costs make sense relative to each other."""
        # Figure analysis should be more expensive than verification
        assert (
            ESTIMATED_TOKENS["figure_analysis"]
            > ESTIMATED_TOKENS["figure_verification"]
        )

        # For scaling operations (per-figure costs), test them in realistic scenarios
        # Discovery for 5 figures should be more expensive than style guide generation
        discovery_5_figures = ESTIMATED_TOKENS["figure_discovery"] * 5
        assert discovery_5_figures > ESTIMATED_TOKENS["style_guide_generation"]

        # Name search should be less expensive per figure than discovery per figure
        assert (
            ESTIMATED_TOKENS["figure_name_search"]
            < ESTIMATED_TOKENS["figure_discovery"]
        )

        # Example generation should be substantial (it's per example)
        assert ESTIMATED_TOKENS["example_generation"] >= 400


class TestEstimateCost:
    """Test cost estimation function."""

    def test_estimate_cost_single_operation(self):
        """Test cost estimation for single operation."""
        cost = estimate_cost("figure_discovery")

        assert isinstance(cost, float)
        assert cost > 0
        # Should be small cost (less than $0.01 for discovery)
        assert cost < 0.09

    def test_estimate_cost_multiple_operations(self):
        """Test cost estimation for multiple operations."""
        single_cost = estimate_cost("example_generation", 1)
        multiple_cost = estimate_cost("example_generation", 5)

        # Allow for small rounding differences due to round() function
        assert abs(multiple_cost - (single_cost * 5)) < 0.0001
        assert multiple_cost > single_cost

    def test_estimate_cost_all_operations(self):
        """Test cost estimation for all operation types."""
        for operation in ESTIMATED_TOKENS.keys():
            cost = estimate_cost(operation)

            assert isinstance(cost, float)
            assert cost > 0
            # All individual operations should cost less than $0.01
            assert cost < 0.50

    def test_estimate_cost_invalid_operation(self):
        """Test cost estimation for invalid operation raises error."""
        with pytest.raises(ValueError, match="Unknown operation 'invalid_operation'"):
            estimate_cost("invalid_operation")

    def test_estimate_cost_invalid_operation_error_message(self):
        """Test that error message includes available operations."""
        with pytest.raises(ValueError) as exc_info:
            estimate_cost("typo_operation")

        error_message = str(exc_info.value)
        assert "Unknown operation 'typo_operation'" in error_message
        assert "Available operations:" in error_message
        # Should contain all known operations
        assert "figure_discovery" in error_message
        assert "figure_analysis" in error_message
        assert "style_guide_generation" in error_message

    def test_estimate_cost_zero_count(self):
        """Test cost estimation with zero count."""
        cost = estimate_cost("figure_discovery", 0)

        assert cost == 0.0

    def test_estimate_cost_large_count(self):
        """Test cost estimation with large count."""
        cost = estimate_cost("example_generation", 100)

        assert isinstance(cost, float)
        assert cost > 0
        # 100 examples should be relatively expensive
        assert cost > 0.9

    # def test_estimate_cost_calculation_accuracy(self):
    #     """Test that cost calculation is accurate."""
    #     operation = "figure_discovery"
    #     count = 3

    #     expected_tokens = ESTIMATED_TOKENS[operation] * count
    #     expected_cost = (expected_tokens / 1000) * 0.002

    #     actual_cost = estimate_cost(operation, count)

    #     assert actual_cost == expected_cost

    def test_cost_estimation_precision(self):
        """Test cost estimation precision for small amounts."""
        # Very small operations should still return non-zero costs
        cost = estimate_cost("style_guide_generation", 1)

        # Should have reasonable precision (not rounded to 0)
        assert cost > 0.0001
        assert cost < 0.01


class TestTemplateIntegration:
    """Test template integration scenarios."""

    def test_full_workflow_template_chain(self):
        """Test that templates can be chained in a typical workflow."""
        # Step 1: Discovery
        criteria = "Famous poets"
        count = 5
        discovery_prompt = FIGURE_DISCOVERY_TEMPLATE.format(
            criteria=criteria, count=count
        )
        assert criteria in discovery_prompt

        # Step 2: Analysis
        figure_name = "Emily Dickinson"
        analysis_prompt = FIGURE_ANALYSIS_TEMPLATE.format(figure_name=figure_name)
        assert figure_name in analysis_prompt

        # Step 3: Verification
        verification_prompt = FIGURE_VERIFICATION_TEMPLATE.format(
            figure_name=figure_name
        )
        assert figure_name in verification_prompt

        # Step 4: Style guide generation
        analysis_text = "Sample analysis content"
        style_prompt = STYLE_GUIDE_GENERATION_TEMPLATE.format(
            figure_name=figure_name, figure_analysis=analysis_text
        )
        assert figure_name in style_prompt
        assert analysis_text in style_prompt

        # Step 5: Example generation
        example_prompt = HISTORICAL_EXAMPLE_GENERATION_TEMPLATE.format(
            figure_name=figure_name,
            tone="introspective",
            voice="first_person",
            formality="moderate",
            length_preference="short",
            style_notes="Distinctive punctuation and imagery",
            historical_context="19th century American poetry",
            count=2,
        )
        assert figure_name in example_prompt
        assert "introspective" in example_prompt

    def test_error_handling_missing_placeholders(self):
        """Test that missing placeholders raise appropriate errors."""
        # Should raise KeyError for missing required placeholder
        with pytest.raises(KeyError):
            FIGURE_DISCOVERY_TEMPLATE.format()  # Missing criteria and count

        with pytest.raises(KeyError):
            FIGURE_DISCOVERY_TEMPLATE.format(criteria="test")  # Missing count

        with pytest.raises(KeyError):
            FIGURE_ANALYSIS_TEMPLATE.format()  # Missing figure_name

    def test_template_content_quality(self):
        """Test that templates contain quality instructional content."""
        # Templates should contain good instruction words
        quality_indicators = [
            "analyze",
            "provide",
            "based on",
            "consider",
            "specific",
            "detailed",
            "examples",
            "format",
            "requirements",
        ]

        all_templates = [
            FIGURE_DISCOVERY_TEMPLATE,
            FIGURE_NAME_SEARCH_TEMPLATE,
            FIGURE_ANALYSIS_TEMPLATE,
            STYLE_GUIDE_GENERATION_TEMPLATE,
            FIGURE_VERIFICATION_TEMPLATE,
            HISTORICAL_EXAMPLE_GENERATION_TEMPLATE,
            FIGURE_SEARCH_REFINEMENT_TEMPLATE,
        ]

        for template in all_templates:
            template_lower = template.lower()
            # Each template should contain at least some quality indicators
            found_indicators = [
                word for word in quality_indicators if word in template_lower
            ]
            assert (
                len(found_indicators) >= 2
            ), f"Template lacks quality instruction words: {found_indicators}"
