from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    openai_api_key: Optional[str] = Field(
        None, validation_alias=AliasChoices("openai_api_key", "OPENAI_API_KEY")
    )
    openai_org_id: Optional[str] = Field(
        None, validation_alias=AliasChoices("openai_org_id", "OPENAI_ORG_ID")
    )
    gemini_api_key: Optional[str] = Field(
        None, validation_alias=AliasChoices("gemini_api_key", "GEMINI_API_KEY")
    )

    # Model configuration
    llm_provider: str = Field(
        "OPENAI", validation_alias=AliasChoices("llm_provider", "LLM_PROVIDER")
    )
    openai_model: str = Field(
        "gpt-4o-mini", validation_alias=AliasChoices("openai_model", "OPENAI_MODEL")
    )
    gemini_model: str = Field(
        "gemini-2.5-flash",
        validation_alias=AliasChoices("gemini_model", "GEMINI_MODEL"),
    )

    # Token limits (can be overridden via .env)
    max_completion_tokens: int = Field(
        10000,
        validation_alias=AliasChoices(
            "max_completion_tokens", "MAX_COMPLETION_TOKENS"
        ),
        description="Default maximum tokens the model may generate in a completion",
    )
    max_context_tokens: int = Field(
        50000,
        validation_alias=AliasChoices("max_context_tokens", "MAX_CONTEXT_TOKENS"),
        description="Approximate maximum tokens allowed in the model's context window",
    )

    # Generation controls
    temperature: float = Field(
        0.7,
        validation_alias=AliasChoices("temperature", "TEMPERATURE"),
        description="Sampling temperature for generation (0.0 - 2.0)",
    )

    # Optional training-specific model for OpenAI fine-tuning
    openai_training_model: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("openai_training_model", "OPENAI_TRAINING_MODEL"),
    )

    debug: bool = Field(False, validation_alias=AliasChoices("debug", "DEBUG"))
    log_level: str = Field(
        "info", validation_alias=AliasChoices("log_level", "LOG_LEVEL")
    )

    data_dir: Path = Field(
        Path("data"), description="Base directory for all data storage"
    )
    authors_dir: Path = Field(
        Path("data/authors"), description="Directory for author profiles"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",  # Allow extra fields like _skip_directory_creation
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Only create directories if not in test mode
        if not kwargs.get("_skip_directory_creation", False):
            self.ensure_directories()

    def ensure_directories(self) -> None:
        # Convert to Path explicitly to satisfy static typing tools
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.authors_dir).mkdir(parents=True, exist_ok=True)

    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)

    def has_gemini_key(self) -> bool:
        return bool(self.gemini_api_key)

    def validate_provider_access(self, provider: str) -> bool:
        if provider == "openai":
            return self.has_openai_key()
        elif provider == "gemini":
            return self.has_gemini_key()
        return False

    def get_default_model(self, provider: Optional[str] = None) -> str:
        """Get the default model for the specified provider or current LLM_PROVIDER."""
        target_provider = provider or self.llm_provider

        if target_provider.upper() == "OPENAI":
            return self.openai_model
        elif target_provider.upper() == "GEMINI":
            return self.gemini_model
        else:
            # Fallback to OpenAI model if provider is unknown
            return self.openai_model

    def get_training_model(self, provider: Optional[str] = None) -> str:
        """Get provider-specific model used for training/fine-tuning.

        For OpenAI, prefer `openai_training_model` if set; otherwise fall back
        to `openai_model`.
        """
        target_provider = provider or self.llm_provider

        if target_provider.upper() == "OPENAI":
            return self.openai_training_model or self.openai_model
        elif target_provider.upper() == "GEMINI":
            return self.gemini_model
        else:
            return self.openai_training_model or self.openai_model

    # --------------------------
    # Validators and normalisers
    # --------------------------
    @field_validator("temperature")
    @classmethod
    def _clamp_temperature(cls, value: float) -> float:
        # Ensure temperature is within a sensible range
        if value is None:
            return 0.7
        return max(0.0, min(2.0, value))

    @field_validator("max_context_tokens")
    @classmethod
    def _clamp_max_context(cls, value: int) -> int:
        # Enforce an upper bound of 128k as requested and minimum of 1
        if value is None:
            return 50000
        return max(1, min(128000, int(value)))

    @field_validator("max_completion_tokens")
    @classmethod
    def _normalise_max_completion(cls, value: int) -> int:
        # Ensure positive integer
        if value is None:
            return 10000
        return max(1, int(value))

    @model_validator(mode="after")
    def _ensure_completion_less_than_context(self) -> "Settings":
        # Guarantee completion tokens are less than context tokens
        if self.max_completion_tokens >= self.max_context_tokens:
            self.max_completion_tokens = max(1, self.max_context_tokens - 1)
        return self


settings = Settings()
