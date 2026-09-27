---
title: Omar GAIA Agent
emoji: 🔎
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 5.25.2
python_version: "3.11"
app_file: app.py
pinned: false
hf_oauth: true
hf_oauth_expiration_minutes: 480
---

# Omar GAIA Agent

A compact AI agent that completes the Hugging Face Agents Course GAIA final
assignment. It uses Groq's server-side browser search to research questions,
submits successful answers to the course scoring API, and displays the score and
per-question results in Gradio.

## Architecture

```text
omar-gaia-agent/
├── app.py              # Gradio, Hugging Face OAuth, evaluation, and submission
├── agent.py            # Groq client, prompt, model, and browser search
├── pyproject.toml       # Local project dependencies
├── uv.lock              # Reproducible local environment
├── requirements.txt     # Hugging Face Spaces dependencies
└── .env.example         # Required environment variables
```

The evaluation is intentionally sequential and simple: fetch the GAIA questions,
run `BasicAgent` once per question, submit the successful answers, and render the
returned score. Browser search is executed by Groq, so the project does not need a
local search implementation or tool-execution loop.

## Local setup

Install the dependencies with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

The project supports Python 3.10 through 3.13. The deployed Space uses Python
3.11, as configured in this README's metadata.

Copy `.env.example` to `.env` and provide your Groq API key:

```dotenv
GROQ_API_KEY=your_key_here
MODEL_NAME=openai/gpt-oss-20b
```

`MODEL_NAME` is optional and defaults to `openai/gpt-oss-20b`. If you override it,
choose a Groq model that supports the built-in `browser_search` tool.

For a local evaluation submission, also set `SPACE_ID` to the Hugging Face Space
identifier, such as `username/space-name`. Then start the interface:

```bash
uv run python app.py
```

## Hugging Face Spaces deployment

1. Create a Gradio Space and push these files to it.
2. Add `GROQ_API_KEY` as a Space secret. Never commit the key.
3. Optionally add `MODEL_NAME` as a Space variable to override the default.
4. Keep the Space public so the scoring service can link to the submitted agent
   source code.

Hugging Face provides `SPACE_ID` and the OAuth profile at runtime. The app uses the
authenticated username in the GAIA submission payload.

## Error handling

Invalid question records and individual agent failures are displayed in the result
table and excluded from the submission. Configuration, network, API, and malformed
response errors are reported in the status panel without exposing secrets.
