import pytest
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

from core.models import (
    Provider, JobStatus, TrainingExample, StyleGuide, AuthorProfile,
    Dataset, FineTuneJob, ModelMetadata
)


class TestProvider:
    """Test Provider enum."""
    
    def test_provider_values(self):
        """Test Provider enum values."""
        assert Provider.OPENAI == "openai"
        assert Provider.GEMINI == "gemini"
    
    def test_provider_string_comparison(self):
        """Test Provider enum string comparison."""
        assert Provider.OPENAI == "openai"
        assert Provider.GEMINI == "gemini"


class TestJobStatus:
    """Test JobStatus enum."""
    
    def test_job_status_values(self):
        """Test JobStatus enum values."""
        assert JobStatus.PENDING == "pending"
        assert JobStatus.RUNNING == "running"
        assert JobStatus.SUCCEEDED == "succeeded"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.CANCELLED == "cancelled"


class TestTrainingExample:
    """Test TrainingExample model."""
    
    def test_valid_training_example(self):
        """Test creating valid training example."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        example = TrainingExample(messages=messages)
        assert example.messages == messages
    
    def test_minimum_messages_required(self):
        """Test that at least 2 messages are required."""
        # Single message should fail
        with pytest.raises(ValidationError) as exc_info:
            TrainingExample(messages=[{"role": "user", "content": "Hello"}])
        assert "at least 2 messages" in str(exc_info.value)
        
        # Empty messages should fail
        with pytest.raises(ValidationError):
            TrainingExample(messages=[])
    
    def test_message_structure_validation(self):
        """Test message structure validation."""
        # Missing role
        with pytest.raises(ValidationError) as exc_info:
            TrainingExample(messages=[
                {"content": "Hello"},
                {"role": "assistant", "content": "Hi"}
            ])
        assert "role" in str(exc_info.value)
        
        # Missing content
        with pytest.raises(ValidationError) as exc_info:
            TrainingExample(messages=[
                {"role": "user"},
                {"role": "assistant", "content": "Hi"}
            ])
        assert "content" in str(exc_info.value)
    
    def test_invalid_role_validation(self):
        """Test invalid role validation."""
        with pytest.raises(ValidationError) as exc_info:
            TrainingExample(messages=[
                {"role": "invalid_role", "content": "Hello"},
                {"role": "assistant", "content": "Hi"}
            ])
        assert "Role must be one of" in str(exc_info.value)
    
    def test_valid_roles(self):
        """Test all valid roles are accepted."""
        for role in ["system", "user", "assistant"]:
            messages = [
                {"role": role, "content": "Test content"},
                {"role": "assistant", "content": "Response"}
            ]
            example = TrainingExample(messages=messages)
            assert example.messages[0]["role"] == role


class TestStyleGuide:
    """Test StyleGuide model."""
    
    def test_style_guide_defaults(self):
        """Test StyleGuide default values."""
        guide = StyleGuide()
        assert guide.tone == "professional"
        assert guide.voice == "first_person"
        assert guide.formality == "moderate"
        assert guide.length_preference == "medium"
        assert guide.topics == []
        assert guide.avoid_topics == []
        assert guide.writing_style_notes == ""
    
    def test_style_guide_with_custom_values(self):
        """Test StyleGuide with custom values."""
        guide = StyleGuide(
            tone="casual",
            voice="third_person",
            formality="informal",
            length_preference="long",
            topics=["tech", "writing"],
            avoid_topics=["politics"],
            writing_style_notes="Keep it fun and engaging"
        )
        
        assert guide.tone == "casual"
        assert guide.voice == "third_person"
        assert guide.formality == "informal"
        assert guide.length_preference == "long"
        assert guide.topics == ["tech", "writing"]
        assert guide.avoid_topics == ["politics"]
        assert guide.writing_style_notes == "Keep it fun and engaging"
    
    def test_style_guide_extra_fields_allowed(self):
        """Test that extra fields are allowed in StyleGuide."""
        guide = StyleGuide(custom_field="custom_value")
        # Should not raise an error due to Config.extra = "allow"
        assert hasattr(guide, 'custom_field')


class TestAuthorProfile:
    """Test AuthorProfile model."""
    
    def test_author_profile_creation(self, sample_style_guide, freeze_datetime):
        """Test AuthorProfile creation."""
        profile = AuthorProfile(
            author_id="test_author",
            name="Test Author",
            description="A test profile"
        )
        
        assert profile.author_id == "test_author"
        assert profile.name == "Test Author"
        assert profile.description == "A test profile"
        assert isinstance(profile.style_guide, StyleGuide)
        assert profile.created_at == datetime(2023, 1, 1, 12, 0, 0)
        assert profile.updated_at == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_author_profile_with_style_guide(self, sample_style_guide):
        """Test AuthorProfile with custom StyleGuide."""
        profile = AuthorProfile(
            author_id="test_author",
            name="Test Author",
            style_guide=sample_style_guide
        )
        
        assert profile.style_guide == sample_style_guide
    
    def test_author_dir_property(self):
        """Test author_dir property."""
        profile = AuthorProfile(author_id="test_author", name="Test")
        expected_path = Path("data/authors/test_author")
        assert profile.author_dir == expected_path
    
    def test_dataset_path_property(self):
        """Test dataset_path property."""
        profile = AuthorProfile(author_id="test_author", name="Test")
        expected_path = Path("data/authors/test_author/train.jsonl")
        assert profile.dataset_path == expected_path
    
    def test_style_guide_path_property(self):
        """Test style_guide_path property."""
        profile = AuthorProfile(author_id="test_author", name="Test")
        expected_path = Path("data/authors/test_author/style_guide.yml")
        assert profile.style_guide_path == expected_path
    
    def test_models_path_property(self):
        """Test models_path property."""
        profile = AuthorProfile(author_id="test_author", name="Test")
        expected_path = Path("data/authors/test_author/models.json")
        assert profile.models_path == expected_path


class TestDataset:
    """Test Dataset model."""
    
    def test_empty_dataset_creation(self, freeze_datetime):
        """Test creating empty dataset."""
        dataset = Dataset(author_id="test_author")
        
        assert dataset.author_id == "test_author"
        assert dataset.examples == []
        assert dataset.size == 0
        assert dataset.created_at == datetime(2023, 1, 1, 12, 0, 0)
        assert dataset.updated_at == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_dataset_with_examples(self, sample_training_examples):
        """Test dataset with training examples."""
        dataset = Dataset(
            author_id="test_author",
            examples=sample_training_examples
        )
        
        assert dataset.size == len(sample_training_examples)
        assert dataset.examples == sample_training_examples
    
    def test_add_example(self, freeze_datetime):
        """Test adding example to dataset."""
        dataset = Dataset(author_id="test_author")
        initial_updated_at = dataset.updated_at
        
        example = TrainingExample(messages=[
            {"role": "user", "content": "Test"},
            {"role": "assistant", "content": "Response"}
        ])
        
        # Simulate time passing
        from freezegun import freeze_time
        with freeze_time("2023-01-01 13:00:00"):
            dataset.add_example(example)
        
        assert dataset.size == 1
        assert dataset.examples[0] == example
        assert dataset.updated_at > initial_updated_at
    
    def test_size_property(self, sample_training_examples):
        """Test size property calculation."""
        dataset = Dataset(author_id="test_author")
        assert dataset.size == 0
        
        for i, example in enumerate(sample_training_examples, 1):
            dataset.add_example(example)
            assert dataset.size == i


class TestFineTuneJob:
    """Test FineTuneJob model."""
    
    def test_fine_tune_job_creation(self, freeze_datetime):
        """Test FineTuneJob creation."""
        job = FineTuneJob(
            job_id="ft-test-123",
            author_id="test_author",
            provider=Provider.OPENAI,
            base_model="gpt-3.5-turbo"
        )
        
        assert job.job_id == "ft-test-123"
        assert job.author_id == "test_author"
        assert job.provider == Provider.OPENAI
        assert job.base_model == "gpt-3.5-turbo"
        assert job.status == JobStatus.PENDING
        assert job.created_at == datetime(2023, 1, 1, 12, 0, 0)
        assert job.updated_at == datetime(2023, 1, 1, 12, 0, 0)
        assert job.training_file_id is None
        assert job.fine_tuned_model is None
        assert job.hyperparameters == {}
        assert job.result_files == []
        assert job.error_message is None
    
    def test_fine_tune_job_with_optional_fields(self):
        """Test FineTuneJob with optional fields."""
        hyperparams = {"n_epochs": 3, "learning_rate": 0.1}
        result_files = ["results.csv"]
        
        job = FineTuneJob(
            job_id="ft-test-123",
            author_id="test_author",
            provider=Provider.OPENAI,
            base_model="gpt-3.5-turbo",
            status=JobStatus.RUNNING,
            training_file_id="file-123",
            fine_tuned_model="ft:gpt-3.5-turbo:model:123",
            hyperparameters=hyperparams,
            result_files=result_files,
            error_message="Test error"
        )
        
        assert job.status == JobStatus.RUNNING
        assert job.training_file_id == "file-123"
        assert job.fine_tuned_model == "ft:gpt-3.5-turbo:model:123"
        assert job.hyperparameters == hyperparams
        assert job.result_files == result_files
        assert job.error_message == "Test error"
    
    def test_update_status(self, freeze_datetime):
        """Test update_status method."""
        job = FineTuneJob(
            job_id="ft-test-123",
            author_id="test_author",
            provider=Provider.OPENAI,
            base_model="gpt-3.5-turbo"
        )
        
        initial_updated_at = job.updated_at
        
        # Simulate time passing
        from freezegun import freeze_time
        with freeze_time("2023-01-01 13:00:00"):
            job.update_status(
                status=JobStatus.SUCCEEDED,
                fine_tuned_model="ft:gpt-3.5-turbo:model:123",
                error_message=None
            )
        
        assert job.status == JobStatus.SUCCEEDED
        assert job.fine_tuned_model == "ft:gpt-3.5-turbo:model:123"
        assert job.error_message is None
        assert job.updated_at > initial_updated_at
    
    def test_update_status_unknown_attribute(self):
        """Test update_status with unknown attribute."""
        job = FineTuneJob(
            job_id="ft-test-123",
            author_id="test_author",
            provider=Provider.OPENAI,
            base_model="gpt-3.5-turbo"
        )
        
        # Should not raise error but shouldn't set unknown attributes
        job.update_status(status=JobStatus.RUNNING, unknown_field="value")
        assert job.status == JobStatus.RUNNING
        assert not hasattr(job, 'unknown_field')


class TestModelMetadata:
    """Test ModelMetadata model."""
    
    def test_empty_model_metadata(self):
        """Test empty ModelMetadata creation."""
        metadata = ModelMetadata()
        
        assert metadata.fine_tune_jobs == []
        assert metadata.active_model is None
    
    def test_add_job(self, sample_fine_tune_job):
        """Test adding job to metadata."""
        metadata = ModelMetadata()
        metadata.add_job(sample_fine_tune_job)
        
        assert len(metadata.fine_tune_jobs) == 1
        assert metadata.fine_tune_jobs[0] == sample_fine_tune_job
    
    def test_get_job(self, sample_fine_tune_job):
        """Test getting job by ID."""
        metadata = ModelMetadata()
        metadata.add_job(sample_fine_tune_job)
        
        found_job = metadata.get_job(sample_fine_tune_job.job_id)
        assert found_job == sample_fine_tune_job
        
        not_found_job = metadata.get_job("nonexistent-id")
        assert not_found_job is None
    
    def test_get_latest_successful_job(self):
        """Test getting latest successful job."""
        metadata = ModelMetadata()
        
        # Add jobs with different statuses and times
        job1 = FineTuneJob(
            job_id="ft-1",
            author_id="test",
            provider=Provider.OPENAI,
            base_model="gpt-3.5-turbo",
            status=JobStatus.FAILED,
            created_at=datetime(2023, 1, 1),
            updated_at=datetime(2023, 1, 1)
        )
        
        job2 = FineTuneJob(
            job_id="ft-2",
            author_id="test",
            provider=Provider.OPENAI,
            base_model="gpt-3.5-turbo",
            status=JobStatus.SUCCEEDED,
            created_at=datetime(2023, 1, 2),
            updated_at=datetime(2023, 1, 2)
        )
        
        job3 = FineTuneJob(
            job_id="ft-3",
            author_id="test",
            provider=Provider.OPENAI,
            base_model="gpt-3.5-turbo",
            status=JobStatus.SUCCEEDED,
            created_at=datetime(2023, 1, 3),
            updated_at=datetime(2023, 1, 3)
        )
        
        metadata.add_job(job1)
        metadata.add_job(job2)
        metadata.add_job(job3)
        
        # Should return the latest successful job (job3)
        latest = metadata.get_latest_successful_job()
        assert latest == job3
    
    def test_get_latest_successful_job_none_successful(self):
        """Test getting latest successful job when none succeeded."""
        metadata = ModelMetadata()
        
        failed_job = FineTuneJob(
            job_id="ft-1",
            author_id="test",
            provider=Provider.OPENAI,
            base_model="gpt-3.5-turbo",
            status=JobStatus.FAILED
        )
        
        metadata.add_job(failed_job)
        
        latest = metadata.get_latest_successful_job()
        assert latest is None
    
    def test_active_model_property(self):
        """Test active_model property."""
        metadata = ModelMetadata(active_model="ft:gpt-3.5-turbo:model:123")
        assert metadata.active_model == "ft:gpt-3.5-turbo:model:123"