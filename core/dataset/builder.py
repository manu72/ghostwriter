import re
from pathlib import Path
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from core.models import Dataset, TrainingExample
from core.prompts.templates import (
    DATASET_BUILDING_PROMPTS,
    EXAMPLE_GENERATION_PROMPTS,
)
from core.storage import AuthorStorage

console = Console()


class DatasetBuilder:
    def __init__(self, author_id: str):
        self.author_id = author_id
        self.storage = AuthorStorage(author_id)
        self.dataset = self.storage.load_dataset() or Dataset(author_id=author_id)

    def interactive_build(self):
        console.print("\n[bold blue]Dataset Builder[/bold blue]")
        console.print("Let's build a training dataset for your writing style!")

        while True:
            console.print(
                f"\n[green]Current dataset size: {self.dataset.size} examples[/green]"
            )

            choices = [
                "1. Add examples from writing samples",
                "2. Generate examples from prompts",
                "3. Import from text file",
                "4. Review current dataset",
                "5. Save and exit",
            ]

            for choice in choices:
                console.print(choice)

            action = Prompt.ask(
                "\nWhat would you like to do?", choices=["1", "2", "3", "4", "5"]
            )

            if action == "1":
                self._add_from_writing_samples()
            elif action == "2":
                self._generate_examples()
            elif action == "3":
                self._import_from_file()
            elif action == "4":
                self._review_dataset()
            elif action == "5":
                self._save_and_exit()
                break

    def _add_from_writing_samples(self):
        console.print(
            Panel(DATASET_BUILDING_PROMPTS["writing_sample"], title="Writing Sample")
        )

        sample = Prompt.ask("", multiline=True)
        if not sample.strip():
            console.print("[red]No sample provided[/red]")
            return

        console.print(
            Panel(
                DATASET_BUILDING_PROMPTS["prompt_for_sample"], title="Prompt Creation"
            )
        )

        prompt = Prompt.ask("")
        if not prompt.strip():
            console.print("[red]No prompt provided[/red]")
            return

        example = TrainingExample(
            messages=[
                {"role": "system", "content": "You are a helpful writing assistant."},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": sample},
            ]
        )

        self.dataset.add_example(example)
        console.print(
            f"[green]Added example! Dataset now has {self.dataset.size} examples[/green]"
        )

    def _generate_examples(self):
        console.print("\n[bold]Generate Training Examples[/bold]")
        console.print("Choose a prompt type:")

        prompt_types = list(EXAMPLE_GENERATION_PROMPTS.keys())
        for i, ptype in enumerate(prompt_types, 1):
            console.print(f"{i}. {ptype.replace('_', ' ').title()}")

        choice = Prompt.ask(
            "Select prompt type",
            choices=[str(i) for i in range(1, len(prompt_types) + 1)],
        )
        prompt_type = prompt_types[int(choice) - 1]

        topic = Prompt.ask("What topic should this example be about?")

        prompt_template = EXAMPLE_GENERATION_PROMPTS[prompt_type]
        user_prompt = prompt_template.format(
            topic=topic, tone="professional", length_preference="medium"
        )

        console.print(f"\n[yellow]Prompt: {user_prompt}[/yellow]")
        console.print("[blue]Now write your response in your style:[/blue]")

        response = Prompt.ask("", multiline=True)
        if not response.strip():
            console.print("[red]No response provided[/red]")
            return

        example = TrainingExample(
            messages=[
                {"role": "system", "content": "You are a helpful writing assistant."},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": response},
            ]
        )

        self.dataset.add_example(example)
        console.print(
            f"[green]Added example! Dataset now has {self.dataset.size} examples[/green]"
        )

    def _import_from_file(self):
        file_path = Prompt.ask("Enter the path to your text file")
        path = Path(file_path)

        if not path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                console.print("[red]File is empty[/red]")
                return

            sections = self._split_content(content)
            console.print(f"[green]Found {len(sections)} sections in the file[/green]")

            for i, section in enumerate(sections):
                if len(section) < 50:  # Skip very short sections
                    continue

                console.print(f"\n[yellow]Section {i+1}:[/yellow]")
                console.print(section[:200] + "..." if len(section) > 200 else section)

                if Confirm.ask("Include this section?"):
                    prompt = Prompt.ask("What prompt would generate this text?")

                    example = TrainingExample(
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful writing assistant.",
                            },
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": section},
                        ]
                    )

                    self.dataset.add_example(example)
                    console.print("[green]Added![/green]")

            console.print(
                f"[green]Import complete! Dataset now has {self.dataset.size} examples[/green]"
            )

        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")

    def _split_content(self, content: str) -> List[str]:
        # Split on common paragraph separators
        sections = re.split(r"\n\s*\n", content)
        return [section.strip() for section in sections if section.strip()]

    def _review_dataset(self):
        if self.dataset.size == 0:
            console.print("[yellow]Dataset is empty[/yellow]")
            return

        console.print(f"\n[bold]Dataset Review ({self.dataset.size} examples)[/bold]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", width=3)
        table.add_column("Prompt", max_width=40)
        table.add_column("Response Preview", max_width=50)

        for i, example in enumerate(self.dataset.examples[:10], 1):  # Show first 10
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

            prompt_preview = user_msg[:37] + "..." if len(user_msg) > 40 else user_msg
            response_preview = (
                assistant_msg[:47] + "..." if len(assistant_msg) > 50 else assistant_msg
            )

            table.add_row(str(i), prompt_preview, response_preview)

        console.print(table)

        if self.dataset.size > 10:
            console.print(f"[dim]... and {self.dataset.size - 10} more examples[/dim]")

    def _save_and_exit(self):
        if self.dataset.size == 0:
            console.print("[yellow]No examples to save[/yellow]")
            return

        self.storage.save_dataset(self.dataset)
        console.print(
            f"[green]Saved {self.dataset.size} examples to {self.storage.author_dir / 'train.jsonl'}[/green]"
        )

        if self.dataset.size < 10:
            console.print(
                "[yellow]Recommendation: Add more examples (10-100) for better fine-tuning results[/yellow]"
            )
        elif self.dataset.size >= 100:
            console.print(
                "[green]Great! You have enough examples for effective fine-tuning[/green]"
            )
