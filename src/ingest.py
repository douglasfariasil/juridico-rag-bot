# Pipeline ETL para PDFs (contratos e OAB)

import os
from pathlib import Path
from dotenv import load_dotenv

import sqlalchemy
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini


# Carrega variáveis do arquivo .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


DATA_DIR = Path("data")


def run_ingestion():
    """
    Processa documentos PDF nas pastas de contratos e legislação,
    gerando embeddings via Gemini e salvando no PostgreSQL (pgvector).
    """
    # 1. Carregar documentos PDF
    if not DATA_DIR.exists() or not list(DATA_DIR.glob("**.pdf")):
        print(
            f"⚠️ Diretório {DATA_DIR} não encontrado. Crie as pastas 'data/contratos' e 'data/legislacao'."
        )
        return

    print("🚀 Iniciando pipeline de ingestão no PostgreSQL (`pgvector`)...")

    reader = SimpleDirectoryReader(
        input_dir=str(DATA_DIR), recursive=True, required_exts=[".pdf"]
    )
    documents = reader.load_data()
    print(f"📄 {len(documents)} páginas/documentos carregados.")

    # 3. Configurar modelo de Embedding do Gemini
    Settings.embed_model = GeminiEmbedding(
        model_name="models/gemini-embedding-001", api_key=api_key
    )
    Settings.llm = Gemini(model_name="gemini-2.5-flash")

    # Conexão com o PostgreSQL via DATABASE_URL
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/juridico_db"
    )
    url = sqlalchemy.engine.make_url(db_url)

    # Criar o vector store do Postgres com credenciais dinâmicas e seguras
    vector_store = PGVectorStore.from_params(
        database=url.database or "juridico_db",
        host=url.host or "localhost",
        password=url.password or "",
        port=url.port or 5432,
        user=url.username or "postgres",
        table_name="juridico_nodes",
        embed_dim=768,  # Dimensão padrão do modelo de embedding do Gemini
        perform_setup=True,
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 4. Criar e persistir o índice vetorial
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=Settings.embed_model
    )

    print(
        "✅ Ingestão concluída com sucesso! Dados salvos na tabela `juridico_nodes` do PostgreSQL."
    )


if __name__ == "__main__":
    run_ingestion()
