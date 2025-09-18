# Ghostwriter Project Overview

## Project Type
Code Project (Python CLI)

## Project Overview
Ghostwriter is a Python command-line interface (CLI) tool designed to empower non-technical users to create and manage personal AI writing assistants. It facilitates the fine-tuning of large language models (LLMs) to mimic a user's unique writing style, tone, and preferences, or to generate content in the style of historical figures. The project aims to democratize LLM fine-tuning, making it accessible for generating various content types like blog posts, articles, essays, and even books, while supporting persistent chat sessions and a feedback loop for continuous improvement.

Key features include:
- **Dataset Builder**: Guided prompts for creating training datasets.
- **Fine-Tune Runner**: CLI for initiating fine-tuning jobs with commercial LLMs (e.g., OpenAI, Google Generative AI).
- **Author Runtime**: Generate content from fine-tuned authors.
- **Chat Conversations**: ChatGPT-style interactions with memory and session persistence.
- **Content Persistence**: Automatic saving of generated content and chat sessions.
- **Historical Figure Authors**: AI-powered discovery, style analysis, profile generation, and dataset creation for historical figures.

## Technologies Used
- **Language**: Python 3.8+
- **CLI Framework**: Typer, Rich
- **Data Validation**: Pydantic, Pydantic-settings
- **HTTP Client**: httpx
- **API Integrations**: openai, google-generativeai
- **Configuration**: python-dotenv, PyYAML
- **Testing**: pytest, pytest-mock, pytest-cov, pytest-typer, responses, freezegun
- **Code Quality**: flake8, black, isort, mypy, bandit

## Building and Running

### Setup
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/manu72/ghostwriter.git
    cd ghostwriter
    ```
2.  **Set up a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Configure API keys**:
    ```bash
    cp .env.example .env
    # Edit .env to add your OPENAI_API_KEY and/or GEMINI_API_KEY
    ```

### Running the CLI
The main entry point for the CLI is `cli.main`.

*   **Traditional manual author creation**:
    ```bash
    python -m cli.main init
    ```
*   **Historical figure author creation**:
    ```bash
    python -m cli.main historical create
    ```
*   **Start a chat conversation**:
    ```bash
    python -m cli.main generate chat <author_id>
    ```
*   **Quick Test (Shakespeare example)**:
    ```bash
    python -m cli.main historical create --figure "William Shakespeare" --id shakespeare
    python -m cli.main train start shakespeare
    python -m cli.main generate chat shakespeare
    ```

For a comprehensive list of commands, refer to the `README.md` or use `python -m cli.main --help`.

## Development Conventions

### Testing
The project uses `pytest` for its comprehensive test suite, targeting 90%+ coverage for core logic.

*   **Run all tests**:
    ```bash
    make test
    # or
    python -m pytest
    ```
*   **Run with coverage report**:
    ```bash
    make test-coverage
    # or
    python -m pytest --cov-report=html --cov-report=term
    ```
*   **Specific test commands (via Makefile)**:
    *   `make test-unit`: Run only unit tests.
    *   `make test-integration`: Run only integration tests.
    *   `make test-fast`: Skip slow tests.
    *   `make clean`: Clean up generated files.

### Code Quality
The project enforces strict code quality standards using various tools.

*   **Formatting**: `black` and `isort` are used for consistent code formatting.
    *   `make format`: Auto-format code.
    *   `make format-check`: Check formatting without changes.
*   **Linting**: `flake8` is used for linting checks.
    *   `make lint`: Run linting checks.
*   **Type Checking**: `mypy` is used for static type checking.
    *   `make type-check`: Run type checking.
*   **Security Scanning**: `bandit` is used for security analysis.
    *   `make security`: Run security scan.
*   **All quality checks**:
    ```bash
    make check
    ```

### Contribution Guidelines
*   Follow the AAA (Arrange, Act, Assert) pattern for tests.
*   Use descriptive test names.
*   Test edge cases and mock external dependencies.
*   Maintain 80%+ test coverage for new code.
*   Use type annotations for all new functions.
*   Update relevant documentation for new features.
*   Ensure no hardcoded secrets or unsafe patterns.

### Pre-commit Checklist
Before submitting a Pull Request, ensure the following:
```bash
black .
isort .
flake8
mypy .
python -m pytest
# Or use the comprehensive check
make check
```