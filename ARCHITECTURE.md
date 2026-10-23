# Desenho técnico da solução

# Arquitetura do Sistema - Bot de Prazos e Contratos (RAG)

## Visão Geral
Sistema de Assistência Jurídica baseado em RAG (Retrieval-Augmented Generation) projetado para otimizar a consulta de prazos processuais, regras da OAB e análise de contratos internos.

## Componentes Técnicos
1. **Ingestão & ETL (`src/ingest.py`):** Processamento de PDFs de contratos e leis usando Python, chunking de texto e geração de embeddings via Gemini API.
2. **Armazenamento Vetorial:** ChromaDB (ambiente local) / pgvector (produção).
3. **Orquestração RAG (`src/bot.py`):** LlamaIndex para recuperação de contexto e união com o Prompt do Agente.
4. **API Backend (`src/api.py`):** FastAPI para expor endpoints REST assíncronos.
