"""
Historical figure research and analysis module.

This module provides AI-powered discovery and analysis of historical and public figures
for creating author profiles based on their writing styles.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.adapters.openai_adapter import OpenAIAdapter
from core.config import settings
from core.prompts.historical_templates import (
    FIGURE_ANALYSIS_TEMPLATE,
    FIGURE_DISCOVERY_TEMPLATE,
    FIGURE_NAME_SEARCH_TEMPLATE,
    FIGURE_SEARCH_REFINEMENT_TEMPLATE,
    FIGURE_VERIFICATION_TEMPLATE,
    estimate_cost,
)

console = Console()


@dataclass
class HistoricalFigure:
    """Represents a discovered historical figure with basic information."""

    name: str
    time_period: str
    writing_style: str
    notable_works: str
    match_criteria: str


@dataclass
class FigureAnalysis:
    """Detailed analysis of a historical figure's writing style."""

    figure_name: str
    tone_analysis: str
    voice_perspective: str
    formality_level: str
    length_structure: str
    unique_characteristics: str
    topics_themes: str
    historical_context: str


@dataclass
class FigureVerification:
    """Verification result for a historical figure."""

    figure_name: str
    status: str  # VERIFIED, UNVERIFIED, INAPPROPRIATE
    reason: str
    available_sources: str
    concerns: str
    time_period: Optional[str] = None
    primary_medium: Optional[str] = None
    writing_volume: Optional[str] = None


class HistoricalFigureResearcher:
    """AI-powered historical figure research and analysis."""

    def __init__(self):
        """Initialize the researcher with OpenAI adapter."""
        try:
            self.adapter = OpenAIAdapter()
            self.model = settings.get_default_model("openai")
        except ValueError as e:
            raise ValueError(f"Could not initialize OpenAI adapter: {e}")

    def discover_figures(self, criteria: str, count: int = 5) -> List[HistoricalFigure]:
        """Discover historical figures based on user criteria.

        Args:
            criteria: User's description of what kind of figure they want
            count: Number of figures to return (1-20, default 5)

        Returns:
            List of discovered historical figures
        """
        # Validate count parameter
        if count < 1 or count > 20:
            raise ValueError("Count must be between 1 and 20")

        if count != 5:
            console.print(f"[dim]Requesting {count} figures[/dim]")
        console.print(
            f"[blue]🔍 Searching for historical figures matching: '{criteria}'[/blue]"
        )

        # Estimate cost and inform user
        cost = estimate_cost("figure_discovery", count=count)
        console.print(f"[yellow]💰 Estimated cost: ${cost:.3f}[/yellow]")

        prompt = FIGURE_DISCOVERY_TEMPLATE.format(criteria=criteria, count=count)

        try:
            response = self.adapter.generate_text(
                model_id=self.model, prompt=prompt, max_completion_tokens=1200
            )

            return self._parse_figure_discovery(response)

        except Exception as e:
            console.print(f"[red]❌ Error discovering figures: {str(e)}[/red]")
            return []

    def search_by_name(self, name_query: str, count: int = 5) -> List[HistoricalFigure]:
        """Search for historical figures by name or name similarity.

        Args:
            name_query: Name or partial name of the figure to search for
            count: Number of figures to return (1-20, default 5)

        Returns:
            List of historical figures matching the name query
        """
        # Validate count parameter
        if count < 1 or count > 20:
            raise ValueError("Count must be between 1 and 20")

        if count != 5:
            console.print(f"[dim]Requesting {count} figures[/dim]")
        console.print(
            f"[blue]🔍 Searching for historical figures named: '{name_query}'[/blue]"
        )

        # Estimate cost and inform user
        cost = estimate_cost("figure_name_search", count=count)
        console.print(f"[yellow]💰 Estimated cost: ${cost:.3f}[/yellow]")

        prompt = FIGURE_NAME_SEARCH_TEMPLATE.format(name_query=name_query, count=count)

        try:
            response = self.adapter.generate_text(
                model_id=self.model, prompt=prompt, max_completion_tokens=1200
            )

            return self._parse_figure_name_search(response)

        except Exception as e:
            console.print(f"[red]❌ Error searching by name: {str(e)}[/red]")
            return []

    def analyze_figure(self, figure_name: str) -> Optional[FigureAnalysis]:
        """Analyze a historical figure's writing style in detail.

        Args:
            figure_name: Name of the figure to analyze

        Returns:
            Detailed analysis of their writing style, or None if failed
        """
        console.print(f"[blue]📚 Analyzing writing style of {figure_name}...[/blue]")

        # Estimate cost
        cost = estimate_cost("figure_analysis")
        console.print(f"[yellow]💰 Estimated cost: ${cost:.3f}[/yellow]")

        prompt = FIGURE_ANALYSIS_TEMPLATE.format(figure_name=figure_name)

        try:
            response = self.adapter.generate_text(
                model_id=self.model, prompt=prompt, max_completion_tokens=1500
            )

            return self._parse_figure_analysis(figure_name, response)

        except Exception as e:
            console.print(f"[red]❌ Error analyzing figure: {str(e)}[/red]")
            return None

    def verify_figure(self, figure_name: str) -> Optional[FigureVerification]:
        """Verify if a figure is appropriate and has sufficient written works.

        Args:
            figure_name: Name of the figure to verify

        Returns:
            Verification result, or None if failed
        """
        console.print(f"[blue]✅ Verifying figure: {figure_name}...[/blue]")

        # Estimate cost
        cost = estimate_cost("figure_verification")
        console.print(f"[yellow]💰 Estimated cost: ${cost:.3f}[/yellow]")

        prompt = FIGURE_VERIFICATION_TEMPLATE.format(figure_name=figure_name)

        try:
            response = self.adapter.generate_text(
                model_id=self.model, prompt=prompt, max_completion_tokens=600
            )

            return self._parse_figure_verification(figure_name, response)

        except Exception as e:
            console.print(f"[red]❌ Error verifying figure: {str(e)}[/red]")
            return None

    def refine_search(
        self, original_criteria: str, user_feedback: str
    ) -> List[HistoricalFigure]:
        """Refine figure search based on user feedback.

        Args:
            original_criteria: The original search criteria
            user_feedback: User's feedback on previous results

        Returns:
            List of refined figure suggestions
        """
        console.print("[blue]🔄 Refining search based on your feedback...[/blue]")

        # Estimate cost
        cost = estimate_cost("search_refinement")
        console.print(f"[yellow]💰 Estimated cost: ${cost:.3f}[/yellow]")

        prompt = FIGURE_SEARCH_REFINEMENT_TEMPLATE.format(
            original_criteria=original_criteria, user_feedback=user_feedback
        )

        try:
            response = self.adapter.generate_text(
                model_id=self.model, prompt=prompt, max_completion_tokens=1000
            )

            return self._parse_figure_refinement(response)

        except Exception as e:
            console.print(f"[red]❌ Error refining search: {str(e)}[/red]")
            return []

    def _parse_figure_discovery(self, response: str) -> List[HistoricalFigure]:
        """Parse the AI response for discovered figures."""
        figures = []

        # Split response into figure sections
        # Look for pattern: **Figure N: [Name] ([Time Period])**
        figure_pattern = r"\*\*Figure \d+: (.+?)\s*\(([^)]+)\)\*\*"
        figure_matches = re.findall(figure_pattern, response)

        # Split the response by figure headers to get content for each
        figure_sections = re.split(r"\*\*Figure \d+:[^*]+\*\*", response)[
            1:
        ]  # Skip first empty section

        for i, (name_match, period_match) in enumerate(figure_matches):
            if i < len(figure_sections):
                section = figure_sections[i]

                # Extract the components using simple text processing
                writing_style = self._extract_field(
                    section, ["Writing Style:", "- Writing Style:"]
                )
                notable_works = self._extract_field(
                    section, ["Notable Works:", "- Notable Works:"]
                )
                match_criteria = self._extract_field(
                    section, ["Match Criteria:", "- Match Criteria:"]
                )

                figure = HistoricalFigure(
                    name=name_match.strip(),
                    time_period=period_match.strip(),
                    writing_style=writing_style or "Not specified",
                    notable_works=notable_works or "Not specified",
                    match_criteria=match_criteria or "Not specified",
                )
                figures.append(figure)

        return figures

    def _parse_figure_name_search(self, response: str) -> List[HistoricalFigure]:
        """Parse the AI response for name-based figure search."""
        figures = []

        # Split response into figure sections
        # Look for pattern: **Figure N: [Name] ([Time Period])**
        figure_pattern = r"\*\*Figure \d+: (.+?)\s*\(([^)]+)\)\*\*"
        figure_matches = re.findall(figure_pattern, response)

        # Split the response by figure headers to get content for each
        figure_sections = re.split(r"\*\*Figure \d+:[^*]+\*\*", response)[
            1:
        ]  # Skip first empty section

        for i, (name_match, period_match) in enumerate(figure_matches):
            if i < len(figure_sections):
                section = figure_sections[i]

                # Extract the components using simple text processing
                writing_style = self._extract_field(
                    section, ["Writing Style:", "- Writing Style:"]
                )
                notable_works = self._extract_field(
                    section, ["Notable Works:", "- Notable Works:"]
                )
                match_type = self._extract_field(
                    section, ["Match Type:", "- Match Type:"]
                )
                also_known_as = self._extract_field(
                    section, ["Also Known As:", "- Also Known As:"]
                )

                # Combine match type and aliases for match criteria
                match_criteria = match_type or "Name match"
                if also_known_as and also_known_as != "None":
                    match_criteria += f" (Also: {also_known_as})"

                figure = HistoricalFigure(
                    name=name_match.strip(),
                    time_period=period_match.strip(),
                    writing_style=writing_style or "Not specified",
                    notable_works=notable_works or "Not specified",
                    match_criteria=match_criteria,
                )
                figures.append(figure)

        return figures

    def _parse_figure_analysis(self, figure_name: str, response: str) -> FigureAnalysis:
        """Parse the AI response for figure analysis."""
        return FigureAnalysis(
            figure_name=figure_name,
            tone_analysis=self._extract_section(
                response, ["**TONE ANALYSIS:**", "TONE ANALYSIS:"]
            ),
            voice_perspective=self._extract_section(
                response, ["**VOICE AND PERSPECTIVE:**", "VOICE AND PERSPECTIVE:"]
            ),
            formality_level=self._extract_section(
                response, ["**FORMALITY LEVEL:**", "FORMALITY LEVEL:"]
            ),
            length_structure=self._extract_section(
                response, ["**LENGTH AND STRUCTURE:**", "LENGTH AND STRUCTURE:"]
            ),
            unique_characteristics=self._extract_section(
                response, ["**UNIQUE CHARACTERISTICS:**", "UNIQUE CHARACTERISTICS:"]
            ),
            topics_themes=self._extract_section(
                response, ["**TOPICS AND THEMES:**", "TOPICS AND THEMES:"]
            ),
            historical_context=self._extract_section(
                response, ["**HISTORICAL CONTEXT:**", "HISTORICAL CONTEXT:"]
            ),
        )

    def _parse_figure_verification(
        self, figure_name: str, response: str
    ) -> FigureVerification:
        """Parse the AI response for figure verification."""
        # Extract key fields
        status = (
            self._extract_field(response, ["**Status:**", "Status:"]) or "UNVERIFIED"
        )
        reason = (
            self._extract_field(response, ["**Reason:**", "Reason:"]) or "Not specified"
        )
        available_sources = (
            self._extract_field(
                response, ["**Available Sources:**", "Available Sources:"]
            )
            or "Unknown"
        )
        concerns = (
            self._extract_field(response, ["**Concerns:**", "Concerns:"])
            or "None specified"
        )

        # Optional fields (only present if VERIFIED)
        time_period = self._extract_field(
            response, ["**Time Period:**", "Time Period:"]
        )
        primary_medium = self._extract_field(
            response, ["**Primary Medium:**", "Primary Medium:"]
        )
        writing_volume = self._extract_field(
            response, ["**Writing Volume:**", "Writing Volume:"]
        )

        return FigureVerification(
            figure_name=figure_name,
            status=status.strip().upper(),
            reason=reason,
            available_sources=available_sources,
            concerns=concerns,
            time_period=time_period,
            primary_medium=primary_medium,
            writing_volume=writing_volume,
        )

    def _parse_figure_refinement(self, response: str) -> List[HistoricalFigure]:
        """Parse the AI response for refined figure suggestions."""
        figures = []

        # Look for pattern: **Figure N: [Name] ([Period])**
        figure_pattern = r"\*\*Figure \d+: (.+?)\s*\(([^)]+)\)\*\*"
        figure_matches = re.findall(figure_pattern, response)

        # Split the response by figure headers
        figure_sections = re.split(r"\*\*Figure \d+:[^*]+\*\*", response)[1:]

        for i, (name_match, period_match) in enumerate(figure_matches):
            if i < len(figure_sections):
                section = figure_sections[i]

                better_match = self._extract_field(
                    section, ["- Better Match Because:", "Better Match Because:"]
                )
                style_preview = self._extract_field(
                    section, ["- Style Preview:", "Style Preview:"]
                )
                available_content = self._extract_field(
                    section, ["- Available Content:", "Available Content:"]
                )

                # Combine the refinement-specific info
                writing_style = style_preview or "Style not specified"
                match_criteria = better_match or "Refinement reason not specified"
                notable_works = available_content or "Content not specified"

                figure = HistoricalFigure(
                    name=name_match.strip(),
                    time_period=period_match.strip(),
                    writing_style=writing_style,
                    notable_works=notable_works,
                    match_criteria=match_criteria,
                )
                figures.append(figure)

        return figures

    def _extract_field(self, text: str, field_markers: List[str]) -> Optional[str]:
        """Extract a single field value from text using multiple possible markers."""
        for marker in field_markers:
            # Look for the marker, then capture until next field (bold or dash prefix) or end
            pattern = rf"{re.escape(marker)}\s*(.+?)(?=\n\s*[\*\-]|\Z)"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                # Get the captured text and clean it up
                value = match.group(1).strip()
                # Remove any trailing content that looks like another field
                value = re.sub(r"\n\s*[\*\-].*", "", value)
                return value.strip()
        return None

    def _extract_section(self, text: str, section_markers: List[str]) -> str:
        """Extract a full section from text using multiple possible markers."""
        for marker in section_markers:
            # Look for the marker followed by content until next section or end
            pattern = rf"{re.escape(marker)}\s*(.+?)(?=\n\*\*[A-Z][A-Z ]*:\*\*|\Z)"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Section not found"


def display_figures(
    figures: List[HistoricalFigure], title: str = "Discovered Historical Figures"
) -> None:
    """Display a table of historical figures."""
    if not figures:
        console.print("[yellow]No figures found.[/yellow]")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("#", width=3, style="cyan")
    table.add_column("Name", style="bold white")
    table.add_column("Period", style="dim")
    table.add_column("Writing Style", max_width=30)
    table.add_column("Notable Works", max_width=30)
    table.add_column("Match Reason", max_width=35)

    for i, figure in enumerate(figures, 1):
        table.add_row(
            str(i),
            figure.name,
            figure.time_period,
            (
                figure.writing_style[:27] + "..."
                if len(figure.writing_style) > 30
                else figure.writing_style
            ),
            (
                figure.notable_works[:27] + "..."
                if len(figure.notable_works) > 30
                else figure.notable_works
            ),
            (
                figure.match_criteria[:32] + "..."
                if len(figure.match_criteria) > 35
                else figure.match_criteria
            ),
        )

    console.print(table)


def display_analysis(analysis: FigureAnalysis) -> None:
    """Display a detailed analysis of a historical figure."""
    console.print(f"\n[bold blue]📚 Analysis of {analysis.figure_name}[/bold blue]")

    sections = [
        ("🎭 Tone Analysis", analysis.tone_analysis),
        ("🗣️  Voice & Perspective", analysis.voice_perspective),
        ("📜 Formality Level", analysis.formality_level),
        ("📏 Length & Structure", analysis.length_structure),
        ("✨ Unique Characteristics", analysis.unique_characteristics),
        ("📖 Topics & Themes", analysis.topics_themes),
        ("🏛️  Historical Context", analysis.historical_context),
    ]

    for title, content in sections:
        if content and content != "Section not found":
            console.print(Panel(content, title=title, border_style="blue"))


def display_verification(verification: FigureVerification) -> None:
    """Display verification results for a historical figure."""
    # Determine color based on status
    status_colors = {"VERIFIED": "green", "UNVERIFIED": "red", "INAPPROPRIATE": "red"}
    status_color = status_colors.get(verification.status, "yellow")
    status_icon = "✅" if verification.status == "VERIFIED" else "❌"

    console.print(
        f"\n[bold {status_color}]{status_icon} Verification: {verification.status}[/bold {status_color}]"
    )

    # Basic info
    info_text = f"[bold]Reason:[/bold] {verification.reason}\n"
    info_text += f"[bold]Available Sources:[/bold] {verification.available_sources}\n"
    if verification.concerns:
        info_text += f"[bold]Concerns:[/bold] {verification.concerns}\n"

    # Additional info if verified
    if verification.status == "VERIFIED":
        if verification.time_period:
            info_text += f"[bold]Time Period:[/bold] {verification.time_period}\n"
        if verification.primary_medium:
            info_text += f"[bold]Primary Medium:[/bold] {verification.primary_medium}\n"
        if verification.writing_volume:
            info_text += f"[bold]Writing Volume:[/bold] {verification.writing_volume}\n"

    console.print(
        Panel(
            info_text.strip(),
            title=f"Verification: {verification.figure_name}",
            border_style=status_color,
        )
    )
