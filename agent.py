"""Groq-powered agent used by the GAIA evaluation interface."""

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DEFAULT_MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """\
You are an AI agent solving GAIA benchmark questions.

You have access to Groq's built-in browser search when internet research is needed.

Rules:
- Use browser search when the question requires information from the internet.
- For reasoning questions that do not need the internet, answer directly.
- Do not invent facts or search results.
- Follow the exact output format requested by the user.
- Keep the final answer concise.
- If the user asks for only a name, number, code, or comma-separated list,
  return only that answer.
"""


class BasicAgent:
    """Answer GAIA questions with Groq and its server-side browser search."""

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured. Add it to .env locally or to "
                "the Hugging Face Space secrets."
            )

        self.model = os.getenv("MODEL_NAME", DEFAULT_MODEL).strip()
        if not self.model:
            raise ValueError("MODEL_NAME cannot be empty.")

        self.client = Groq(api_key=api_key)
        self.tools = [{"type": "browser_search"}]

    def __call__(self, question: str) -> str:
        """Return one concise final answer for a GAIA question."""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                reasoning_effort="low",
                max_completion_tokens=2048,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Groq request failed for model '{self.model}': {exc}"
            ) from exc

        try:
            final_answer = (response.choices[0].message.content or "").strip()
        except (AttributeError, IndexError, TypeError) as exc:
            raise RuntimeError("Groq returned an invalid response.") from exc
        if not final_answer:
            raise RuntimeError("Groq returned an empty answer.")

        return final_answer
