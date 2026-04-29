from __future__ import annotations

from base64 import b64encode
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
STATIC_DIR = ROOT_DIR / "static"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agentic_genai.config import load_settings
from agentic_genai.crew import run_topic_crew
from agentic_genai.image_service import generate_topic_image
from agentic_genai.rag import build_pdf_context


class AppHandler(BaseHTTPRequestHandler):
    server_version = "AgenticGenAI/1.0"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return

        if path.startswith("/static/"):
            file_path = STATIC_DIR / path.removeprefix("/static/")
            content_type = _content_type(file_path)
            self._send_file(file_path, content_type)
            return

        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/generate":
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return

        try:
            fields = self._read_multipart_form()
            topic = fields.get("topic", "").strip()
            if not topic:
                raise ValueError("Please enter a topic.")

            settings = load_settings()
            pdf_context_summary = None
            pdf_file = fields.get("pdf")
            pdf_context = "No PDF was uploaded. Use web findings as the source material."

            if isinstance(pdf_file, UploadedFile):
                pdf_data = build_pdf_context(pdf_file.content, pdf_file.filename, topic)
                pdf_context = (
                    f"Uploaded file: {pdf_data.filename}\n"
                    f"Pages: {pdf_data.page_count}\n\n"
                    f"{pdf_data.selected_context}"
                )
                pdf_context_summary = {
                    "filename": pdf_data.filename,
                    "page_count": pdf_data.page_count,
                }

            crew_result = run_topic_crew(
                topic=topic,
                settings=settings,
                pdf_context=pdf_context,
            )
            topic_image = generate_topic_image(topic=topic, settings=settings)

            self._send_json(
                {
                    "image_data_url": _image_data_url(topic_image),
                    "teaching_summary": crew_result.teaching_summary,
                    "research_report": crew_result.research_report,
                    "pdf": pdf_context_summary,
                }
            )
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def _read_multipart_form(self) -> dict[str, str | "UploadedFile"]:
        content_type = self.headers.get("Content-Type", "")
        boundary_match = re.search(r"boundary=(.+)", content_type)
        if not boundary_match:
            raise ValueError("Invalid form upload.")

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        boundary = boundary_match.group(1).strip('"').encode("utf-8")

        fields: dict[str, str | UploadedFile] = {}
        for part in body.split(b"--" + boundary):
            part = part.strip()
            if not part or part == b"--":
                continue

            header_bytes, separator, content = part.partition(b"\r\n\r\n")
            if not separator:
                continue

            headers = header_bytes.decode("utf-8", errors="ignore")
            disposition = _header_value(headers, "Content-Disposition")
            name = _disposition_value(disposition, "name")
            filename = _disposition_value(disposition, "filename")
            content = content.removesuffix(b"\r\n")
            content = content.removesuffix(b"--")

            if not name:
                continue

            if filename:
                if content:
                    fields[name] = UploadedFile(filename=filename, content=content)
            else:
                fields[name] = content.decode("utf-8", errors="replace")
        return fields

    def _send_file(self, file_path: Path, content_type: str) -> None:
        if not file_path.exists() or not file_path.is_file():
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return

        body = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class UploadedFile:
    def __init__(self, filename: str, content: bytes) -> None:
        self.filename = filename
        self.content = content


def _image_data_url(image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _content_type(file_path: Path) -> str:
    if file_path.suffix == ".css":
        return "text/css; charset=utf-8"
    if file_path.suffix == ".js":
        return "text/javascript; charset=utf-8"
    if file_path.suffix == ".html":
        return "text/html; charset=utf-8"
    return "application/octet-stream"


def _header_value(headers: str, header_name: str) -> str:
    for line in headers.splitlines():
        name, separator, value = line.partition(":")
        if separator and name.strip().lower() == header_name.lower():
            return value.strip()
    return ""


def _disposition_value(disposition: str, key: str) -> str:
    match = re.search(rf'{key}="([^"]*)"', disposition)
    return match.group(1) if match else ""


def main() -> None:
    host = "0.0.0.0"
    port = 8000
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Open http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
