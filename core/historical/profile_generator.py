"""
Historical figure profile generation module.

This module converts historical figure analysis into AuthorProfile and StyleGuide
objects that can be used in the Ghostwriter training workflow.
"""

import re
from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from core.adapters.openai_adapter import OpenAIAdapter
from core.config import settings
from core.historical.figure_research import FigureAnalysis
from core.models import AuthorProfile, AuthorSource, StyleGuide
from core.prompts.historical_templates import (
    STYLE_GUIDE_GENERATION_TEMPLATE,
    estimate_cost,
)

console = Console()


class HistoricalProfileGenerator:
    """Generate AuthorProfile objects from historical figure analysis."""
    
    def __init__(self):
        """Initialize the generator with OpenAI adapter."""
        try:
            self.adapter = OpenAIAdapter()
            self.model = settings.get_default_model("openai")
        except ValueError as e:
            raise ValueError(f"Could not initialize OpenAI adapter: {e}")
    
    def generate_profile(
        self, 
        figure_analysis: FigureAnalysis,
        author_id: str,
        custom_description: Optional[str] = None
    ) -> Optional[AuthorProfile]:
        """Generate an AuthorProfile from figure analysis.
        
        Args:
            figure_analysis: Detailed analysis of the historical figure
            author_id: Unique ID for this author profile
            custom_description: Optional custom description, otherwise generates one
            
        Returns:
            AuthorProfile object ready for use in Ghostwriter workflow
        """
        console.print(f"[blue]🎭 Generating author profile for {figure_analysis.figure_name}...[/blue]")
        
        # Generate StyleGuide from analysis
        style_guide = self.generate_style_guide(figure_analysis)
        if not style_guide:
            console.print("[red]❌ Failed to generate style guide[/red]")
            return None
        
        # Create description
        description = custom_description or self._generate_description(figure_analysis)
        
        # Create the profile
        profile = AuthorProfile(
            author_id=author_id,
            name=figure_analysis.figure_name,
            description=description,
            source_type=AuthorSource.HISTORICAL,
            style_guide=style_guide,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        console.print(f"[green]✅ Generated profile for {figure_analysis.figure_name}[/green]")
        return profile
    
    def generate_style_guide(self, figure_analysis: FigureAnalysis) -> Optional[StyleGuide]:
        """Generate a StyleGuide from figure analysis using AI.
        
        Args:
            figure_analysis: Detailed analysis of the figure's writing style
            
        Returns:
            StyleGuide object, or None if generation failed
        """
        # Combine all analysis sections
        full_analysis = self._format_analysis_for_prompt(figure_analysis)
        
        # Estimate cost
        cost = estimate_cost("style_guide_generation")
        console.print(f"[yellow]💰 Estimated cost: ${cost:.3f}[/yellow]")
        
        prompt = STYLE_GUIDE_GENERATION_TEMPLATE.format(
            figure_name=figure_analysis.figure_name,
            figure_analysis=full_analysis
        )
        
        try:
            response = self.adapter.generate_text(
                model_id=self.model,
                prompt=prompt,
                max_completion_tokens=800
            )
            
            return self._parse_style_guide(response, figure_analysis.figure_name)
            
        except Exception as e:
            console.print(f"[red]❌ Error generating style guide: {str(e)}[/red]")
            return None
    
    def _format_analysis_for_prompt(self, analysis: FigureAnalysis) -> str:
        """Format the analysis for inclusion in the style guide generation prompt."""
        return f"""
TONE ANALYSIS:
{analysis.tone_analysis}

VOICE AND PERSPECTIVE: 
{analysis.voice_perspective}

FORMALITY LEVEL:
{analysis.formality_level}

LENGTH AND STRUCTURE:
{analysis.length_structure}

UNIQUE CHARACTERISTICS:
{analysis.unique_characteristics}

TOPICS AND THEMES:
{analysis.topics_themes}

HISTORICAL CONTEXT:
{analysis.historical_context}
        """.strip()
    
    def _generate_description(self, analysis: FigureAnalysis) -> str:
        """Generate a description for the author profile based on analysis."""
        return (f"AI author based on {analysis.figure_name}'s writing style and voice. "
                f"This profile captures their distinctive communication patterns, "
                f"tone, and stylistic characteristics as documented in their historical writings.")
    
    def _parse_style_guide(self, response: str, figure_name: str) -> Optional[StyleGuide]:
        """Parse the AI response into a StyleGuide object."""
        try:
            # Extract each field from the response
            tone = self._extract_style_field(response, "TONE") or "professional"
            voice = self._extract_style_field(response, "VOICE") or "first_person"  
            formality = self._extract_style_field(response, "FORMALITY") or "moderate"
            length_preference = self._extract_style_field(response, "LENGTH_PREFERENCE") or "medium"
            
            # Extract topics (list)
            topics_text = self._extract_style_field(response, "PREFERRED_TOPICS") or ""
            topics = self._parse_topic_list(topics_text)
            
            avoid_topics_text = self._extract_style_field(response, "AVOID_TOPICS") or ""
            avoid_topics = self._parse_topic_list(avoid_topics_text)
            
            # Extract style notes
            style_notes = self._extract_style_field(response, "WRITING_STYLE_NOTES") or ""
            
            # Validate the extracted values
            tone = self._validate_choice(tone, ["casual", "professional", "friendly", "authoritative", "witty", "formal"], "professional")
            voice = self._validate_choice(voice, ["first_person", "second_person", "third_person"], "first_person")
            formality = self._validate_choice(formality, ["very_casual", "casual", "moderate", "formal", "academic"], "moderate")
            length_preference = self._validate_choice(length_preference, ["short", "medium", "long", "variable"], "medium")
            
            style_guide = StyleGuide(
                tone=tone,
                voice=voice,
                formality=formality,
                length_preference=length_preference,
                topics=topics,
                avoid_topics=avoid_topics,
                writing_style_notes=style_notes
            )
            
            console.print(f"[green]✅ Style guide parsed successfully for {figure_name}[/green]")
            return style_guide
            
        except Exception as e:
            console.print(f"[red]❌ Error parsing style guide: {str(e)}[/red]")
            return None
    
    def _extract_style_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a field value from the structured response."""
        # Look for **FIELD:** [value]
        patterns = [
            rf"\*\*{field_name}:\*\*\s*\[(.+?)\]",
            rf"\*\*{field_name}:\*\*\s*(.+?)(?=\n\*\*|\Z)",
            rf"{field_name}:\s*\[(.+?)\]",
            rf"{field_name}:\s*(.+?)(?=\n[A-Z_]+:|\Z)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Clean up common AI response artifacts
                value = value.replace("**", "").strip()
                if value:
                    return value
        return None
    
    def _parse_topic_list(self, text: str) -> List[str]:
        """Parse a comma-separated topic list."""
        if not text:
            return []
        
        # Split by comma and clean up each topic
        topics = [topic.strip() for topic in text.split(",")]
        # Remove empty topics and common artifacts
        topics = [topic for topic in topics if topic and topic.lower() not in ["none", "n/a", "not specified"]]
        return topics[:10]  # Limit to 10 topics max
    
    def _validate_choice(self, value: str, valid_choices: List[str], default: str) -> str:
        """Validate that a value is in the list of valid choices."""
        value_lower = value.lower()
        for choice in valid_choices:
            if choice.lower() == value_lower:
                return choice
        
        # If not found, try partial matching
        for choice in valid_choices:
            if value_lower in choice.lower() or choice.lower() in value_lower:
                return choice
        
        console.print(f"[yellow]⚠️  Invalid value '{value}', using default '{default}'[/yellow]")
        return default
    
    def preview_profile(self, profile: AuthorProfile) -> None:
        """Display a preview of the generated profile."""
        console.print(f"\n[bold blue]📋 Author Profile Preview: {profile.name}[/bold blue]")
        
        # Basic info
        basic_info = f"[bold]Name:[/bold] {profile.name}\n"
        basic_info += f"[bold]ID:[/bold] {profile.author_id}\n"
        basic_info += f"[bold]Description:[/bold] {profile.description}\n"
        
        console.print(Panel(basic_info, title="👤 Basic Information", border_style="blue"))
        
        # Style guide
        style = profile.style_guide
        style_info = f"[bold]Tone:[/bold] {style.tone}\n"
        style_info += f"[bold]Voice:[/bold] {style.voice}\n"  
        style_info += f"[bold]Formality:[/bold] {style.formality}\n"
        style_info += f"[bold]Length:[/bold] {style.length_preference}\n"
        
        if style.topics:
            style_info += f"[bold]Topics:[/bold] {', '.join(style.topics[:5])}\n"
        if style.avoid_topics:
            style_info += f"[bold]Avoid:[/bold] {', '.join(style.avoid_topics[:3])}\n"
        if style.writing_style_notes:
            style_info += f"[bold]Notes:[/bold] {style.writing_style_notes[:200]}{'...' if len(style.writing_style_notes) > 200 else ''}\n"
        
        console.print(Panel(style_info, title="🎭 Style Guide", border_style="green"))
    
    def confirm_profile(self, profile: AuthorProfile) -> bool:
        """Show profile preview and get user confirmation."""
        self.preview_profile(profile)
        
        console.print("\n[yellow]This profile will be used to create training data and fine-tune a model.[/yellow]")
        return Confirm.ask("Does this profile look good?")
    
    def customize_profile(self, profile: AuthorProfile) -> AuthorProfile:
        """Allow user to customize the generated profile."""
        console.print(f"\n[blue]✏️  Customizing profile for {profile.name}[/blue]")
        console.print("Press Enter to keep current values, or type new values to change them.")
        
        from rich.prompt import Prompt
        
        # Allow editing description
        new_description = Prompt.ask("Description", default=profile.description)
        profile.description = new_description
        
        # Allow editing style guide
        style = profile.style_guide
        
        style.tone = Prompt.ask(
            "Tone",
            default=style.tone,
            choices=["casual", "professional", "friendly", "authoritative", "witty", "formal"]
        )
        
        style.voice = Prompt.ask(
            "Voice", 
            default=style.voice,
            choices=["first_person", "second_person", "third_person"]
        )
        
        style.formality = Prompt.ask(
            "Formality",
            default=style.formality, 
            choices=["very_casual", "casual", "moderate", "formal", "academic"]
        )
        
        style.length_preference = Prompt.ask(
            "Length Preference",
            default=style.length_preference,
            choices=["short", "medium", "long", "variable"]
        )
        
        # Topics
        topics_str = ", ".join(style.topics) if style.topics else ""
        new_topics = Prompt.ask("Preferred topics (comma-separated)", default=topics_str)
        style.topics = [t.strip() for t in new_topics.split(",") if t.strip()]
        
        avoid_str = ", ".join(style.avoid_topics) if style.avoid_topics else ""
        new_avoid = Prompt.ask("Topics to avoid (comma-separated)", default=avoid_str) 
        style.avoid_topics = [t.strip() for t in new_avoid.split(",") if t.strip()]
        
        style.writing_style_notes = Prompt.ask("Style notes", default=style.writing_style_notes)
        
        # Update timestamp
        profile.updated_at = datetime.now()
        
        console.print("[green]✅ Profile customized![/green]")
        return profile