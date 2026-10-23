from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api import app

client = TestClient(app)


def test_read_root():
    """Valida se o endpoint raiz da API está online e respondendo corretamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "online",
        "service": "Lex & Associados Bot API",
    }


@patch("src.api.get_engine")
def test_chat_endpoint_mocked(mock_get_engine):
    """Valida o endpoint /chat utilizando um mock do motor RAG para isolar o teste."""

    # Mock do comportamento do query_engine do LlamaIndex
    class MockResponse:
        def __init__(self):
            self.source_nodes = []

        def __str__(self):
            return "Prazo processual calculado com base no CPC: 15 dias úteis."

    mock_engine = mock_get_engine.return_value
    mock_engine.query.return_value = MockResponse()

    response = client.post("/chat", json={"question": "Qual o prazo de contestação?"})

    assert response.status_code == 200
    data = response.json()
    assert "Prazo processual" in data["answer"]
    assert "sources" in data
