import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini

# Carrega variáveis do arquivo .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


PROMPT_PATH = Path("prompts/agent_prompt.md")


def load_system_prompt() -> str:
    """Carrega o prompt personalizado do agente salvo no desafio."""
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "Você é um assistente jurídico interno."


def get_query_engine():
    """
    Configura o motor de busca RAG unindo o PostgreSQL (pgvector),
    o modelo Gemini e as regras do Prompt do Agente.
    """

    # 1. Configurar Embedding e LLM do Gemini nas globais do LlamaIndex
    Settings.embed_model = GeminiEmbedding(
        model_name="gemini-embedding-001", api_key=api_key
    )
    Settings.llm = Gemini(model_name="gemini-2.5-flash", api_key=api_key)

    # 2. Conectar ao Vector Store do PostgreSQL de forma dinâmica e segura
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/juridico_db"
    )
    url = make_url(db_url)

    vector_store = PGVectorStore.from_params(
        database=url.database or "juridico_db",
        host=url.host or "localhost",
        password=url.password or "",
        port=url.port or 5432,
        user=url.username or "postgres",
        table_name="juridico_nodes",
        embed_dim=768,
    )

    # 3. Carregar o índice vetorial
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, embed_model=Settings.embed_model
    )

    # 4. Configurar o motor de consulta aplicando o prompt do sistema
    system_prompt = load_system_prompt()

    query_engine = index.as_query_engine(
        similarity_top_k=3, system_prompt=system_prompt
    )

    return query_engine


if __name__ == "__main__":
    try:
        engine = get_query_engine()
        pergunta = "Qual é o prazo aplicável para cumprimento das obrigações contratuais conforme as regras do escritório?"

        print(f"❓ Pergunta de teste: {pergunta}\n")
        response = engine.query(pergunta)

        print(f"🤖 Resposta do Agente:\n{response}")
    except Exception as e:
        print(f"Erro ao executar o bot: {e}")
