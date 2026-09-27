
# Omar GAIA Agent

A lightweight agent built for the final assignment of the Hugging Face Agents Course.

The project evaluates a Groq-powered agent on the GAIA Level 1 benchmark. The agent uses `openai/gpt-oss-20b` with Groq's built-in browser search, submits answers to the course evaluation API, and displays the resulting score and per-question outputs through a Gradio interface.

## Overview

The application follows a simple evaluation pipeline:

```text
GAIA Question
    ↓
BasicAgent
    ↓
Groq LLM
    ↓
Browser Search when required
    ↓
Final Answer
    ↓
GAIA Scoring API
```

The implementation intentionally keeps the agent architecture small. It focuses on direct reasoning and web research rather than supporting every input modality in the GAIA benchmark.

## Project Structure

```text
omar-gaia-agent/
├── app.py
├── agent.py
├── pyproject.toml
├── uv.lock
├── requirements.txt
└── .env.example
```

### `app.py`

Handles:

- Gradio interface
- Hugging Face OAuth
- question retrieval
- evaluation execution
- submission to the scoring API
- result display

### `agent.py`

Contains:

- Groq client configuration
- model selection
- system prompt
- browser search configuration
- final answer generation

## Evaluation

The agent was evaluated on the 20 GAIA Level 1 questions provided by the Hugging Face Agents Course.

Result:

```text
Score: 35%
Correct answers: 7 / 20
```

The course certification threshold was exceeded.

The current implementation performs best on questions that require:

- direct reasoning
- factual web research
- concise answer formatting

It does not currently provide dedicated support for:

- audio transcription
- video understanding
- image-based reasoning
- spreadsheet analysis
- attached code execution

## Local Setup

This project uses `uv` for dependency management.

Install dependencies:

```bash
uv sync
```

Create a `.env` file from `.env.example`:

```env
GROQ_API_KEY=your_key_here
MODEL_NAME=openai/gpt-oss-20b
```

Start the application:

```bash
uv run python app.py
```

When running locally, Hugging Face OAuth requires an authenticated Hugging Face session.

You can log in with:

```bash
hf auth login
```

## Configuration

### Required

```env
GROQ_API_KEY=
```

### Optional

```env
MODEL_NAME=openai/gpt-oss-20b
```

The selected model must support Groq's built-in `browser_search` tool.

When deployed on Hugging Face Spaces, `SPACE_ID` and the authenticated Hugging Face user profile are provided by the platform.

For local submission testing, `SPACE_ID` can be set manually.

## Hugging Face Spaces

To deploy the project:

1. Create a public Gradio Space.
2. Push the repository contents to the Space.
3. Add `GROQ_API_KEY` as a Space secret.
4. Add `MODEL_NAME` as a Space variable if you want to override the default model.

The Space should remain public because the evaluation service includes the repository URL in the submission.

## Design Notes

The original Hugging Face assignment template was kept intentionally simple.

The main changes in this implementation are:

- moving agent logic into a separate module
- using Groq as the LLM provider
- using Groq's server-side browser search instead of a custom search tool
- adding environment-based configuration
- using `uv` for dependency management
- improving error handling and project structure

No multi-agent framework is used, and the project does not depend on LangChain or LangGraph.

## License

This repository contains my implementation of the Hugging Face Agents Course final assignment. Course materials and the GAIA benchmark remain subject to their respective licenses.
