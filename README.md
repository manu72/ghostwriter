# Ghostwriter

Ghostwriter is a tool that empowers non-technical users to create their own personal writing AI.
It helps you finetune a language model so it learns your style, tone, and preferences, or create AI authors based on historical figures.
Over time, your Ghostwriter becomes a unique voice or author that improves through feedback and edits you provide.

---

## Vision

There are three ways to improve the quality of LLM output: prompt engineering, retrieval augmented generation (RAG), and finetuning.
The goal of Ghostwriter is to democratise finetuning. Anyone, not just developers, should be able to:

- Collect and structure a small dataset of writing samples, or create authors based on historical figures.
- Finetune an existing large language model (LLM) into a personal voice or author.
- Generate content that reflects their voice: blog posts, articles, essays, or even books.
- Have conversations with their fine-tuned author, maintaining context and memory across sessions.
- Manage persistent chat sessions with save, resume, and export capabilities.
- Provide feedback on drafts and see the author evolve continuously.

---

## Features (Stage 1)

### Core Features

- **Dataset Builder**: Guided prompts help you prepare a small training dataset in the correct format for the LLM.
- **Fine-Tune Runner**: Simple CLI to start a finetuning job with a commercial LLM.
- **Author Runtime**: Generate drafts from your tuned author with a single command.
- **Chat Conversations**: Full ChatGPT-style conversations with your finetuned model, including conversation memory and session persistence.
- **Content Persistence**: All generated content and chat sessions are automatically saved as markdown files with metadata.
- **Session Management**: Save, resume, and export chat conversations with full history tracking.
- **Feedback Loop**: Rate or edit drafts, turning feedback into new training examples.

### NEW: Historical Figure Authors ✨

- **Enhanced Figure Search**: Intelligent search with auto-detection (name vs. description), configurable result counts (1-20), and smart fallback options
- **AI-Powered Discovery**: Search for historical figures based on your criteria (e.g., "famous poets", "20th century scientists")
- **Direct Name Search**: Find specific authors by name with fuzzy matching and alias detection
- **Automatic Style Analysis**: AI analyses the figure's documented writing style, tone, and characteristics
- **Smart Verification**: AI verifies figure authenticity with detailed reasoning and available sources
- **User Override Option**: Proceed with unverified figures after clear warnings and explicit confirmation
- **🆕 Corpus-Based Dataset Generation**: For well-documented authors (Hemingway, Austen, etc.), incorporates actual quotes and excerpts from their famous works
- **🆕 Intelligent Dataset Modes**: Automatically selects optimal generation strategy:
  - **Corpus-Heavy**: Rich authors get datasets with actual quotes + work excerpts
  - **Hybrid**: Moderate corpus authors get mix of actual content + AI examples
  - **Traditional**: Sparse corpus authors get AI-generated examples only
- **🆕 Enhanced Verification**: Comprehensive corpus assessment including famous works, quote availability, and public domain status
- **Profile Generation**: Automatically creates author profiles with appropriate style guides
- **Training Dataset Creation**: AI generates 15-30 training examples in the historical figure's authentic voice
- **Dataset Expansion**: Add more examples to existing historical authors with `historical build` command
- **Bulk Accept Feature**: Accept all generated examples at once or review individually
- **One-Command Setup**: Complete author creation from discovery to training-ready dataset
- **Cost-Effective**: Full historical author setup typically costs $0.10-0.30, expansion ~$0.05-0.15

---

## Roadmap

### Stage 1: Terminal based POC ✅

- CLI tool for dataset building, validation, and fine-tuning.
- Adaptor for a single commercial provider (OpenAI or Gemini).
- ChatGPT-style conversations with context memory and session persistence.
- Content generation modes: single text, interactive, and chat sessions.
- Feedback mechanism for turning edits into new examples.
- Local storage of datasets (.jsonl) and author profiles.
- AI-powered historical figure author creation with discovery, analysis, and dataset generation.
- Corpus-based dataset generation for well-documented authors with actual quotes and excerpts.
- Intelligent dataset mode selection (Corpus-Heavy/Hybrid/Traditional) based on content availability.
- Enhanced verification system with comprehensive corpus assessment.
- Dataset expansion for historical authors with bulk accept functionality.
- Comprehensive command-line interface with full feature coverage.

### Stage 2: Basic Browser UI

- Minimal web interface to guide dataset creation and fine-tuning.
- Inline editor for reviewing drafts and logging feedback.
- Backend built on FastAPI or Flask, frontend with React or Svelte or Streamlit.
- users will provide their own API keys

### Stage 3: Multiple model support

- Support multiple LLMs (OpenAI, Gemini).
- Local model support via Ollama (DeepSeek, Mistral Small).
- LoRA or PEFT-based finetuning for open models.

### Stage 4: Multiple user accounts

- Secure account creation and login.
- Each user has isolated storage and their own fine-tuned authors.
- Bring-your-own-key support for provider APIs.

### Stage 5: Production ready UI/UX

- Full author dashboard with progress tracking and dataset versioning.
- Job queueing, monitoring, and error handling.
- Export, backup, and delete-my-data options.
- Observability and cost management tools.

---

## Project Structure

```
ghostwriter/
├── cli/                    # Typer-based CLI entrypoints
│   └── commands/
│       ├── author.py      # Manual author creation
│       ├── historical_author.py  # 🆕 Historical figure authors
│       ├── dataset.py     # Dataset building
│       ├── train.py       # Fine-tuning
│       └── generate.py    # Content generation
├── core/
│   ├── adapters/          # openai_adapter.py, gemini_adapter.py
│   ├── dataset/           # builders, validators, splitters
│   ├── feedback/          # edit diff, new examples from feedback
│   ├── eval/              # style metrics, safety checks
│   ├── historical/        # 🆕 Historical figure processing
│   │   ├── figure_research.py    # AI figure discovery & analysis
│   │   ├── profile_generator.py  # Convert analysis to profiles
│   │   └── dataset_generator.py  # Generate historical training data
│   └── prompts/           # system templates
│       └── historical_templates.py  # 🆕 Historical figure prompts
├── data/
│   └── authors/<author_id>/
│       ├── style_guide.yml
│       ├── train.jsonl
│       ├── examples/      # training examples as markdown
│       ├── content/       # generated content as markdown
│       ├── chats/         # 🆕 chat session files
│       ├── edits/
│       └── models.json    # fine-tune job metadata
├── tests/                 # Comprehensive test suite
│   ├── unit/
│   │   └── core/
│   │       └── historical/  # 🆕 Historical feature tests
│   └── integration/
├── .env.example           # API keys and secrets
├── requirements.txt
└── README.md
```

---

## Quickstart (Stage 1 CLI)

1. Clone the repo:

```bash
git clone https://github.com/manu72/ghostwriter.git
cd ghostwriter
```

2. Set up a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Copy `.env.example` → `.env` and add your API keys (and optional defaults):

```bash
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY and/or GEMINI_API_KEY
# Optional defaults:
#   MAX_COMPLETION_TOKENS=10000
#   MAX_CONTEXT_TOKENS=50000
#   TEMPERATURE=0.7
```

4. Run the CLI:

```bash
# Traditional manual author creation
python -m cli.main init

# Or try the new historical figure author creation
python -m cli.main historical create

# After training, start a chat conversation
python -m cli.main generate chat <author_id>
```

### 🚀 Quick Test

Want to see Ghostwriter in action? Try creating a historical author:

```bash
# Create Shakespeare author with one command
python -m cli.main historical create --figure "William Shakespeare" --id shakespeare

# Train the model (after dataset is built)
python -m cli.main train start shakespeare

# Chat with Shakespeare!
python -m cli.main generate chat shakespeare
```

---

## CLI Commands

### Author Management

```bash
# Initialise a new author profile (manual creation)
python -m cli.main init

# List all authors (shows both manual and historical)
python -m cli.main author list

# Show detailed author information
python -m cli.main author show <author_id>
```

### Historical Figure Authors (NEW!)

```bash
# Create historical figure author (interactive)
python -m cli.main historical create

# Search for historical figures (supports various modes and counts)
python -m cli.main historical search "famous American poets"

# NEW: Get more results (1-20)
python -m cli.main historical search "famous poets" --count 15

# NEW: Search by name with auto-detection
python -m cli.main historical search "Virginia Woolf"

# NEW: Explicit search modes
python -m cli.main historical search "Hemingway" --mode name --count 10
python -m cli.main historical search "Mark Twain" --mode description

# Analyse a specific figure's writing style (includes verification check)
python -m cli.main historical analyse "Emily Dickinson"

# Create with specific parameters
python -m cli.main historical create --figure "Mark Twain" --id twain_author --dataset-size 25

# Add more examples to existing historical author
python -m cli.main historical build twain_author --count 15
```

### Dataset Building

```bash
# Build training dataset interactively (manual authors)
python -m cli.main dataset build <author_id>

# Historical authors come with pre-built datasets, but can be extended
python -m cli.main dataset build <historical_author_id>

# Validate dataset quality
python -m cli.main dataset validate <author_id>

# Show dataset information
python -m cli.main dataset show <author_id>

# Export dataset to JSONL format
python -m cli.main dataset export <author_id> --output my_dataset.jsonl

# Clear all training examples (use with caution)
python -m cli.main dataset clear <author_id>
```

### Fine-tuning

```bash
# Start fine-tuning job (works for both manual and historical authors)
python -m cli.main train start <author_id>

# Check training status
python -m cli.main train status <author_id>

# List all training jobs for an author
python -m cli.main train list <author_id>

# Test fine-tuned model quickly
python -m cli.main train test <author_id>

# Generate test content during training workflow
python -m cli.main train generate <author_id> --prompt "Test generation"
```

### Content Generation

```bash
# Generate single piece of content (works for both manual and historical authors)
python -m cli.main generate text <author_id> --prompt "Write about productivity"

# Generate content in Mark Twain's style
python -m cli.main generate text twain_author --prompt "Write about modern technology"

# Interactive generation session (no conversation memory)
python -m cli.main generate interactive <author_id>

# Start a chat conversation with your author (with memory)
python -m cli.main generate chat <author_id>

# Resume an existing chat session
python -m cli.main generate chat <author_id> --session <session_id>

# Chat with auto-save disabled
python -m cli.main generate chat <author_id> --no-save
```

#### Chat Session Commands

Once in a chat session, you can use these commands:

- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/history` - Show full conversation
- `/save` - Manually save session
- `/export` - Export as markdown
- `/info` - Session information
- `/sessions` - List all sessions
- `/quit` - End chat session

---

## Usage Examples

### Complete Workflow: Historical Author

```bash
# 1. Create a historical author (automatically uses corpus-based generation for well-documented figures)
python -m cli.main historical create --figure "Virginia Woolf" --id woolf_author

# System automatically detects: Corpus-Heavy mode for Virginia Woolf
# → Incorporates actual quotes from "To the Lighthouse", "Mrs. Dalloway"
# → Includes excerpts showcasing stream-of-consciousness technique
# → Supplements with AI-generated examples matching her style

# 2. Add more examples if needed
python -m cli.main historical build woolf_author --count 10

# 3. Validate dataset
python -m cli.main dataset validate woolf_author

# 4. Start fine-tuning
python -m cli.main train start woolf_author --wait

# 5. Chat with Virginia Woolf
python -m cli.main generate chat woolf_author
```

### Corpus-Based Dataset Generation Examples

The system automatically selects the optimal dataset generation mode based on the author's documented works:

```bash
# Corpus-Heavy Mode (Rich literary corpus)
python -m cli.main historical create --figure "Ernest Hemingway" --id hemingway
# → Dataset includes actual quotes: "The Sun Also Rises", "A Farewell to Arms"
# → Incorporates excerpts showcasing his distinctive prose style
# → AI generates additional examples matching his voice

python -m cli.main historical create --figure "Jane Austen" --id austen
# → Includes famous quotes about society and wit
# → References excerpts from "Pride and Prejudice", "Emma"
# → Shows her characteristic irony and social commentary

# Hybrid Mode (Moderate corpus)
python -m cli.main historical create --figure "Maya Angelou" --id angelou
# → Mix of actual memorable quotes and AI-generated examples
# → Balances authenticity with comprehensive style coverage

# Traditional Mode (Sparse documented works)
python -m cli.main historical create --figure "Unknown Historical Writer" --id unknown
# → Falls back to AI-generated examples only
# → Still captures documented style characteristics
```

### Complete Workflow: Manual Author

```bash
# 1. Initialize author profile
python -m cli.main init

# 2. Build training dataset
python -m cli.main dataset build my_author

# 3. Validate and train
python -m cli.main dataset validate my_author
python -m cli.main train start my_author

# 4. Generate content
python -m cli.main generate text my_author --prompt "Write about creativity"

# 5. Start interactive session
python -m cli.main generate interactive my_author
```

### Enhanced Historical Figure Search Examples

```bash
# Smart auto-detection examples
python -m cli.main historical search "Mark Twain"           # → Detected as name search
python -m cli.main historical search "famous American authors"  # → Detected as description search
python -m cli.main historical search "Victorian era poets" # → Detected as description search
python -m cli.main historical search "Dr. Martin Luther King"   # → Detected as name search

# Get more results when needed
python -m cli.main historical search "famous poets" --count 15
python -m cli.main historical search "20th century American authors" --count 20

# Explicit mode selection for precise control
python -m cli.main historical search "Hemingway" --mode name --count 10
python -m cli.main historical search "Shakespeare" --mode description  # Forces description search

# Refine search results
python -m cli.main historical search "American writers" --refine
```

**Smart Auto-Detection Features:**
- **Name patterns**: Detects proper names, titles (Dr., Sir), and name particles (von, de)
- **Description patterns**: Identifies adjectives, plurals, time periods, and question words
- **Intelligent fallback**: Offers description search when name search finds no results
- **Cost optimization**: Name searches are more cost-effective than description searches

### Chat Session Example

```bash
$ python -m cli.main generate chat woolf_author

💬 Chat Session
Author: Virginia Woolf
Session: abc123...

💬 Can you help me write about the concept of time in literature?

🤖 Virginia Woolf: Time in literature is not the mechanical ticking of clocks, but
the fluid, subjective experience of consciousness. It flows and eddies, sometimes
rushing past like a river in flood, sometimes pooling in moments of profound
significance...

💬 That's beautiful. Can you expand on how stream of consciousness relates to this?

🤖 Virginia Woolf: Stream of consciousness attempts to capture this very fluidity -
the way thoughts layer upon thoughts, memories intrude upon present moments...

💬 /export
Chat exported to: woolf_author_chat_2024-01-15_142301.md
```

---

## System Commands

```bash
# Get overview of all authors and their status
python -m cli.main status

# Show version information
python -m cli.main version

# Get help for any command
python -m cli.main --help
python -m cli.main generate --help
```

---

## Status

Currently in Stage 1 (terminal-based proof of concept). Expect rapid iteration.

---

## Testing

Ghostwriter includes a comprehensive test suite with 90%+ coverage. The testing framework uses pytest with extensive mocking for external APIs and file operations.

### Quick Start

```bash
# Install all dependencies (including test tools)
pip install -r requirements.txt

# Run all tests
make test
# or
python -m pytest

# Run with coverage report
make test-coverage
# or
python -m pytest --cov-report=html --cov-report=term
```

### Test Commands

#### Using Make (Recommended)

```bash
make test           # Run all tests with coverage
make test-unit      # Run only unit tests
make test-integration  # Run only integration tests
make test-fast      # Skip slow tests
make test-coverage  # Generate detailed coverage report
make clean          # Clean up generated files

# Code quality
make lint           # Run linting checks
make format         # Auto-format code with black/isort
make format-check   # Check formatting without changes
make type-check     # Run mypy type checking
make security       # Run bandit security scan
make check          # Run all quality checks

# Development setup
make dev-install    # Install with pre-commit hooks
```

#### Using pytest directly

```bash
# Basic test runs
python -m pytest                    # All tests
python -m pytest tests/unit         # Unit tests only
python -m pytest tests/integration  # Integration tests only
python -m pytest -m "not slow"      # Fast tests only

# With coverage
python -m pytest --cov=core --cov=cli --cov-report=html

# Specific tests
python -m pytest tests/unit/test_models.py                    # Single file
python -m pytest tests/unit/test_models.py::TestAuthorProfile # Single class
python -m pytest -k "test_author"                            # Pattern matching

# Debugging
python -m pytest -v               # Verbose output
python -m pytest -s               # Don't capture output
python -m pytest --pdb            # Drop into debugger on failure
python -m pytest -x               # Stop on first failure
```

#### Using the test runner script

```bash
python run_tests.py deps          # Check dependencies
python run_tests.py unit          # Unit tests
python run_tests.py integration   # Integration tests
python run_tests.py all           # All tests with coverage
python run_tests.py fast          # Fast tests only
python run_tests.py coverage      # Detailed coverage report
python run_tests.py specific --test-path tests/unit/test_models.py
```

### Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── unit/                          # Unit tests (90%+ coverage target)
│   ├── test_models.py            # Pydantic model validation
│   ├── test_config.py            # Settings and environment
│   ├── test_historical_templates.py  # 🆕 Historical prompt templates
│   ├── core/
│   │   ├── test_dataset_builder.py    # Dataset processing logic
│   │   ├── test_markdown_utils.py     # Markdown content generation
│   │   ├── test_storage.py           # File I/O and data persistence
│   │   ├── historical/               # 🆕 Historical feature tests
│   │   │   ├── test_figure_research.py
│   │   │   ├── test_profile_generator.py
│   │   │   └── test_dataset_generator.py
│   │   └── adapters/
│   │       └── test_openai_adapter.py # API integration (mocked)
│   └── cli/
│       └── commands/
│           └── test_historical_author.py  # 🆕 Historical CLI tests
├── integration/                   # End-to-end workflow tests
│   └── test_cli_workflows.py     # Complete CLI command testing
└── fixtures/                     # Sample data and API responses
    ├── sample_datasets/
    ├── author_profiles/
    └── api_responses/
```

### Test Coverage

- **Minimum Required**: 80% (enforced by CI/CD)
- **Target**: 90%+ for core business logic
- **Current Coverage**: View with `make test-coverage` and open `htmlcov/index.html`

#### Coverage by Module

- **Core Models**: Pydantic validation, properties, business logic
- **Storage System**: File I/O, JSON/YAML/JSONL handling, content persistence, error cases
- **Markdown Utils**: Content generation, filename sanitization, metadata handling
- **Dataset Builder**: Content processing, imports, user interactions
- **OpenAI Adapter**: Full API mocking, job management, error scenarios
- **Historical Features**: Figure research, profile generation, corpus-based dataset creation, CLI commands
- **Corpus-Based Generation**: Dataset mode selection, quote collection, excerpt extraction
- **Prompt Templates**: Template validation, formatting, cost estimation, new corpus templates
- **CLI Commands**: End-to-end command testing with Typer

### Writing Tests

#### Guidelines

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: `test_author_profile_creation_with_custom_style_guide`
3. **Test Edge Cases**: Include error conditions and boundary cases
4. **Mock External Dependencies**: Don't hit real APIs or file systems
5. **Keep Tests Independent**: Each test should be isolated

#### Example Test

```python
def test_author_profile_creation(sample_style_guide):
    """Test AuthorProfile creation with custom StyleGuide."""
    # Arrange
    profile_data = {
        "author_id": "test_author",
        "name": "Test Author",
        "style_guide": sample_style_guide
    }

    # Act
    profile = AuthorProfile(**profile_data)

    # Assert
    assert profile.author_id == "test_author"
    assert profile.name == "Test Author"
    assert profile.style_guide == sample_style_guide
```

### Continuous Integration

Tests run automatically on:

- **Push/PR to main/develop branches**
- **Multiple Python versions**: 3.8, 3.9, 3.10, 3.11
- **Code quality checks**: linting, formatting, type checking, security

#### GitHub Actions Jobs

- **test**: Run unit and integration tests across Python versions
- **lint**: Code formatting (black, isort), linting (flake8), typing (mypy)
- **security**: Security scanning with bandit

### Troubleshooting Tests

#### Common Issues

```bash
# Import errors - ensure PYTHONPATH is set
export PYTHONPATH=$PWD
python -m pytest

# Permission errors - use temp directories in tests
pytest --basetemp=/tmp/pytest

# Slow tests - run fast subset only
python -m pytest -m "not slow"

# Debug specific test
python -m pytest tests/unit/test_models.py::test_author_profile_creation -v -s --pdb
```

#### Test Markers

```bash
# Available markers
python -m pytest --markers

# Run by marker
python -m pytest -m unit           # Unit tests only
python -m pytest -m integration    # Integration tests only
python -m pytest -m "not slow"     # Exclude slow tests
python -m pytest -m openai         # OpenAI-related tests only
```

### Performance Testing

For performance-sensitive tests:

```bash
# Time test execution
python -m pytest --durations=10    # Show 10 slowest tests
python -m pytest --benchmark-only  # Run benchmark tests only
```

### Test Documentation

- **Comprehensive Guide**: See [TESTING.md](TESTING.md) for detailed documentation
- **API Documentation**: Tests serve as examples of API usage
- **Coverage Reports**: Generated in `htmlcov/` directory

---

## Contributing

This project is in early development. Contributions, feedback, and suggestions are welcome!

### Development Setup

```bash
# Clone and setup
git clone https://github.com/manu72/ghostwriter.git
cd ghostwriter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup development tools
make dev-install  # Installs pre-commit hooks

# Before submitting PR
make check        # Run all quality checks
make test         # Ensure tests pass
```

### Code Quality Standards

- **Formatting**: Use `black` and `isort` for consistent code formatting
- **Linting**: Pass `flake8` and `mypy` checks without errors
- **Test Coverage**: Maintain 80%+ coverage for new code
- **Type Hints**: Use type annotations for all new functions
- **Documentation**: Update relevant docs for new features
- **Security**: No hardcoded secrets or unsafe patterns

### Pre-commit Checklist

Before submitting a PR:

```bash
# Format code
black .
isort .

# Run quality checks
flake8
mypy .

# Run tests
python -m pytest

# Or use the comprehensive check
make check  # if Makefile available
```

## License

MIT
