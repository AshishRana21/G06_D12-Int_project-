from __future__ import annotations

from io import BytesIO
import time

import httpx
from huggingface_hub import InferenceClient
from PIL import Image

from agentic_genai.config import Settings


FALLBACK_IMAGE_MODELS = (
    "stabilityai/stable-diffusion-xl-base-1.0",
    "black-forest-labs/FLUX.1-schnell",
)


def build_image_prompt(topic: str) -> str:
    return (
        f"Create a high-quality educational illustration about {topic}. "
        "Make it visually rich, accurate to the topic, engaging for learners, and easy to understand."
    )


def _normalize_image(image: Image.Image | bytes) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    return Image.open(BytesIO(image))


def _candidate_models(primary_model: str) -> list[str]:
    models = [primary_model]
    for model in FALLBACK_IMAGE_MODELS:
        if model not in models:
            models.append(model)
    return models


def generate_topic_image(topic: str, settings: Settings) -> Image.Image:
    if not settings.hf_token:
        raise ValueError("Missing HF_TOKEN. Add it to your environment or .env file.")

    prompt = build_image_prompt(topic)
    errors: list[str] = []

    for model in _candidate_models(settings.hf_image_model):
        client = InferenceClient(
            provider=settings.hf_image_provider,
            api_key=settings.hf_token,
        )

        for attempt in range(1, 4):
            try:
                image = client.text_to_image(
                    prompt=prompt,
                    model=model,
                    guidance_scale=7.0,
                    num_inference_steps=18,
                    width=1024,
                    height=768,
                )
                return _normalize_image(image)
            except httpx.HTTPError as exc:
                errors.append(f"{model} attempt {attempt}: {exc}")
                time.sleep(min(attempt * 2, 6))
            except Exception as exc:
                errors.append(f"{model} attempt {attempt}: {exc}")
                break

    raise RuntimeError(
        "Image generation failed after retries. "
        "This is usually a temporary Hugging Face provider/network issue. "
        f"Last errors: {' | '.join(errors[-3:])}"
    )
