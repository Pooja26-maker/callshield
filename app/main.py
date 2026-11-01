
import json
import logging
import time
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.usage import get_usage_summary, log_usage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(title="CallShield", version="0.3.0")

SettingsDep = Annotated[Settings, Depends(get_settings)]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    steps: list[str]
    sources: list[str]
    disclaimer: str


SYSTEM_PROMPT = """
You are CallShield, an AI assistant for telecom-related citizen guidance.

Give practical steps in simple language.
Do not invent official links, phone numbers, rules, or source documents.
Document retrieval is not implemented, so always return an empty sources list.

Clearly say that answers are AI-generated and not yet verified against
CallShield's document collection.

For JSON responses, return exactly these four fields:
- answer: a string
- steps: a list of strings
- sources: an empty list
- disclaimer: a string

Return valid JSON only when JSON output is requested.
"""


def create_client(settings: Settings) -> Groq:
    """Create a Groq client using application settings."""
    return Groq(
        api_key=settings.groq_api_key,
        timeout=settings.groq_timeout_seconds,
        max_retries=0,
    )


def model_order(settings: Settings) -> list[str]:
    """Return primary and fallback models without duplicates."""
    return list(
        dict.fromkeys(
            [
                settings.groq_model,
                settings.groq_fallback_model,
            ]
        )
    )


def retry_delay(attempt: int) -> None:
    """Apply a short, capped delay before another attempt."""
    time.sleep(min(2**attempt, 4))


def log_groq_error(
    model: str,
    attempt: int,
    exc: Exception,
) -> None:
    """Log detailed error information without logging credentials."""
    logger.warning(
        "Groq model %s attempt %s failed: %s - %s",
        model,
        attempt + 1,
        type(exc).__name__,
        str(exc),
        exc_info=True,
    )


def generate_json(
    request: ChatRequest,
    settings: Settings,
) -> ChatResponse:
    """Generate a validated JSON response with retries and model fallback."""

    if not settings.groq_api_key:
        raise HTTPException(
            status_code=503,
            detail="Groq API key is not configured.",
        )

    client = create_client(settings)
    last_error: Exception | None = None

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"Citizen's situation:\n{request.message}",
        },
    ]

    for model in model_order(settings):
        for attempt in range(settings.groq_max_retries + 1):
            try:
                logger.info(
                    "Trying Groq model %s, attempt %s",
                    model,
                    attempt + 1,
                )

                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )

                content = response.choices[0].message.content

                if not content:
                    raise ValueError("Groq returned an empty response.")

                chat_response = ChatResponse.model_validate_json(content)

                usage = response.usage

                log_usage(
                    log_path=settings.usage_log_path,
                    model=model,
                    prompt_tokens=getattr(usage, "prompt_tokens", None),
                    candidate_tokens=getattr(
                        usage,
                        "completion_tokens",
                        None,
                    ),
                    total_tokens=getattr(usage, "total_tokens", None),
                    input_price_per_million=(
                        settings.input_price_per_million
                    ),
                    output_price_per_million=(
                        settings.output_price_per_million
                    ),
                )

                logger.info(
                    "Groq response generated successfully using %s",
                    model,
                )

                return chat_response

            except Exception as exc:
                last_error = exc
                log_groq_error(model, attempt, exc)

                if attempt < settings.groq_max_retries:
                    retry_delay(attempt)

    logger.error("All configured Groq models failed.")

    raise HTTPException(
        status_code=502,
        detail=(
            "Groq could not generate a response "
            "using the configured models."
        ),
    ) from last_error


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    """Check application health."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/usage")
def usage(settings: SettingsDep) -> dict:
    """Return accumulated AI usage statistics."""
    return get_usage_summary(settings.usage_log_path)


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    settings: SettingsDep,
) -> ChatResponse:
    """Return structured JSON generated by Groq."""
    return generate_json(request, settings)


@app.post("/chat/stream")
def chat_stream(
    request: ChatRequest,
    settings: SettingsDep,
) -> StreamingResponse:
    """Stream generated text using Server-Sent Events."""

    if not settings.groq_api_key:
        raise HTTPException(
            status_code=503,
            detail="Groq API key is not configured.",
        )

    prompt_messages = [
        {
            "role": "system",
            "content": (
                SYSTEM_PROMPT
                + "\nReturn plain text for this streaming endpoint, not JSON."
            ),
        },
        {
            "role": "user",
            "content": f"Citizen's situation:\n{request.message}",
        },
    ]

    def event_stream():
        client = create_client(settings)

        for model in model_order(settings):
            for attempt in range(settings.groq_max_retries + 1):
                try:
                    # Buffer the complete attempt before emitting tokens.
                    # This avoids duplicate output if a retry is required.
                    chunks: list[str] = []

                    logger.info(
                        "Starting Groq streaming with %s, attempt %s",
                        model,
                        attempt + 1,
                    )

                    stream = client.chat.completions.create(
                        model=model,
                        messages=prompt_messages,
                        stream=True,
                        temperature=0.2,
                    )

                    for chunk in stream:
                        if not chunk.choices:
                            continue

                        content = chunk.choices[0].delta.content

                        if content:
                            chunks.append(content)

                    if not chunks:
                        raise ValueError(
                            "Groq returned an empty streaming response."
                        )

                    # Emit only after the complete attempt succeeds.
                    for token in chunks:
                        yield (
                            "event: token\n"
                            f"data: {json.dumps(token)}\n\n"
                        )

                    logger.info(
                        "Groq streaming completed successfully using %s",
                        model,
                    )

                    yield "event: done\ndata: {}\n\n"
                    return

                except Exception as exc:
                    log_groq_error(model, attempt, exc)

                    if attempt < settings.groq_max_retries:
                        retry_delay(attempt)

        logger.error("All configured Groq streaming attempts failed.")

        yield (
            "event: error\n"
            + "data: "
            + json.dumps(
                {
                    "message": (
                        "Streaming failed for the configured models."
                    )
                }
            )
            + "\n\n"
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
