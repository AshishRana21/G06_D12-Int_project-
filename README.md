# Agentic RAG + Generative AI Project

This project combines:

- `CrewAI` for multi-agent orchestration
- `Groq` for the agent LLM
- `Hugging Face` Inference API for topic-based image generation
- `PyMuPDF` for PDF text extraction
- HTML, CSS, and JavaScript for the browser UI

## What It Does

Enter a topic and optionally upload a PDF. The app will:

1. Extract text from the uploaded PDF
2. Select relevant PDF chunks for the topic
3. Run a research agent using the PDF context plus web findings
4. Run a summarizing agent to create a student-friendly explanation
5. Generate a matching image
6. Show the generated image first, then the text output below it

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── static/
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── src/
    └── agentic_genai/
        ├── config.py
        ├── crew.py
        ├── image_service.py
        ├── rag.py
        └── tools.py
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
GROQ_MODEL=groq/llama-3.1-8b-instant
HF_IMAGE_PROVIDER=nscale
HF_IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0
```

## Run The App

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:8000
```

## Notes

- PDF uploads are limited to 12 MB.
- The full workflow uses live DuckDuckGo, Groq, and Hugging Face API calls.
- Generated `.zip` archives are ignored by Git.
