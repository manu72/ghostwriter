from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class Provider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainingExample(BaseModel):
    messages: List[Dict[str, str]] = Field(
        description="OpenAI chat format training example"
    )

    @validator("messages")
    def validate_messages(cls, v):
        if not v or len(v) < 2:
            raise ValueError("Training example must have at least 2 messages")

        valid_roles = {"system", "user", "assistant"}
        for msg in v:
            if "role" not in msg or "content" not in msg:
                raise ValueError("Each message must have 'role' and 'content' fields")
            if msg["role"] not in valid_roles:
                raise ValueError(f"Role must be one of {valid_roles}")

        return v


class StyleGuide(BaseModel):
    tone: str = Field(
        default="professional",
        description="Writing tone (e.g., casual, professional, witty)",
    )
    voice: str = Field(
        default="first_person",
        description="Narrative voice (e.g., first_person, third_person)",
    )
    formality: str = Field(
        default="moderate",
        description="Formality level (e.g., casual, moderate, formal)",
    )
    length_preference: str = Field(
        default="medium",
        description="Preferred content length (e.g., short, medium, long)",
    )
    topics: List[str] = Field(
        default_factory=list, description="Preferred topics or domains"
    )
    avoid_topics: List[str] = Field(default_factory=list, description="Topics to avoid")
    writing_style_notes: str = Field(
        default="", description="Additional style preferences"
    )

    class Config:
        extra = "allow"


class AuthorProfile(BaseModel):
    author_id: str = Field(description="Unique identifier for the author")
    name: str = Field(description="Display name for the author")
    description: str = Field(default="", description="Brief description of the author")
    style_guide: StyleGuide = Field(default_factory=StyleGuide)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def author_dir(self) -> Path:
        return Path("data/authors") / self.author_id

    @property
    def dataset_path(self) -> Path:
        return self.author_dir / "train.jsonl"

    @property
    def style_guide_path(self) -> Path:
        return self.author_dir / "style_guide.yml"

    @property
    def models_path(self) -> Path:
        return self.author_dir / "models.json"


class Dataset(BaseModel):
    author_id: str
    examples: List[TrainingExample] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def size(self) -> int:
        return len(self.examples)

    def add_example(self, example: TrainingExample):
        self.examples.append(example)
        self.updated_at = datetime.now()


class FineTuneJob(BaseModel):
    job_id: str = Field(description="Provider's job identifier")
    author_id: str
    provider: Provider
    base_model: str = Field(description="Base model name (e.g., gpt-3.5-turbo)")
    status: JobStatus = Field(default=JobStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    training_file_id: Optional[str] = Field(
        None, description="Provider's training file ID"
    )
    fine_tuned_model: Optional[str] = Field(
        None, description="ID of the fine-tuned model"
    )
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    result_files: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None

    def update_status(self, status: JobStatus, **kwargs):
        self.status = status
        self.updated_at = datetime.now()

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class ModelMetadata(BaseModel):
    fine_tune_jobs: List[FineTuneJob] = Field(default_factory=list)
    active_model: Optional[str] = Field(
        None, description="Currently active fine-tuned model"
    )

    def add_job(self, job: FineTuneJob):
        self.fine_tune_jobs.append(job)

    def get_job(self, job_id: str) -> Optional[FineTuneJob]:
        return next((job for job in self.fine_tune_jobs if job.job_id == job_id), None)

    def get_latest_successful_job(self) -> Optional[FineTuneJob]:
        successful_jobs = [
            job for job in self.fine_tune_jobs if job.status == JobStatus.SUCCEEDED
        ]
        return (
            max(successful_jobs, key=lambda x: x.updated_at)
            if successful_jobs
            else None
        )
