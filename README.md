# 🚀 Agentic RAG Studio

## 📌 Overview

**Agentic RAG Studio** is a Python-based web application that combines **Agentic AI**, **Retrieval-Augmented Generation (RAG)**, PDF processing, web search, LLM-powered research, teaching-style summarization, and AI image generation.

Users can enter a research topic and optionally upload a PDF. The system extracts relevant context, performs web search, runs multi-agent workflows, and generates:

* 📊 Research Report
* 📘 Teaching Summary
* 🖼️ Educational Image

All results are displayed in a clean browser interface.

---

## ✨ Features

* Topic-based research generation
* Optional PDF upload
* PDF text extraction using PyMuPDF
* Relevant PDF context selection
* DuckDuckGo web search integration
* CrewAI multi-agent workflow
* Research Agent for concise reports
* Summarize Agent for student-friendly explanations
* Hugging Face image generation
* Visual educational image output
* Teaching Summary, Research Notes, Raw Output tabs
* Frontend progress animation and status updates
* Environment-based API configuration

---

## 🛠️ Tech Stack

* Python
* Built-in HTTP Server (`BaseHTTPRequestHandler`)
* HTML, CSS, JavaScript
* CrewAI
* Groq LLM
* Hugging Face Inference API
* DuckDuckGo Search
* PyMuPDF
* Pillow
* python-dotenv

---

## 🧠 Architecture / Workflow

1. User enters a topic (+ optional PDF)
2. Backend validates input
3. PDF (if uploaded) is processed:

   * Extract → Clean → Chunk → Select relevant context
4. Web search is performed
5. CrewAI workflow runs:

   * Research Agent → generates report
   * Summarize Agent → creates teaching summary
6. Image prompt is generated
7. Hugging Face generates an educational image
8. Results returned as JSON
9. Frontend renders output in UI tabs

👉 If no PDF is uploaded, **web findings are used as the source material**.

---

## 📁 Project Structure

```
app.py
requirements.txt
Dockerfile

static/
  index.html
  styles.css
  app.js

src/
  agentic_genai/
    __init__.py
    config.py
    crew.py
    image_service.py
    rag.py
    tools.py
```

---

## 📂 Important Files

* **app.py**
  Starts backend server, handles routes, processes input, coordinates PDF, CrewAI, and image generation.

* **config.py**
  Loads environment variables and API configurations.

* **rag.py**
  Handles PDF validation, extraction, cleaning, chunking, and context selection.

* **crew.py**
  Defines CrewAI agents, tasks, and workflow.

* **tools.py**
  Handles DuckDuckGo web search.

* **image_service.py**
  Generates educational images using Hugging Face.

* **static/index.html**
  UI layout.

* **static/styles.css**
  Styling for frontend.

* **static/app.js**
  Handles API calls, UI updates, and rendering.

---

## 🔐 Environment Variables

Create a `.env` file and add:

```
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
GROQ_MODEL=groq/llama-3.1-8b-instant
HF_IMAGE_PROVIDER=nscale
HF_IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0
```

---

## ⚙️ Installation

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## ▶️ Running the Application

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:8000
```

---

## 🧑‍💻 Usage Guide

1. Open the web app
2. Enter a research topic
3. (Optional) Upload a PDF
4. Click **Generate Summary**
5. View:

   * 🖼️ Generated Image
   * 📘 Teaching Summary
   * 📊 Research Notes
   * 🧾 Raw Output

---

## 🔗 API Endpoint

### `POST /api/generate`

### Form Fields:

* `topic` (required)
* `pdf` (optional file upload)

---

## 📦 Sample Response

```json
{
  "image_data_url": "data:image/png;base64,...",
  "teaching_summary": "...",
  "research_report": "...",
  "pdf": {
    "filename": "example.pdf",
    "page_count": 5
  }
}
```

---

## 🔄 Example Request Flow

1. Frontend sends `FormData` → Backend
2. Backend validates topic
3. Loads API settings
4. Processes PDF (if uploaded)
5. Performs web search
6. Runs CrewAI agents
7. Generates image via Hugging Face
8. Returns JSON response
9. Frontend displays results

---

## ⚠️ Error Handling

The system handles:

* Missing topic
* Missing API keys
* Large PDF files (>12MB)
* PDF processing errors
* Web search failures
* CrewAI execution issues
* Image generation failures

Errors are returned as JSON and displayed in UI.

---

## ⚡ Limitations

* No persistent database (temporary processing only)
* Depends on external APIs (Groq, Hugging Face)
* PDF size limit (12 MB)
* Performance depends on network/API speed

---

## 🚀 Future Improvements

* Add database support (history & caching)
* User authentication
* Multiple file uploads
* Streaming responses
* Better UI/UX with frameworks
* Model selection UI
* Export reports as PDF

---

## 📄 License

This project is for educational purposes. You can modify and use it as needed.

---

⭐ *Agentic RAG Studio — Turning topics into visual learning experiences.*


---

## 👤 Author
**Ashish Rana**
