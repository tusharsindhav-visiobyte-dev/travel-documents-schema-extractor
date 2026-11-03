"""Document type endpoint, exercised against a local stand-in for Ollama."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.config import Settings
from api.extract import extract_upload
from registry import get_supported_document_types, validate_document_type


def _pdf(text: str) -> bytes:
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 36 100 Td ({safe}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 400 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(out)


class _OllamaStub:
    def __init__(self, *, status: int = 200, document_type: str = "flight_ticket") -> None:
        self.status = status
        self.document_type = document_type
        self.requests: list[dict] = []
        handler = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length) or b"{}")
                handler.requests.append({"path": self.path, "body": body})
                if handler.status != 200:
                    payload = b'{"error":"unavailable"}'
                    self.send_response(handler.status)
                else:
                    properties = body.get("format", {}).get("properties", {})
                    key = next(iter(properties), "document_type")
                    value = handler.document_type if key == "document_type" else "flight"
                    content = json.dumps({key: value})
                    payload = json.dumps({"message": {"role": "assistant", "content": content}}).encode()
                    self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, format: str, *args: object) -> None:
                return

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self.thread.start()

    @property
    def base_url(self) -> str:
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    def close(self) -> None:
        self._server.shutdown()
        self.thread.join(timeout=3)
        self._server.server_close()


@pytest.fixture
def ollama():
    stub = _OllamaStub()
    try:
        yield stub
    finally:
        stub.close()


@pytest.fixture
def client(ollama: _OllamaStub):
    app = create_app(
        Settings(ollama_url=ollama.base_url, model="qwen:7b", timeout_seconds=5)
    )
    with TestClient(app) as test_client:
        yield test_client


def test_json_text_returns_a_registered_document_type(client: TestClient, ollama: _OllamaStub):
    response = client.post(
        "/document-type",
        json={"text": "E-TICKET\nPassenger name record HX4Q2P\nFlight EX101"},
    )

    assert response.status_code == 200
    document_type = response.json()["document_type"]
    assert document_type == "flight_ticket"
    assert validate_document_type(document_type)
    assert set(response.json()) == {"document_type"}

    assert len(ollama.requests) == 2
    category_call, type_call = ollama.requests
    assert category_call["path"] == "/api/chat"
    assert "flight_ticket" in category_call["body"]["messages"][0]["content"]
    assert "hotel_booking" in category_call["body"]["messages"][0]["content"]
    assert type_call["body"]["model"] == "qwen:7b"
    allowed = type_call["body"]["format"]["properties"]["document_type"]["enum"]
    assert "flight_ticket" in allowed
    assert "flight_departure" not in allowed
    assert "flight_ticket:" in type_call["body"]["messages"][0]["content"]
    assert "E-TICKET" in type_call["body"]["messages"][0]["content"]


def test_form_text_and_text_file_are_classified(client: TestClient):
    form = client.post("/document-type", data={"text": "Hotel voucher for a confirmed stay."})
    multipart = client.post(
        "/document-type",
        files={"text": (None, "Hotel voucher for a confirmed stay.")},
    )
    upload = client.post(
        "/document-type",
        files={"file": ("ticket.txt", b"Issued e-ticket coupon 1", "text/plain")},
    )

    assert form.status_code == 200
    assert form.json() == {"document_type": "flight_ticket"}
    assert multipart.status_code == 200
    assert multipart.json() == {"document_type": "flight_ticket"}
    assert upload.status_code == 200
    assert upload.json()["document_type"] == "flight_ticket"


def test_uploaded_pdf_text_is_sent_to_the_model(client: TestClient, ollama: _OllamaStub):
    response = client.post(
        "/document-type",
        files={"file": ("boarding.pdf", _pdf("Boarding pass gate A12"), "application/pdf")},
    )

    assert response.status_code == 200
    assert "Boarding pass gate A12" in ollama.requests[-1]["body"]["messages"][0]["content"]


def test_file_is_used_when_text_is_also_sent(client: TestClient, ollama: _OllamaStub):
    response = client.post(
        "/document-type",
        data={"text": "this pasted text should not be classified"},
        files={"file": ("ticket.txt", b"Ticket number 123", "text/plain")},
    )

    assert response.status_code == 200
    user_message = ollama.requests[-1]["body"]["messages"][0]["content"]
    assert "Ticket number 123" in user_message
    assert "should not be classified" not in user_message


def test_missing_input_is_rejected(client: TestClient):
    assert client.post("/document-type", json={"text": "   "}).status_code == 400
    assert client.post("/document-type", json={}).status_code == 400
    assert client.post("/document-type", data={}).status_code == 400
    assert client.post("/document-type", content=b"hello").status_code == 400


def test_unsupported_file_is_rejected(client: TestClient):
    response = client.post(
        "/document-type",
        files={"file": ("scan.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )
    assert response.status_code == 415


def test_unregistered_model_answer_is_rejected(ollama: _OllamaStub):
    ollama.document_type = "flight_departure"
    app = create_app(Settings(ollama_url=ollama.base_url, model="qwen:7b", timeout_seconds=5))
    with TestClient(app) as test_client:
        response = test_client.post("/document-type", json={"text": "A flight leaves tonight."})

    assert response.status_code == 422
    assert validate_document_type("flight_departure") is False


def test_model_http_error_is_a_bad_gateway(ollama: _OllamaStub):
    ollama.status = 503
    app = create_app(Settings(ollama_url=ollama.base_url, model="qwen:7b", timeout_seconds=5))
    with TestClient(app) as test_client:
        response = test_client.post("/document-type", json={"text": "Hotel invoice"})

    assert response.status_code == 502


def test_unreachable_model_is_a_bad_gateway():
    app = create_app(
        Settings(ollama_url="http://127.0.0.1:9", model="qwen:7b", timeout_seconds=1)
    )
    with TestClient(app) as test_client:
        response = test_client.post("/document-type", json={"text": "Passport of the bearer"})

    assert response.status_code == 502


def test_pdf_extraction_and_catalog_cover_the_registry():
    assert "Boarding pass" in extract_upload("pass.pdf", "application/pdf", _pdf("Boarding pass"), max_bytes=10000)
    from api.classifier import document_type_catalog

    catalog = document_type_catalog()
    for document_type in get_supported_document_types():
        assert f"- {document_type}:" in catalog


def test_openapi_documents_both_inputs(client: TestClient):
    spec = client.get("/openapi.json").json()
    operation = spec["paths"]["/document-type"]["post"]
    content = operation["requestBody"]["content"]
    assert "text" in content["application/json"]["schema"]["properties"]
    assert "file" in content["multipart/form-data"]["schema"]["properties"]
    response_schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    if "$ref" in response_schema:
        name = response_schema["$ref"].rsplit("/", 1)[-1]
        response_schema = spec["components"]["schemas"][name]
    assert "document_type" in response_schema["properties"]
