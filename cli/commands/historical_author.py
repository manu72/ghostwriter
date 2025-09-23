"""
CLI commands for creating authors based on historical figures.

This module provides an AI-assisted workflow for discovering historical figures,
analyzing their writing styles, and creating author profiles for fine-tuning.
"""

from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from core.historical import (
    FigureVerification,
    HistoricalDatasetGenerator,
    HistoricalFigure,
    HistoricalFigureResearcher,
    HistoricalProfileGenerator,
    display_analysis,
    display_figures,
    display_verification,
)
from core.storage import AuthorStorage, get_author_profile

console = Console()
historical_app = typer.Typer()


def _detect_search_mode(query: str) -> str:
    """Detect whether a query is likely a name or description.

    Args:
        query: Search query string

    Returns:
        "name" if likely a name, "description" otherwise
    """
    # Convert to lowercase for analysis
    query_lower = query.lower().strip()

    # Check for obvious name patterns
    name_indicators = [
        # Has typical name structure (2+ capitalized words)
        len([word for word in query.split() if word and word[0].isupper()]) >= 2,
        # Contains common name particles
        any(
            particle in query_lower
            for particle in [" de ", " da ", " von ", " van ", " el ", " al-"]
        ),
        # Shorter queries are more likely to be names
        len(query.split()) <= 3 and len(query) <= 30,
        # Contains personal titles
        any(
            title in query_lower
            for title in [
                "sir ",
                "lord ",
                "lady ",
                "dr. ",
                "professor ",
                "saint ",
                "st. ",
            ]
        ),
    ]

    # Check for description patterns
    description_indicators = [
        # Contains descriptive adjectives
        any(
            adj in query_lower
            for adj in [
                "famous",
                "great",
                "influential",
                "notable",
                "renowned",
                "american",
                "british",
                "french",
                "ancient",
                "modern",
                "classical",
            ]
        ),
        # Contains plural forms suggesting categories
        any(
            plural in query_lower
            for plural in [
                "writers",
                "authors",
                "poets",
                "philosophers",
                "scientists",
                "historians",
                "politicians",
            ]
        ),
        # Contains time periods
        any(
            period in query_lower
            for period in [
                "century",
                "era",
                "period",
                "age",
                "renaissance",
                "medieval",
                "victorian",
                "modern",
            ]
        ),
        # Longer descriptive queries
        len(query.split()) > 4,
        # Contains "who" or similar question words
        any(
            word in query_lower
            for word in ["who", "what", "which", "type of", "kind of"]
        ),
    ]

    # Count indicators
    name_score = sum(name_indicators)
    description_score = sum(description_indicators)

    # If description indicators are strong, it's definitely a description
    if description_score >= 2:
        return "description"

    # If name indicators are strong and no description indicators, it's likely a name
    if name_score >= 2 and description_score == 0:
        return "name"

    # Default to description for ambiguous cases
    return "description"


def _handle_verification_result(
    verification: Optional[FigureVerification], figure_name: str
) -> bool:
    """Handle verification result with optional user override for unverified figures.

    Args:
        verification: The verification result from the researcher
        figure_name: Name of the figure being verified

    Returns:
        True if should proceed (verified or user override), False otherwise
    """
    if not verification:
        console.print(f"[red]❌ Could not verify figure '{figure_name}'[/red]")
        return False

    display_verification(verification)

    # If verified, proceed without question
    if verification.status == "VERIFIED":
        return True

    # For unverified figures, show warning and ask for override
    console.print(
        f"\n[yellow]⚠️  Warning: Figure '{figure_name}' is not verified[/yellow]"
    )
    console.print(f"[yellow]Reason: {verification.reason}[/yellow]")

    if verification.concerns and verification.concerns != "None specified":
        console.print(f"[yellow]Concerns: {verification.concerns}[/yellow]")

    console.print("\n[red]Proceeding with unverified figures may result in:[/red]")
    console.print("[red]• Lower quality training data[/red]")
    console.print("[red]• Inaccurate style analysis[/red]")
    console.print("[red]• Poor model performance[/red]")

    return Confirm.ask(
        "\n[bold red]Are you sure you want to proceed with this unverified figure?[/bold red]",
        default=False,
    )


@historical_app.command("create")
def create_historical_author(
    author_id: str = typer.Option(
        None, "--id", help="Unique ID for the author (auto-generated if not provided)"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--batch", help="Interactive mode (default) vs batch mode"
    ),
    criteria: str = typer.Option(
        None, "--criteria", help="Search criteria for finding historical figures"
    ),
    figure_name: str = typer.Option(
        None, "--figure", help="Specific historical figure name (skips discovery)"
    ),
    dataset_size: int = typer.Option(
        None, "--dataset-size", help="Number of training examples to generate"
    ),
) -> None:
    """🎭 Create a new author profile based on a historical figure."""

    console.print(
        Panel(
            "[bold blue]Historical Figure Author Creator[/bold blue]\n\n"
            "This tool will help you create an AI author based on a historical "
            "or public figure's writing style using AI analysis and generation.\n\n"
            "Process:\n"
            "1. 🔍 Discover or specify historical figure\n"
            "2. 📚 Analyze their writing style\n"
            "3. 🎭 Generate author profile\n"
            "4. 📝 Create training dataset\n"
            "5. ✅ Ready for fine-tuning!",
            title="🏛️  Historical Author Creation",
            border_style="blue",
        )
    )

    if interactive:
        create_historical_author_interactive(
            author_id, criteria, figure_name, dataset_size
        )
    else:
        create_historical_author_batch(author_id, criteria, figure_name, dataset_size)


@historical_app.command("search")
def search_historical_figures(
    query: str = typer.Argument(..., help="Search query (criteria or author name)"),
    count: int = typer.Option(
        5, "--count", "-c", min=1, max=20, help="Number of results to return (1-20)"
    ),
    mode: str = typer.Option(
        "auto", "--mode", "-m", help="Search mode: 'auto', 'description', or 'name'"
    ),
    refine: bool = typer.Option(
        False, "--refine", help="Refine previous search results"
    ),
) -> None:
    """🔍 Search for historical figures based on criteria or name."""

    # Validate mode parameter
    valid_modes = ["auto", "description", "name"]
    if mode not in valid_modes:
        console.print(
            f"[red]Invalid mode '{mode}'. Must be one of: {', '.join(valid_modes)}[/red]"
        )
        raise typer.Exit(1)

    try:
        researcher = HistoricalFigureResearcher()

        if refine:
            # Get feedback for refinement
            feedback = Prompt.ask(
                "What would you like to change about the previous results?"
            )
            figures = researcher.refine_search(query, feedback)
            display_figures(figures, "Refined Search Results")
        else:
            # Determine search mode
            if mode == "auto":
                detected_mode = _detect_search_mode(query)
                console.print(f"[dim]Auto-detected search mode: {detected_mode}[/dim]")
                search_mode = detected_mode
            else:
                search_mode = mode

            # Perform search based on mode
            if search_mode == "name":
                figures = researcher.search_by_name(query, count)
                title = f"Name Search Results ({count} requested)"

                # If no results found with name search, offer fallback to description search
                if not figures:
                    console.print(
                        f"\n[yellow]No figures found with name '{query}'[/yellow]"
                    )
                    if Confirm.ask(
                        "Try searching by description instead?", default=True
                    ):
                        console.print(
                            f"[blue]Falling back to description search...[/blue]"
                        )
                        figures = researcher.discover_figures(query, count)
                        title = (
                            f"Description Search Results (fallback, {count} requested)"
                        )
            else:  # description mode
                figures = researcher.discover_figures(query, count)
                title = f"Description Search Results ({count} requested)"

            display_figures(figures, title)

        if figures:
            console.print(
                f"\n[green]Found {len(figures)} figures matching your search[/green]"
            )
            console.print(
                "Use [cyan]ghostwriter historical create --figure <name>[/cyan] to create an author"
            )
        else:
            console.print("\n[yellow]No figures found matching your search[/yellow]")
            console.print("Try different search terms or increase --count")

    except ValueError as e:
        console.print(f"[red]❌ {str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error searching for figures: {str(e)}[/red]")
        raise typer.Exit(1)


@historical_app.command("analyze")
def analyze_historical_figure(
    figure_name: str = typer.Argument(
        ..., help="Name of the historical figure to analyze"
    )
) -> None:
    """📚 Analyze a historical figure's writing style."""

    try:
        researcher = HistoricalFigureResearcher()

        # Verify figure first
        verification = researcher.verify_figure(figure_name)

        # Use the helper function to handle verification and user override
        if not _handle_verification_result(verification, figure_name):
            raise typer.Exit(1)

        if not Confirm.ask("Proceed with detailed analysis?"):
            return

        # Perform detailed analysis
        analysis = researcher.analyze_figure(figure_name)
        if not analysis:
            console.print("[red]❌ Could not analyze figure[/red]")
            raise typer.Exit(1)

        display_analysis(analysis)
        console.print(f"\n[green]✅ Analysis complete for {figure_name}[/green]")

    except Exception as e:
        console.print(f"[red]Error analyzing figure: {str(e)}[/red]")
        raise typer.Exit(1)


@historical_app.command("build")
def build_historical_dataset(
    author_id: str = typer.Argument(..., help="Author ID to build dataset for"),
    count: int = typer.Option(
        10, "--count", "-c", help="Number of examples to generate"
    ),
) -> None:
    """📊 Generate additional training examples for an existing historical author."""

    from core.models import AuthorSource

    profile = get_author_profile(author_id)
    if not profile:
        console.print(f"[red]Author '{author_id}' not found.[/red]")
        console.print(
            "Use 'ghostwriter historical create' to create a historical author first."
        )
        raise typer.Exit(1)

    # Check if this is a historical author
    if profile.source_type != AuthorSource.HISTORICAL:
        console.print(f"[red]'{author_id}' is not a historical author.[/red]")
        console.print("Use 'ghostwriter dataset build' for regular authors.")
        raise typer.Exit(1)

    console.print(
        f"[bold blue]Building dataset for historical author: {profile.name}[/bold blue]"
    )

    try:
        # Initialize components
        researcher = HistoricalFigureResearcher()
        dataset_generator = HistoricalDatasetGenerator()

        # Re-analyze the figure (we don't store analysis currently)
        console.print(
            f"[blue]Re-analyzing {profile.name} for dataset generation...[/blue]"
        )

        # Verify figure first
        verification = researcher.verify_figure(profile.name)

        # Use the helper function to handle verification and user override
        if not _handle_verification_result(verification, profile.name):
            raise typer.Exit(1)

        # Perform detailed analysis
        analysis = researcher.analyze_figure(profile.name)
        if not analysis:
            console.print(f"[red]❌ Could not analyze figure '{profile.name}'[/red]")
            raise typer.Exit(1)

        # Load existing dataset
        storage = AuthorStorage(author_id)
        dataset = storage.load_dataset()

        if not dataset:
            console.print(f"[red]No dataset found for '{author_id}'.[/red]")
            console.print(
                "This shouldn't happen for historical authors. Try recreating the author."
            )
            raise typer.Exit(1)

        console.print(f"[green]Current dataset: {dataset.size} examples[/green]")

        # Generate additional examples
        added_count = dataset_generator.add_examples_to_dataset(
            dataset, profile, analysis, count
        )

        if added_count > 0:
            # Save updated dataset
            storage.save_dataset(dataset)
            console.print(
                f"\n[green]🎉 Successfully added {added_count} examples to {profile.name}'s dataset![/green]"
            )
            console.print(f"[green]Total dataset size: {dataset.size} examples[/green]")

            # Show next steps
            console.print(
                Panel(
                    f"[bold green]Dataset Updated! 🎉[/bold green]\n\n"
                    f"[bold]What's Next?[/bold]\n\n"
                    f"1. View your dataset:\n"
                    f"   [cyan]ghostwriter dataset show {author_id}[/cyan]\n\n"
                    f"2. Validate dataset quality:\n"
                    f"   [cyan]ghostwriter dataset validate {author_id}[/cyan]\n\n"
                    f"3. Start fine-tuning:\n"
                    f"   [cyan]ghostwriter train start {author_id}[/cyan]",
                    title="🚀 Ready for training!",
                    border_style="green",
                )
            )
        else:
            console.print("[yellow]No examples were added to the dataset.[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Error building dataset: {str(e)}[/red]")
        raise typer.Exit(1)


def create_historical_author_interactive(
    author_id: Optional[str] = None,
    initial_criteria: Optional[str] = None,
    figure_name: Optional[str] = None,
    dataset_size: Optional[int] = None,
) -> None:
    """Interactive historical author creation workflow."""

    try:
        # Initialize components
        researcher = HistoricalFigureResearcher()
        profile_generator = HistoricalProfileGenerator()
        dataset_generator = HistoricalDatasetGenerator()

        # Step 1: Discovery or direct figure specification
        selected_figure = None
        if figure_name:
            console.print(f"[blue]Using specified figure: {figure_name}[/blue]")
            # Create a basic figure object for the specified name
            selected_figure = HistoricalFigure(
                name=figure_name,
                time_period="To be determined",
                writing_style="To be analyzed",
                notable_works="To be analyzed",
                match_criteria="User specified",
            )
        else:
            selected_figure = _interactive_figure_discovery(
                researcher, initial_criteria
            )

        if not selected_figure:
            console.print("[yellow]No figure selected. Exiting.[/yellow]")
            return

        # Step 2: Verification and Analysis
        console.print(
            f"\n[bold blue]Step 2: Analyzing {selected_figure.name}[/bold blue]"
        )

        # Verify the figure
        verification = researcher.verify_figure(selected_figure.name)

        # Use the helper function to handle verification and user override
        if not _handle_verification_result(verification, selected_figure.name):
            return

        if not Confirm.ask("Proceed with creating author profile?"):
            return

        # Perform detailed analysis
        analysis = researcher.analyze_figure(selected_figure.name)
        if not analysis:
            console.print("[red]❌ Could not analyze figure[/red]")
            return

        display_analysis(analysis)

        # Step 3: Profile Generation
        console.print(f"\n[bold blue]Step 3: Generating Author Profile[/bold blue]")

        if not author_id:
            suggested_id = (
                selected_figure.name.lower().replace(" ", "_").replace(".", "")
            )
            author_id = Prompt.ask("Enter author ID", default=suggested_id)

        # Check if author already exists
        if get_author_profile(author_id):
            console.print(f"[red]Author '{author_id}' already exists![/red]")
            if not Confirm.ask("Do you want to choose a different ID?"):
                return
            author_id = Prompt.ask("Enter a different author ID")
            if get_author_profile(author_id):
                console.print("[red]ID still exists. Exiting.[/red]")
                return

        # Generate profile
        profile = profile_generator.generate_profile(analysis, author_id)
        if not profile:
            console.print("[red]❌ Failed to generate profile[/red]")
            return

        # Review and customize profile
        if not profile_generator.confirm_profile(profile):
            console.print("[blue]Let's customize the profile...[/blue]")
            profile = profile_generator.customize_profile(profile)
            if not profile_generator.confirm_profile(profile):
                console.print("[yellow]Profile creation cancelled[/yellow]")
                return

        # Step 4: Dataset Generation
        console.print(f"\n[bold blue]Step 4: Generating Training Dataset[/bold blue]")

        if not dataset_size:
            dataset_size = dataset_generator.suggest_dataset_size(selected_figure.name)

        # Generate initial dataset
        dataset = dataset_generator.generate_initial_dataset(
            profile, analysis, verification, dataset_size
        )
        if not dataset:
            console.print("[red]❌ Failed to generate dataset[/red]")
            return

        dataset_generator.preview_dataset(dataset, selected_figure.name)

        # Ask if they want to add more examples
        if dataset.size > 0 and Confirm.ask(
            "Would you like to generate additional examples?"
        ):
            additional_count = int(
                Prompt.ask("How many additional examples?", default="5")
            )
            dataset_generator.add_examples_to_dataset(
                dataset, profile, analysis, additional_count
            )

        # Step 5: Save everything
        console.print(
            f"\n[bold blue]Step 5: Saving Author Profile and Dataset[/bold blue]"
        )

        storage = AuthorStorage(author_id)
        storage.save_profile(profile)
        storage.save_dataset(dataset)

        console.print(
            f"\n[green]🎉 Historical author '{profile.name}' created successfully![/green]"
        )

        # Show next steps
        _show_next_steps(author_id, dataset.size)

    except Exception as e:
        console.print(
            f"[red]❌ Error during historical author creation: {str(e)}[/red]"
        )
        raise typer.Exit(1)


def create_historical_author_batch(
    author_id: Optional[str] = None,
    criteria: Optional[str] = None,
    figure_name: Optional[str] = None,
    dataset_size: Optional[int] = None,
) -> None:
    """Batch mode historical author creation (less interactive)."""

    if not figure_name and not criteria:
        console.print(
            "[red]❌ Either --figure or --criteria must be provided in batch mode[/red]"
        )
        raise typer.Exit(1)

    if not author_id:
        console.print("[red]❌ --id must be provided in batch mode[/red]")
        raise typer.Exit(1)

    # Check if author already exists
    if get_author_profile(author_id):
        console.print(f"[red]Author '{author_id}' already exists![/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Creating historical author in batch mode...[/blue]")
    console.print(f"Author ID: {author_id}")
    console.print(f"Figure: {figure_name or 'To be discovered'}")
    console.print(f"Dataset size: {dataset_size or 20}")

    # This is a simplified batch implementation
    # In a full implementation, you'd want to handle all the same steps
    # but with minimal user interaction
    console.print("[yellow]⚠️  Batch mode is not fully implemented yet.[/yellow]")
    console.print(
        "Please use interactive mode: [cyan]ghostwriter author create-historical[/cyan]"
    )


def _interactive_figure_discovery(
    researcher: HistoricalFigureResearcher, initial_criteria: Optional[str] = None
) -> Optional[HistoricalFigure]:
    """Interactive figure discovery process."""

    console.print(f"\n[bold blue]Step 1: Discovering Historical Figures[/bold blue]")

    # Get search criteria
    if not initial_criteria:
        console.print("\nDescribe the type of historical figure you're looking for:")
        console.print(
            "[dim]Examples: 'Famous American authors', 'Classical philosophers', 'Renaissance artists'[/dim]"
        )
        initial_criteria = Prompt.ask("Your criteria")

    figures = []
    current_criteria = initial_criteria

    while True:
        # Search for figures
        figures = researcher.discover_figures(current_criteria)

        if not figures:
            console.print("[red]❌ No figures found[/red]")
            if Confirm.ask("Try different criteria?"):
                current_criteria = Prompt.ask("Enter new search criteria")
                continue
            else:
                return None

        display_figures(figures)

        # Let user choose
        console.print(f"\n[green]Found {len(figures)} figures[/green]")
        choice = Prompt.ask(
            "What would you like to do?",
            choices=["select", "refine", "new_search", "quit"],
            default="select",
        )

        if choice == "select":
            return _select_figure_from_list(figures)
        elif choice == "refine":
            feedback = Prompt.ask("What would you like to change about these results?")
            figures = researcher.refine_search(current_criteria, feedback)
            if figures:
                display_figures(figures, "Refined Results")
                if Confirm.ask("Select from these refined results?"):
                    return _select_figure_from_list(figures)
        elif choice == "new_search":
            current_criteria = Prompt.ask("Enter new search criteria")
            continue
        else:
            return None


def _select_figure_from_list(
    figures: List[HistoricalFigure],
) -> Optional[HistoricalFigure]:
    """Let user select a figure from the list."""

    while True:
        try:
            choice = int(
                Prompt.ask(
                    f"Select a figure (1-{len(figures)}, or 0 to cancel)", default="1"
                )
            )

            if choice == 0:
                return None
            elif 1 <= choice <= len(figures):
                selected = figures[choice - 1]

                # Show details and confirm
                console.print(f"\n[bold green]Selected: {selected.name}[/bold green]")
                console.print(f"[dim]Period: {selected.time_period}[/dim]")
                console.print(f"[dim]Style: {selected.writing_style}[/dim]")
                console.print(f"[dim]Works: {selected.notable_works}[/dim]")

                if Confirm.ask("Proceed with this figure?"):
                    return selected
                else:
                    continue
            else:
                console.print(
                    f"[yellow]Please enter a number between 0 and {len(figures)}[/yellow]"
                )

        except ValueError:
            console.print("[yellow]Please enter a valid number[/yellow]")


def _show_next_steps(author_id: str, dataset_size: int) -> None:
    """Display next steps after author creation."""

    console.print(
        Panel(
            f"[bold green]Historical Author Created Successfully! 🎉[/bold green]\n\n"
            f"[bold]What's Next?[/bold]\n\n"
            f"1. Review your author:\n"
            f"   [cyan]ghostwriter author show {author_id}[/cyan]\n\n"
            f"2. Start fine-tuning ({dataset_size} examples ready):\n"
            f"   [cyan]ghostwriter train start {author_id}[/cyan]\n\n"
            f"3. Check training status:\n"
            f"   [cyan]ghostwriter train status {author_id}[/cyan]\n\n"
            f"4. Generate content (after training completes):\n"
            f"   [cyan]ghostwriter generate text {author_id}[/cyan]\n\n"
            f"[dim]The historical figure author is now ready for the standard Ghostwriter workflow![/dim]",
            title="🚀 Next Steps",
            border_style="green",
        )
    )
