import os
from pathlib import Path
from dotenv import load_dotenv

import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini

# Carrega variáveis do arquivo .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

DB_DIR = Path("chroma_db")
PROMPT_PATH = Path("prompts/agent_prompt.md")


def load_system_prompt() -> str:
    """Carrega o prompt personalizado do agente salvo no desafio."""
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "Você é um assistente jurídico interno."


def get_query_engine():
    """
    Configura o motor de busca RAG unindo o ChromaDB,
    o modelo Gemini e as regras do Prompt do Agente.
    """
    if not DB_DIR.exists():
        raise FileNotFoundError(
            "⚠️ Base vetorial não encontrada. Execute 'src/ingest.py' primeiro."
        )

    # 1. Conectar ao ChromaDB existente
    db = chromadb.PersistentClient(path=str(DB_DIR))
    chroma_collection = db.get_or_create_collection("juridico_collection")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # 2. Configurar Embedding e LLM do Gemini nas globais do LlamaIndex
    Settings.embed_model = GeminiEmbedding(
        model_name="gemini-embedding-001", api_key=api_key
    )
    Settings.llm = Gemini(model_name="gemini-2.5-flash", api_key=api_key)

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
