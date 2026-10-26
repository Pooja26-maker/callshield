from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.config import Settings, get_settings

app = FastAPI(title="CallShield", version="0.2.0")

SettingsDep = Annotated[Settings, Depends(get_settings)]


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="The citizen's question or situation",
    )


class ChatResponse(BaseModel):
    answer: str
    steps: list[str]
    sources: list[str]
    disclaimer: str


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    """Check that the application is running."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, settings: SettingsDep) -> ChatResponse:
    """Generate structured citizen-help guidance using Gemini."""

    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured.",
        )

    client = genai.Client(api_key=settings.gemini_api_key)

    prompt = f"""
You are CallShield, an AI assistant that helps citizens understand
telecom-related situations and possible next steps.

User's situation:
{request.message}

Instructions:
- Give clear, practical guidance in simple language.
- Never invent official phone numbers, URLs, rules, or source documents.
- Do not claim you checked official documents or performed an action.
- If the answer depends on current official procedures, tell the user
  to verify them through the relevant official channel.
- The document retrieval system is not implemented yet. Therefore,
  sources must be an empty list.
- Return an answer, an ordered list of steps, an empty sources list,
  and a disclaimer that the response is AI-generated and not yet
  verified against CallShield's document collection.
"""

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ChatResponse,
        ),
         
        )

        if not response.text:
            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty response.",
            )

        return ChatResponse.model_validate_json(response.text)

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Gemini error: {type(exc).__name__}: {exc}")
    raise HTTPException(
        status_code=502,
        detail="Unable to generate a response from Gemini. Check the server terminal.",
    ) from None

