import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import jsonlines
import yaml

from core.config import settings
from core.markdown_utils import save_example_as_markdown
from core.models import AuthorProfile, Dataset, ModelMetadata, TrainingExample


class AuthorStorage:
    def __init__(self, author_id: str) -> None:
        self.author_id = author_id
        self.author_dir = settings.authors_dir / author_id
        self.author_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_examples_directory()

    def save_profile(self, profile: AuthorProfile) -> None:
        profile_path = self.author_dir / "profile.json"
        with open(profile_path, "w") as f:
            json.dump(profile.model_dump(), f, indent=2, default=str)

        style_guide_path = self.author_dir / "style_guide.yml"
        with open(style_guide_path, "w") as f:
            yaml.dump(profile.style_guide.model_dump(), f, default_flow_style=False)

    def load_profile(self) -> Optional[AuthorProfile]:
        profile_path = self.author_dir / "profile.json"
        if not profile_path.exists():
            return None

        with open(profile_path, "r") as f:
            data = json.load(f)
        return AuthorProfile(**data)

    def save_dataset(self, dataset: Dataset) -> None:
        dataset_path = self.author_dir / "train.jsonl"
        with jsonlines.open(dataset_path, "w") as writer:
            for example in dataset.examples:
                writer.write(example.model_dump())

    def load_dataset(self) -> Optional[Dataset]:
        dataset_path = self.author_dir / "train.jsonl"
        if not dataset_path.exists():
            return Dataset(author_id=self.author_id)

        examples = []
        with jsonlines.open(dataset_path, "r") as reader:
            for obj in reader:
                examples.append(TrainingExample(**obj))

        return Dataset(author_id=self.author_id, examples=examples)

    def save_model_metadata(self, metadata: ModelMetadata) -> None:
        models_path = self.author_dir / "models.json"
        with open(models_path, "w") as f:
            json.dump(metadata.model_dump(), f, indent=2, default=str)

    def load_model_metadata(self) -> ModelMetadata:
        models_path = self.author_dir / "models.json"
        if not models_path.exists():
            return ModelMetadata()

        with open(models_path, "r") as f:
            data = json.load(f)
        return ModelMetadata(**data)

    def exists(self) -> bool:
        return self.author_dir.exists() and (self.author_dir / "profile.json").exists()

    def _ensure_examples_directory(self) -> Path:
        """Ensure the examples directory exists for this author."""
        examples_dir = self.author_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        return examples_dir

    def save_example_as_markdown(
        self,
        prompt: str,
        response: str,
        example_type: str,
        timestamp: Optional[datetime] = None,
    ) -> Path:
        """Save a training example as a markdown file.

        Args:
            prompt: The user prompt
            response: The assistant response
            example_type: 'user' or 'llm'
            timestamp: Optional timestamp, defaults to current time

        Returns:
            Path to the created markdown file
        """
        return save_example_as_markdown(
            self.author_dir, prompt, response, example_type, timestamp
        )

    @property
    def examples_dir(self) -> Path:
        """Get the examples directory path."""
        return self.author_dir / "examples"


def list_authors() -> List[str]:
    if not settings.authors_dir.exists():
        return []

    authors = []
    for author_dir in settings.authors_dir.iterdir():
        if author_dir.is_dir() and (author_dir / "profile.json").exists():
            authors.append(author_dir.name)

    return sorted(authors)


def get_author_profile(author_id: str) -> Optional[AuthorProfile]:
    storage = AuthorStorage(author_id)
    return storage.load_profile()
