# Ghostwriter

Ghostwriter is a tool that empowers non-technical users to create their own personal writing AI.
It helps you fine-tune a language model so it learns your style, tone, and preferences.
Over time, your Ghostwriter becomes a unique "author" that improves through feedback and edits you provide.

---

## Vision

The goal of Ghostwriter is to democratize fine-tuning. Anyone, not just developers, should be able to:

- Collect and structure a small dataset of writing samples.
- Fine-tune an existing large language model (LLM) into a personal "author."
- Generate content that reflects their voice: blog posts, articles, essays, or even books.
- Provide feedback on drafts and see the author evolve continuously.

---

## Features (Stage 1)

- **Dataset Builder**: Guided prompts help you build a small training dataset (100–500 examples).
- **Fine-Tune Runner**: Simple CLI to start a fine-tune job with a commercial LLM (OpenAI first).
- **Author Runtime**: Generate drafts from your tuned author with a single command.
- **Feedback Loop**: Rate or edit drafts, turning feedback into new training examples.

---

## Roadmap

### Stage 1: Terminal-based Proof of Concept

- CLI tool for dataset building, validation, and fine-tuning.
- Adaptor for a single commercial provider (OpenAI or Gemini).
- Feedback mechanism for turning edits into new examples.
- Local storage of datasets (.jsonl) and author profiles.

### Stage 2: Basic Browser UI

- Minimal web interface to guide dataset creation and fine-tuning.
- Inline editor for reviewing drafts and logging feedback.
- Backend built on FastAPI or Flask, frontend with React or Svelte.

### Stage 3: Multi-Model Support

- Support multiple LLMs (OpenAI, Gemini).
- Local model support via Ollama (DeepSeek, Mistral Small).
- LoRA or PEFT-based fine-tuning for open models.

### Stage 4: Multi-User Accounts

- Secure account creation and login.
- Each user has isolated storage and their own fine-tuned authors.
- Bring-your-own-key support for provider APIs.

### Stage 5: Production-Ready UI/UX

- Full author dashboard with progress tracking and dataset versioning.
- Job queueing, monitoring, and error handling.
- Export, backup, and delete-my-data options.
- Observability and cost management tools.

---

## Project Structure

```
ghostwriter/
├── cli/                    # Typer-based CLI entrypoints
├── core/
│   ├── adapters/          # openai_adapter.py, gemini_adapter.py
│   ├── dataset/           # builders, validators, splitters
│   ├── feedback/          # edit diff, new examples from feedback
│   ├── eval/              # style metrics, safety checks
│   └── prompts/           # system templates
├── data/
│   └── authors/<author_id>/
│       ├── style_guide.yml
│       ├── train.jsonl
│       ├── edits/
│       └── models.json    # fine-tune job metadata
├── .env.example           # API keys and secrets
├── requirements.txt
└── README.md
```

---

## Quickstart (Stage 1 CLI)

1. Clone the repo:

```bash
git clone https://github.com/<your-username>/ghostwriter.git
cd ghostwriter
```

2. Set up a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Copy `.env.example` → `.env` and add your API key.

4. Run the CLI:

```bash
python -m cli.main init
```

---

## Status

Currently in Stage 1 (terminal-based proof of concept). Expect rapid iteration.

---

## License

MIT (to be confirmed).
