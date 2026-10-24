# Pipeline ETL para PDFs (contratos e OAB)

import os
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
import chromadb

# Carrega variáveis do arquivo .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


DATA_DIR = Path("data")
DB_DIR = Path("chroma_db")


def run_ingestion():
    """
    Processa documentos PDF nas pastas de contratos e legislação,
    gerando embeddings via Gemini e salvando no ChromaDB local.
    """
    print("🚀 Iniciando pipeline de ingestão...")

    # 1. Carregar documentos PDF
    if not DATA_DIR.exists():
        print(
            f"⚠️ Diretório {DATA_DIR} não encontrado. Crie as pastas 'data/contratos' e 'data/legislacao'."
        )
        return

    reader = SimpleDirectoryReader(
        input_dir=str(DATA_DIR), recursive=True, required_exts=[".pdf"]
    )
    documents = reader.load_data()
    print(f"📄 {len(documents)} páginas/documentos carregados.")

    # 2. Configurar o banco vetorial ChromaDB
    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))

    # # Se quiser recriar do zero sempre:
    # try:
    #     chroma_client.delete_collection("juridico_collection")
    # except Exception:
    #     pass

    chroma_collection = chroma_client.get_or_create_collection("juridico_collection")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 3. Configurar modelo de Embedding do Gemini
    embed_model = GeminiEmbedding(
        model_name="models/gemini-embedding-001", api_key=api_key
    )

    # 4. Criar e persistir o índice vetorial
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=embed_model
    )

    print("✅ Ingestão concluída com sucesso! Vetores salvos em 'chroma_db/'.")


if __name__ == "__main__":
    run_ingestion()
