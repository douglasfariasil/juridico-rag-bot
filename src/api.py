# Endpoints FastAPI

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.bot import get_query_engine

app = FastAPI(
    title="Lex & Associados - Bot Jurídico API",
    description="API para assistente interno de prazos processuais e contratos com RAG e Gemini.",
    version="0.1.0",
)

# Inicializa o motor de RAG de forma lazy ou na carga
query_engine = None


def get_engine():
    global query_engine
    if query_engine is None:
        query_engine = get_query_engine()
    return query_engine


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str] = []


@app.get("/")
def read_root():
    return {"status": "online", "service": "Lex & Associados Bot API"}


@app.post("/chat", response_model=QueryResponse)
def chat_with_bot(request: QueryRequest):
    try:
        engine = get_engine()
        response = engine.query(request.question)

        # Extrai os nomes dos arquivos fonte utilizados na resposta (RAG)
        sources = []
        if hasattr(response, "source_nodes") and response.source_nodes:
            for node in response.source_nodes:
                file_name = node.metadata.get("file_name", "Documento interno")
                sources.append(file_name)

        return QueryResponse(answer=str(response), sources=list(set(sources)))
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar consulta: {str(e)}"
        )
