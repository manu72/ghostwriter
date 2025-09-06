from unittest.mock import Mock, mock_open, patch

from core.dataset.builder import DatasetBuilder
from core.models import Dataset, TrainingExample
from core.storage import AuthorStorage


class TestDatasetBuilder:
    """Test DatasetBuilder class."""

    def test_init(self, temp_data_dir, mock_settings):
        """Test DatasetBuilder initialization."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            assert builder.author_id == "test_author"
            assert isinstance(builder.storage, AuthorStorage)
            assert isinstance(builder.dataset, Dataset)
            assert builder.dataset.author_id == "test_author"

    def test_init_with_existing_dataset(
        self, temp_data_dir, mock_settings, sample_dataset
    ):
        """Test DatasetBuilder initialization with existing dataset."""
        with patch("core.storage.settings", mock_settings):
            # Save dataset first
            storage = AuthorStorage("test_author")
            storage.save_dataset(sample_dataset)

            # Initialize builder - should load existing dataset
            builder = DatasetBuilder("test_author")
            assert builder.dataset.size == sample_dataset.size

    def test_split_content_normal_text(self):
        """Test _split_content with normal paragraph structure."""
        builder = DatasetBuilder("test_author")

        content = """First paragraph with some content.

Second paragraph with different content.

Third paragraph with more text."""

        sections = builder._split_content(content)
        assert len(sections) == 3
        assert sections[0] == "First paragraph with some content."
        assert sections[1] == "Second paragraph with different content."
        assert sections[2] == "Third paragraph with more text."

    def test_split_content_multiple_newlines(self):
        """Test _split_content with multiple newlines between paragraphs."""
        builder = DatasetBuilder("test_author")

        content = """First paragraph.



Second paragraph after multiple newlines.


Third paragraph."""

        sections = builder._split_content(content)
        assert len(sections) == 3
        assert "First paragraph." in sections
        assert "Second paragraph after multiple newlines." in sections
        assert "Third paragraph." in sections

    def test_split_content_empty_sections(self):
        """Test _split_content filters out empty sections."""
        builder = DatasetBuilder("test_author")

        content = """Valid paragraph.


Another valid paragraph.

"""

        sections = builder._split_content(content)
        assert len(sections) == 2
        assert sections[0] == "Valid paragraph."
        assert sections[1] == "Another valid paragraph."

    def test_split_content_single_paragraph(self):
        """Test _split_content with single paragraph."""
        builder = DatasetBuilder("test_author")

        content = "Single paragraph without line breaks."

        sections = builder._split_content(content)
        assert len(sections) == 1
        assert sections[0] == "Single paragraph without line breaks."

    def test_split_content_empty_string(self):
        """Test _split_content with empty string."""
        builder = DatasetBuilder("test_author")

        sections = builder._split_content("")
        assert sections == []

    def test_split_content_whitespace_only(self):
        """Test _split_content with whitespace only."""
        builder = DatasetBuilder("test_author")

        sections = builder._split_content("   \n\n  \t  \n  ")
        assert sections == []

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    def test_add_from_writing_samples(
        self, mock_prompt, mock_console, temp_data_dir, mock_settings
    ):
        """Test _add_from_writing_samples method."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Mock user inputs
            mock_prompt.ask.side_effect = [
                "Sample writing content here.",  # writing sample
                "Write about the topic",  # prompt
            ]

            initial_size = builder.dataset.size
            builder._add_from_writing_samples()

            # Should add one example
            assert builder.dataset.size == initial_size + 1

            # Check the added example
            example = builder.dataset.examples[-1]
            assert len(example.messages) == 3
            assert example.messages[0]["role"] == "system"
            assert example.messages[1]["role"] == "user"
            assert example.messages[1]["content"] == "Write about the topic"
            assert example.messages[2]["role"] == "assistant"
            assert example.messages[2]["content"] == "Sample writing content here."

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    def test_add_from_writing_samples_empty_input(
        self, mock_prompt, mock_console, temp_data_dir, mock_settings
    ):
        """Test _add_from_writing_samples with empty input."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Mock empty sample
            mock_prompt.ask.side_effect = ["", "Some prompt"]

            initial_size = builder.dataset.size
            builder._add_from_writing_samples()

            # Should not add any examples
            assert builder.dataset.size == initial_size
            mock_console.print.assert_called_with("[red]No sample provided[/red]")

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    def test_add_from_writing_samples_empty_prompt(
        self, mock_prompt, mock_console, temp_data_dir, mock_settings
    ):
        """Test _add_from_writing_samples with empty prompt."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Mock empty prompt
            mock_prompt.ask.side_effect = ["Sample content", ""]

            initial_size = builder.dataset.size
            builder._add_from_writing_samples()

            # Should not add any examples
            assert builder.dataset.size == initial_size
            mock_console.print.assert_called_with("[red]No prompt provided[/red]")

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    @patch(
        "core.prompts.templates.EXAMPLE_GENERATION_PROMPTS",
        {
            "creative_writing": "Write creatively about {topic} in a {tone} tone with {length_preference} length.",
            "technical_explanation": "Explain {topic} technically.",
        },
    )
    def test_generate_examples(
        self, mock_prompt, mock_console, temp_data_dir, mock_settings
    ):
        """Test _generate_examples method."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Mock user inputs
            mock_prompt.ask.side_effect = [
                "1",  # prompt type selection
                "artificial intelligence",  # topic
                "AI is fascinating and complex...",  # response
            ]

            initial_size = builder.dataset.size
            builder._generate_examples()

            # Should add one example
            assert builder.dataset.size == initial_size + 1

            # Check the added example
            example = builder.dataset.examples[-1]
            assert "artificial intelligence" in example.messages[1]["content"]
            assert example.messages[2]["content"] == "AI is fascinating and complex..."

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    def test_generate_examples_empty_response(
        self, mock_prompt, mock_console, temp_data_dir, mock_settings
    ):
        """Test _generate_examples with empty response."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Mock inputs with empty response
            mock_prompt.ask.side_effect = ["1", "test topic", ""]

            initial_size = builder.dataset.size

            # Mock EXAMPLE_GENERATION_PROMPTS
            with patch(
                "core.dataset.builder.EXAMPLE_GENERATION_PROMPTS",
                {"test": "Test prompt"},
            ):
                builder._generate_examples()

            # Should not add any examples
            assert builder.dataset.size == initial_size
            mock_console.print.assert_called_with("[red]No response provided[/red]")

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    @patch("core.dataset.builder.Confirm")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="This is the first paragraph with enough content to pass the minimum length requirement for testing purposes.\n\nThis is the second paragraph which also has sufficient content to meet the length requirements for the dataset builder test.",
    )
    @patch("core.dataset.builder.Path")
    def test_import_from_file(
        self,
        mock_path_class,
        mock_file,
        mock_confirm,
        mock_prompt,
        mock_console,
        temp_data_dir,
        mock_settings,
    ):
        """Test _import_from_file method."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Mock Path behavior
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            # Mock user inputs
            mock_prompt.ask.side_effect = [
                "/path/to/file.txt",  # file path
                "What prompt for first paragraph?",  # prompt for first section
                "What prompt for second paragraph?",  # prompt for second section
            ]
            mock_confirm.ask.side_effect = [True, True]  # Include both sections

            initial_size = builder.dataset.size
            builder._import_from_file()

            # Should add two examples (both sections included)
            assert builder.dataset.size == initial_size + 2

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    @patch("core.dataset.builder.Path")
    def test_import_from_file_not_exists(
        self, mock_path_class, mock_prompt, mock_console, temp_data_dir, mock_settings
    ):
        """Test _import_from_file with non-existent file."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Mock Path behavior
            mock_path = Mock()
            mock_path.exists.return_value = False
            mock_path_class.return_value = mock_path

            mock_prompt.ask.return_value = "/nonexistent/file.txt"

            initial_size = builder.dataset.size
            builder._import_from_file()

            # Should not add any examples
            assert builder.dataset.size == initial_size
            mock_console.print.assert_called_with(
                "[red]File not found: /nonexistent/file.txt[/red]"
            )

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch("core.dataset.builder.Path")
    def test_import_from_file_empty(
        self,
        mock_path_class,
        mock_file,
        mock_prompt,
        mock_console,
        temp_data_dir,
        mock_settings,
    ):
        """Test _import_from_file with empty file."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Mock Path behavior
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            mock_prompt.ask.return_value = "/path/to/empty.txt"

            initial_size = builder.dataset.size
            builder._import_from_file()

            # Should not add any examples
            assert builder.dataset.size == initial_size
            mock_console.print.assert_called_with("[red]File is empty[/red]")

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    @patch("builtins.open", side_effect=IOError("Permission denied"))
    @patch("core.dataset.builder.Path")
    def test_import_from_file_read_error(
        self,
        mock_path_class,
        mock_file,
        mock_prompt,
        mock_console,
        temp_data_dir,
        mock_settings,
    ):
        """Test _import_from_file with file read error."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Mock Path behavior
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            mock_prompt.ask.return_value = "/path/to/restricted.txt"

            builder._import_from_file()

            # Should show error message
            mock_console.print.assert_called_with(
                "[red]Error reading file: Permission denied[/red]"
            )

    @patch("core.dataset.builder.console")
    def test_review_dataset_empty(self, mock_console, temp_data_dir, mock_settings):
        """Test _review_dataset with empty dataset."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            builder._review_dataset()

            mock_console.print.assert_called_with("[yellow]Dataset is empty[/yellow]")

    @patch("core.dataset.builder.console")
    def test_review_dataset_with_examples(
        self, mock_console, temp_data_dir, mock_settings, sample_training_examples
    ):
        """Test _review_dataset with examples."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Add examples
            for example in sample_training_examples:
                builder.dataset.add_example(example)

            builder._review_dataset()

            # Should print dataset review header
            mock_console.print.assert_any_call(
                f"\n[bold]Dataset Review ({len(sample_training_examples)} examples)[/bold]"
            )

    @patch("core.dataset.builder.console")
    def test_save_and_exit_empty(self, mock_console, temp_data_dir, mock_settings):
        """Test _save_and_exit with empty dataset."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            builder._save_and_exit()

            mock_console.print.assert_called_with(
                "[yellow]No examples to save[/yellow]"
            )

    @patch("core.dataset.builder.console")
    def test_save_and_exit_with_examples(
        self, mock_console, temp_data_dir, mock_settings, sample_training_examples
    ):
        """Test _save_and_exit with examples."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Add examples
            for example in sample_training_examples:
                builder.dataset.add_example(example)

            builder._save_and_exit()

            # Should save dataset and print success message
            expected_path = builder.storage.author_dir / "train.jsonl"
            mock_console.print.assert_any_call(
                f"[green]Saved {len(sample_training_examples)} examples to {expected_path}[/green]"
            )

    @patch("core.dataset.builder.console")
    def test_save_and_exit_recommendations(
        self, mock_console, temp_data_dir, mock_settings
    ):
        """Test _save_and_exit recommendation messages."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            # Test with few examples (< 10)
            for i in range(5):
                example = TrainingExample(
                    messages=[
                        {"role": "user", "content": f"Test {i}"},
                        {"role": "assistant", "content": f"Response {i}"},
                    ]
                )
                builder.dataset.add_example(example)

            builder._save_and_exit()

            mock_console.print.assert_any_call(
                "[yellow]Recommendation: Add more examples (10-100) for better fine-tuning results[/yellow]"
            )

            # Reset and test with many examples (>= 100)
            mock_console.reset_mock()
            for i in range(95):  # Total will be 100
                example = TrainingExample(
                    messages=[
                        {"role": "user", "content": f"Test {i+5}"},
                        {"role": "assistant", "content": f"Response {i+5}"},
                    ]
                )
                builder.dataset.add_example(example)

            builder._save_and_exit()

            mock_console.print.assert_any_call(
                "[green]Great! You have enough examples for effective fine-tuning[/green]"
            )

    def test_content_filtering_short_sections(self, temp_data_dir, mock_settings):
        """Test that short sections are filtered out during import."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("test_author")

            content = """This is a very long paragraph with more than fifty characters to test filtering.

Short.

Another long paragraph that should not be filtered out because it has enough content to be meaningful."""

            with patch(
                "core.dataset.builder.Confirm.ask", side_effect=[True, True]
            ), patch(
                "core.dataset.builder.Prompt.ask", side_effect=["prompt1", "prompt2"]
            ):

                # Mock the file operations
                sections = builder._split_content(content)

                # Should get 3 sections but only process the long ones
                assert len(sections) == 3

                # Simulate the filtering logic from _import_from_file
                long_sections = [s for s in sections if len(s) >= 50]
                assert len(long_sections) == 2  # Only the long paragraphs


class TestDatasetBuilderIntegration:
    """Integration tests for DatasetBuilder."""

    @patch("core.dataset.builder.console")
    @patch("core.dataset.builder.Prompt")
    @patch("core.dataset.builder.Confirm")
    def test_full_workflow_simulation(
        self, mock_confirm, mock_prompt, mock_console, temp_data_dir, mock_settings
    ):
        """Test a simulated full workflow of dataset building."""
        with patch("core.storage.settings", mock_settings):
            builder = DatasetBuilder("integration_author")

            # Simulate adding from writing sample
            mock_prompt.ask.side_effect = [
                "Sample content for testing",  # writing sample
                "Generate sample content",  # prompt
            ]

            builder._add_from_writing_samples()
            assert builder.dataset.size == 1

            # Simulate saving
            builder._save_and_exit()

            # Verify the dataset was saved
            loaded_dataset = builder.storage.load_dataset()
            assert loaded_dataset.size == 1
            assert (
                "Sample content for testing"
                in loaded_dataset.examples[0].messages[2]["content"]
            )
