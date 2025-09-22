"""
Historical figure dataset generation module.

This module generates training datasets specifically for historical figures,
creating authentic examples that match their documented writing style and era.
"""

import re
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from core.adapters.openai_adapter import OpenAIAdapter
from core.config import settings
from core.historical.figure_research import FigureAnalysis
from core.models import AuthorProfile, Dataset, TrainingExample
from core.prompts.historical_templates import (
    HISTORICAL_EXAMPLE_GENERATION_TEMPLATE,
    estimate_cost,
)

console = Console()


class HistoricalDatasetGenerator:
    """Generate training datasets for historical figures."""

    def __init__(self):
        """Initialize the generator with OpenAI adapter."""
        try:
            self.adapter = OpenAIAdapter()
            self.model = settings.get_default_model("openai")
        except ValueError as e:
            raise ValueError(f"Could not initialize OpenAI adapter: {e}")

    def generate_initial_dataset(
        self, profile: AuthorProfile, figure_analysis: FigureAnalysis, count: int = 10
    ) -> Optional[Dataset]:
        """Generate an initial dataset for a historical figure.

        Args:
            profile: The author profile for this historical figure
            figure_analysis: Detailed analysis of their writing style
            count: Number of training examples to generate

        Returns:
            Dataset with generated examples, or None if failed
        """
        console.print(
            f"[blue]📚 Generating initial dataset for {profile.name} ({count} examples)[/blue]"
        )

        # Estimate cost and confirm
        cost = estimate_cost("example_generation", count)
        console.print(f"[yellow]💰 Estimated cost: ${cost:.3f} (OpenAI API)[/yellow]")

        if not Confirm.ask("Continue with dataset generation?"):
            console.print("[yellow]Dataset generation cancelled[/yellow]")
            return None

        # Create dataset
        dataset = Dataset(author_id=profile.author_id)

        # Generate examples in batches to manage context length
        batch_size = 10  # Generate 10 examples at a time
        batches = [(i, min(batch_size, count - i)) for i in range(0, count, batch_size)]

        total_generated = 0
        for batch_start, batch_count in batches:
            console.print(
                f"[dim]Generating batch {batch_start//batch_size + 1}: examples {batch_start+1}-{batch_start+batch_count}[/dim]"
            )

            batch_examples = self._generate_example_batch(
                profile, figure_analysis, batch_count
            )

            if batch_examples:
                # Review and approve each example
                approved = self._review_examples(batch_examples, profile.name)
                for example in approved:
                    dataset.add_example(example)
                    total_generated += 1

                console.print(
                    f"[green]Batch complete: {len(approved)}/{len(batch_examples)} examples approved[/green]"
                )
            else:
                console.print(
                    "[yellow]⚠️  Failed to generate batch, continuing with next...[/yellow]"
                )

        if total_generated == 0:
            console.print("[red]❌ No examples were generated successfully[/red]")
            return None

        console.print(
            f"[green]🎉 Generated {total_generated} training examples for {profile.name}![/green]"
        )
        return dataset

    def add_examples_to_dataset(
        self,
        dataset: Dataset,
        profile: AuthorProfile,
        figure_analysis: FigureAnalysis,
        count: int = 5,
    ) -> int:
        """Add more examples to an existing dataset.

        Args:
            dataset: Existing dataset to add to
            profile: The author profile
            figure_analysis: Figure analysis for context
            count: Number of examples to add

        Returns:
            Number of examples actually added
        """
        console.print(
            f"[blue]📝 Adding {count} more examples to {profile.name}'s dataset[/blue]"
        )

        # Estimate cost
        cost = estimate_cost("example_generation", count)
        console.print(f"[yellow]💰 Estimated cost: ${cost:.3f}[/yellow]")

        if not Confirm.ask("Continue with example generation?"):
            return 0

        initial_size = dataset.size

        # Generate examples in batches to manage context length
        batch_size = 10
        batches = [(i, min(batch_size, count - i)) for i in range(0, count, batch_size)]

        for batch_start, batch_count in batches:
            console.print(f"[dim]Generating batch {batch_start//batch_size + 1}[/dim]")

            batch_examples = self._generate_example_batch(
                profile, figure_analysis, batch_count
            )

            if batch_examples:
                approved = self._review_examples(batch_examples, profile.name)
                for example in approved:
                    dataset.add_example(example)

        added_count = dataset.size - initial_size
        console.print(f"[green]✅ Added {added_count} new examples to dataset[/green]")
        return added_count

    def _generate_example_batch(
        self, profile: AuthorProfile, figure_analysis: FigureAnalysis, count: int
    ) -> List[TrainingExample]:
        """Generate a batch of training examples."""
        try:
            # Create historical context string
            historical_context = self._create_historical_context(figure_analysis)

            prompt = HISTORICAL_EXAMPLE_GENERATION_TEMPLATE.format(
                figure_name=profile.name,
                tone=profile.style_guide.tone,
                voice=profile.style_guide.voice,
                formality=profile.style_guide.formality,
                length_preference=profile.style_guide.length_preference,
                style_notes=profile.style_guide.writing_style_notes
                or "No specific notes",
                historical_context=historical_context,
                count=count,
            )

            response = self.adapter.generate_text(
                model_id=self.model,
                prompt=prompt,
                max_completion_tokens=10000,  # Increased for longer training examples
            )

            return self._parse_generated_examples(response)

        except Exception as e:
            console.print(f"[red]❌ Error generating example batch: {str(e)}[/red]")
            return []

    def _create_historical_context(self, analysis: FigureAnalysis) -> str:
        """Create historical context for the generation prompt."""
        context_parts = []

        if analysis.historical_context != "Section not found":
            context_parts.append(f"Historical Context: {analysis.historical_context}")

        if analysis.topics_themes != "Section not found":
            context_parts.append(f"Typical Topics: {analysis.topics_themes}")

        if analysis.unique_characteristics != "Section not found":
            context_parts.append(
                f"Unique Characteristics: {analysis.unique_characteristics}"
            )

        return (
            "\n\n".join(context_parts)
            if context_parts
            else "No specific historical context available."
        )

    def _parse_generated_examples(self, response: str) -> List[TrainingExample]:
        """Parse AI response into TrainingExample objects."""
        examples = []

        try:
            # Look for EXAMPLE N: pattern
            example_pattern = r"\*\*EXAMPLE \d+:\*\*"
            example_sections = re.split(example_pattern, response)[
                1:
            ]  # Skip first empty section

            for section in example_sections:
                # Parse each section for User prompt: and Assistant response:
                user_pattern = r"User prompt:\s*(.*?)(?=\nAssistant response:)"
                assistant_pattern = r"Assistant response:\s*(.*?)(?=\n\*\*EXAMPLE|\Z)"

                user_match = re.search(user_pattern, section, re.DOTALL | re.IGNORECASE)
                assistant_match = re.search(
                    assistant_pattern, section, re.DOTALL | re.IGNORECASE
                )

                if user_match and assistant_match:
                    user_prompt = user_match.group(1).strip()
                    assistant_response = assistant_match.group(1).strip()

                    if user_prompt and assistant_response:
                        example = TrainingExample(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a helpful writing assistant.",
                                },
                                {"role": "user", "content": user_prompt},
                                {"role": "assistant", "content": assistant_response},
                            ]
                        )
                        examples.append(example)

            # Fallback parsing if the above doesn't work
            if not examples:
                console.print("[dim]Trying fallback parsing method...[/dim]")
                examples = self._fallback_parse_examples(response)

        except Exception as e:
            console.print(f"[yellow]⚠️  Error parsing examples: {e}[/yellow]")

        return examples

    def _fallback_parse_examples(self, response: str) -> List[TrainingExample]:
        """Fallback method to parse examples when primary parsing fails."""
        examples = []
        lines = response.split("\n")

        current_prompt: Optional[str] = None
        current_response_lines: List[str] = []

        for line in lines:
            line = line.strip()

            if line.startswith("User prompt:") or line.startswith("Prompt:"):
                # Save previous example if exists
                if current_prompt and current_response_lines:
                    response_text = "\n".join(current_response_lines)
                    if response_text.strip():
                        example = TrainingExample(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a helpful writing assistant.",
                                },
                                {"role": "user", "content": current_prompt},
                                {"role": "assistant", "content": response_text},
                            ]
                        )
                        examples.append(example)

                # Start new example
                current_prompt = line.split(":", 1)[1].strip()
                current_response_lines = []

            elif line.startswith("Assistant response:") or line.startswith("Response:"):
                current_response_lines = [line.split(":", 1)[1].strip()]

            elif (
                current_prompt is not None
                and current_response_lines is not None
                and line
                and not line.startswith(("User prompt:", "EXAMPLE"))
            ):
                current_response_lines.append(line)

        # Don't forget the last example
        if current_prompt and current_response_lines:
            response_text = "\n".join(current_response_lines)
            if response_text.strip():
                example = TrainingExample(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful writing assistant.",
                        },
                        {"role": "user", "content": current_prompt},
                        {"role": "assistant", "content": response_text},
                    ]
                )
                examples.append(example)

        return examples

    def _review_examples(
        self, examples: List[TrainingExample], figure_name: str
    ) -> List[TrainingExample]:
        """Allow user to review and approve generated examples."""
        if not examples:
            return []

        console.print(
            f"\n[green]✅ Generated {len(examples)} examples for {figure_name}[/green]"
        )
        console.print("[blue]Please review each example:[/blue]")

        # Ask if user wants to accept all examples at once
        if len(examples) > 1 and Confirm.ask(
            "Would you like to accept all examples without individual review?"
        ):
            console.print(f"[green]✅ Accepted all {len(examples)} examples[/green]")
            return examples

        approved = []

        for i, example in enumerate(examples):
            # Extract prompt and response
            user_msg = next(
                (msg["content"] for msg in example.messages if msg["role"] == "user"),
                "",
            )
            assistant_msg = next(
                (
                    msg["content"]
                    for msg in example.messages
                    if msg["role"] == "assistant"
                ),
                "",
            )

            console.print(f"\n[cyan]--- Example {i+1} of {len(examples)} ---[/cyan]")
            console.print(f"[yellow]Prompt:[/yellow] {user_msg}")
            console.print(f"[green]Response:[/green]")

            # Show response in a panel for better readability
            response_preview = (
                assistant_msg[:300] + "..."
                if len(assistant_msg) > 300
                else assistant_msg
            )
            console.print(Panel(response_preview, border_style="green", padding=(0, 1)))

            if len(assistant_msg) > 300:
                if Confirm.ask("Show full response?"):
                    console.print(
                        Panel(assistant_msg, border_style="dim", title="Full Response")
                    )

            # Get user decision
            action = Prompt.ask(
                "What would you like to do with this example?",
                choices=["accept", "edit", "skip"],
                default="accept",
            )

            if action == "accept":
                approved.append(example)
                console.print("[green]✅ Example accepted[/green]")

            elif action == "edit":
                # Allow editing the response
                console.print(f"[blue]Current response:[/blue] {assistant_msg}")
                new_response = Prompt.ask(
                    "Enter new response (or press Enter to keep current)",
                    default=assistant_msg,
                )

                if new_response.strip():
                    # Create edited example
                    edited_example = TrainingExample(
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful writing assistant.",
                            },
                            {"role": "user", "content": user_msg},
                            {"role": "assistant", "content": new_response},
                        ]
                    )
                    approved.append(edited_example)
                    console.print("[green]✅ Edited example accepted[/green]")
                else:
                    console.print(
                        "[yellow]⚠️  No changes made, skipping example[/yellow]"
                    )

            else:  # skip
                console.print("[yellow]⚠️  Example skipped[/yellow]")

        console.print(
            f"\n[green]Review complete: {len(approved)}/{len(examples)} examples approved[/green]"
        )
        return approved

    def preview_dataset(self, dataset: Dataset, figure_name: str) -> None:
        """Display a preview of the generated dataset."""
        console.print(f"\n[bold blue]📊 Dataset Preview: {figure_name}[/bold blue]")
        console.print(f"[green]Total examples: {dataset.size}[/green]")

        if dataset.size == 0:
            console.print("[yellow]No examples in dataset yet[/yellow]")
            return

        # Show first 3 examples
        for i, example in enumerate(dataset.examples[:3], 1):
            user_msg = next(
                (msg["content"] for msg in example.messages if msg["role"] == "user"),
                "",
            )
            assistant_msg = next(
                (
                    msg["content"]
                    for msg in example.messages
                    if msg["role"] == "assistant"
                ),
                "",
            )

            console.print(f"\n[yellow]Example {i}:[/yellow]")
            console.print(
                f"[dim]Prompt:[/dim] {user_msg[:80]}{'...' if len(user_msg) > 80 else ''}"
            )
            console.print(
                f"[dim]Response:[/dim] {assistant_msg[:120]}{'...' if len(assistant_msg) > 120 else ''}"
            )

        if dataset.size > 3:
            console.print(f"\n[dim]... and {dataset.size - 3} more examples[/dim]")

    def estimate_generation_cost(self, count: int) -> float:
        """Estimate the cost of generating a given number of examples."""
        return estimate_cost("example_generation", count)

    def suggest_dataset_size(self, figure_name: str) -> int:
        """Suggest an appropriate dataset size for fine-tuning."""
        console.print(
            f"\n[blue]📏 Dataset Size Recommendations for {figure_name}:[/blue]"
        )
        console.print("[green]• Minimum effective size: 10-20 examples[/green]")
        console.print("[green]• Good size: 20-50 examples[/green]")
        console.print("[green]• Excellent size: 50+ examples[/green]")
        console.print(
            "\n[dim]More examples generally lead to better style replication,[/dim]"
        )
        console.print("[dim]but also increase cost and training time.[/dim]")

        while True:
            try:
                size = int(
                    Prompt.ask(
                        "How many examples would you like to generate?", default="20"
                    )
                )
                if 1 <= size <= 100:
                    # Show cost estimate
                    cost = self.estimate_generation_cost(size)
                    console.print(
                        f"[yellow]💰 Estimated cost for {size} examples: ${cost:.3f}[/yellow]"
                    )
                    return size
                else:
                    console.print(
                        "[yellow]Please enter a number between 1 and 100[/yellow]"
                    )
            except ValueError:
                console.print("[yellow]Please enter a valid number[/yellow]")
