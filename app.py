"""Gradio interface for running and submitting the GAIA evaluation."""

import os

import gradio as gr
import pandas as pd
import requests

from agent import BasicAgent

DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"
RESULT_COLUMNS = ["Task ID", "Question", "Submitted Answer"]


def _results_frame(results: list[dict[str, str]]) -> pd.DataFrame:
    return pd.DataFrame(results, columns=RESULT_COLUMNS)


def run_and_submit_all(
    profile: gr.OAuthProfile | None,
) -> tuple[str, pd.DataFrame | None]:
    """Run the agent on every GAIA question and submit successful answers."""
    if profile is None:
        return "Please log in to Hugging Face before running the evaluation.", None

    space_id = os.getenv("SPACE_ID", "").strip()
    if not space_id:
        message = (
            "SPACE_ID is not configured. Run this evaluation from a Hugging Face "
            "Space or set SPACE_ID locally."
        )
        return message, None

    try:
        agent = BasicAgent()
    except Exception as exc:  # noqa: BLE001
        return f"Error initializing agent: {exc}", None

    questions_url = f"{DEFAULT_API_URL}/questions"
    submit_url = f"{DEFAULT_API_URL}/submit"

    try:
        response = requests.get(questions_url, timeout=15)
        response.raise_for_status()
        questions_data = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        return f"The questions endpoint returned invalid JSON: {exc}", None
    except requests.exceptions.Timeout:
        return "Fetching questions failed: the request timed out.", None
    except requests.exceptions.RequestException as exc:
        return f"Fetching questions failed: {exc}", None

    if not isinstance(questions_data, list) or not questions_data:
        return "The questions endpoint returned an empty or invalid question list.", None

    results_log: list[dict[str, str]] = []
    answers_payload: list[dict[str, str]] = []

    for item in questions_data:
        if not isinstance(item, dict):
            results_log.append(
                {
                    "Task ID": "Unknown",
                    "Question": str(item),
                    "Submitted Answer": "AGENT ERROR: Invalid question record.",
                }
            )
            continue

        task_id = item.get("task_id")
        question = item.get("question")
        if not task_id or not isinstance(question, str) or not question.strip():
            results_log.append(
                {
                    "Task ID": str(task_id or "Unknown"),
                    "Question": str(question or ""),
                    "Submitted Answer": (
                        "AGENT ERROR: Question record is missing a task ID or question."
                    ),
                }
            )
            continue

        try:
            submitted_answer = agent(question)
        except Exception as exc:  # noqa: BLE001
            results_log.append(
                {
                    "Task ID": str(task_id),
                    "Question": question,
                    "Submitted Answer": f"AGENT ERROR: {exc}",
                }
            )
            continue

        answers_payload.append(
            {"task_id": task_id, "submitted_answer": submitted_answer}
        )
        results_log.append(
            {
                "Task ID": str(task_id),
                "Question": question,
                "Submitted Answer": submitted_answer,
            }
        )

    results_frame = _results_frame(results_log)
    if not answers_payload:
        return "The agent did not produce any answers to submit.", results_frame

    submission_data = {
        "username": profile.username.strip(),
        "agent_code": f"https://huggingface.co/spaces/{space_id}/tree/main",
        "answers": answers_payload,
    }

    try:
        response = requests.post(submit_url, json=submission_data, timeout=60)
        response.raise_for_status()
        result_data = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        return f"Submission failed: the server returned invalid JSON ({exc}).", results_frame
    except requests.exceptions.Timeout:
        return "Submission failed: the request timed out.", results_frame
    except requests.exceptions.HTTPError as exc:
        detail = exc.response.text[:500]
        try:
            error_data = exc.response.json()
            detail = str(error_data.get("detail", detail))
        except requests.exceptions.JSONDecodeError:
            pass
        return (
            f"Submission failed with status {exc.response.status_code}: {detail}",
            results_frame,
        )
    except requests.exceptions.RequestException as exc:
        return f"Submission failed: {exc}", results_frame

    if not isinstance(result_data, dict):
        return "Submission failed: the server returned an invalid response.", results_frame

    failed_count = len(results_log) - len(answers_payload)
    final_status = (
        "Submission successful!\n"
        f"User: {result_data.get('username', profile.username)}\n"
        f"Overall score: {result_data.get('score', 'N/A')}% "
        f"({result_data.get('correct_count', '?')}/"
        f"{result_data.get('total_attempted', '?')} correct)\n"
        f"Message: {result_data.get('message', 'No message received.')}"
    )
    if failed_count:
        final_status += f"\nSkipped questions: {failed_count}"

    return final_status, results_frame


with gr.Blocks(title="GAIA Agent Evaluation") as demo:
    gr.Markdown("# GAIA Agent Evaluation Runner")
    gr.Markdown(
        "Log in with Hugging Face, then run the evaluation. The app fetches the "
        "GAIA questions, answers them sequentially with Groq, and submits the "
        "successful answers for scoring."
    )

    gr.LoginButton()
    run_button = gr.Button("Run Evaluation & Submit Answers", variant="primary")
    status_output = gr.Textbox(
        label="Evaluation status", lines=6, interactive=False
    )
    results_table = gr.DataFrame(label="Questions and answers", wrap=True)

    run_button.click(
        fn=run_and_submit_all,
        outputs=[status_output, results_table],
    )


if __name__ == "__main__":
    demo.launch()
