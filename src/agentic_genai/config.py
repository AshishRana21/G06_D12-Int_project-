from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    hf_token: str
    groq_model: str = "groq/llama-3.1-8b-instant"
    hf_image_provider: str = "nscale"
    hf_image_model: str = "stabilityai/stable-diffusion-xl-base-1.0"


def load_settings() -> Settings:
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
    hf_token = os.getenv("HF_TOKEN", "").strip()
    groq_model = os.getenv("GROQ_MODEL", "groq/llama-3.1-8b-instant").strip()
    hf_image_provider = os.getenv("HF_IMAGE_PROVIDER", "nscale").strip()
    hf_image_model = os.getenv("HF_IMAGE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0").strip()

    return Settings(
        groq_api_key=groq_api_key,
        hf_token=hf_token,
        groq_model=groq_model,
        hf_image_provider=hf_image_provider,
        hf_image_model=hf_image_model,
    )
