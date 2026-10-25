# GEMINI.md - Contexto do Projeto: juridico-rag-bot

## 1. Visão Geral do Projeto
O **juridico-rag-bot** é um assistente interno de suporte jurídico baseado em RAG (*Retrieval-Augmented Generation*) para o escritório fictício **Lex & Associados**.
Seu propósito é permitir que advogados associados, estagiários e gestores consultem com rapidez e segurança:
- **Prazos processuais** (regras do CPC, CLT, suspensões e contagem em dias úteis).
- **Normas e regras da OAB**.
- **Cláusulas contratuais** (prazos de entrega, multas, rescisões e obrigações de contratos de clientes).

---

## 2. Stack Tecnológica
- **Linguagem & Ambiente**: Python 3.12 (gerenciado via `uv`).
- **Orquestração RAG**: [LlamaIndex](https://www.llamaindex.ai/) (`llama-index-core`, `llama-index-vector-stores-chroma`, `llama-index-embeddings-gemini`, `llama-index-llms-gemini`).
- **Modelos de IA (Google Gemini)**:
  - **LLM**: `gemini-2.5-flash` (via API Gemini).
  - **Embedding**: `gemini-embedding-001` / `models/gemini-embedding-001`.
**Banco Vetorial**: PostgreSQL com extensão `pgvector` (tabela `juridico_nodes`), gerenciado via container Docker `juridico_postgres`.
- **Backend / API**: [FastAPI](https://fastapi.tiangolo.com/) com validação via Pydantic e servidor Uvicorn.
- **Frontend / Interface**: [Streamlit](https://streamlit.io/) com chat interativo e exibição de fontes citadas.
- **Containerização**: Docker e Docker Compose (`Dockerfile`, `Dockerfile.streamlit`, `docker-compose.yml`).
- **Testes**: `pytest` e `httpx` (em `tests/`).

---

## 3. Estrutura do Repositório

```plaintext
juridico-rag-bot/
├── .github/
│   └── workflows/ci.yml    # Pipeline de CI com GitHub Actions
├── .env.exemplo            # Exemplo de variáveis de ambiente necessárias
├── .env                    # Chaves de API locais (GOOGLE_API_KEY / GEMINI_API_KEY)
├── ARCHITECTURE.md         # Diagrama e desenho técnico da arquitetura
├── ROADMAP.md              # Próximos passos e backlog do projeto
├── pyproject.toml          # Dependências do projeto gerenciadas via uv
├── docker-compose.yml      # Orquestração dos containers (Postgres pgvector + API + Streamlit)
├── Dockerfile              # Imagem para execução da API FastAPI
├── Dockerfile.streamlit    # Imagem para execução do frontend Streamlit
├── data/                   # Documentos PDF de entrada (contratos e legislação)
├── prompts/
│   └── agent_prompt.md     # Persona, regras e diretrizes do agente jurídico
├── src/
│   ├── __init__.py
│   ├── ingest.py           # Pipeline ETL: leitura de PDFs, chunking e gravação no PostgreSQL (pgvector)
│   ├── bot.py              # Motor RAG: conexão com PostgreSQL (pgvector), modelo Gemini e Query Engine
│   ├── api.py              # API FastAPI: expõe endpoints GET / e POST /chat
│   └── app.py              # Interface Web em Streamlit consumindo a API
└── tests/                  # Testes automatizados da aplicação
```

---

## 4. Componentes e Fluxo de Dados

1. **Ingestão (`src/ingest.py`)**:
   - Lê recursivamente PDFs em `data/` usando `SimpleDirectoryReader`.
   - Gera embeddings com `GeminiEmbedding`.
   - Salva e indexa no PostgreSQL via `PGVectorStore` na tabela `juridico_nodes`.

2. **Motor RAG (`src/bot.py`)**:
   - Conecta ao PostgreSQL via `PGVectorStore` e recupera os nós mais similares (`similarity_top_k=3`).
   - Carrega a persona e diretrizes do assistente de `prompts/agent_prompt.md`.
   - Configura o LLM `gemini-2.5-flash` e gera a resposta fundamentada com citações dos documentos de origem.

3. **API (`src/api.py`)**:
   - `GET /`: Healthcheck e status do serviço.
   - `POST /chat`: Recebe `{"question": "..."}` e retorna `{"answer": "...", "sources": ["doc1.pdf", ...]}`.

4. **Interface (`src/app.py`)**:
   - Chat interativo em Streamlit com histórico de sessão e menu expansível para inspecionar os documentos fonte retornados pelo RAG.

---

## 5. Como Executar o Projeto

### Localmente (com `uv`):
```bash
# 1. Instalar dependências
uv sync

# 2. Configurar variáveis de ambiente
cp .env.exemplo .env # preencher GEMINI_API_KEY ou GOOGLE_API_KEY

# 3. Executar o pipeline de ingestão
uv run python src/ingest.py

# 4. Iniciar a API Backend
uv run uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

# 5. Em outro terminal, iniciar o frontend Streamlit
uv run streamlit run src/app.py
```

### Com Docker Compose:
```bash
docker compose up --build
```
- API disponível em: `http://localhost:8000`
- Streamlit disponível em: `http://localhost:8501`

---

## 6. Diretrizes e Regras para Desenvolvimento (AI Assistant Guidelines)

1. **Ambiente & Pacotes**:
   - Sempre utilize `uv run` ou respeite o gerenciador `uv`. Não use `pip install` global.
   - Ao adicionar novas bibliotecas, use `uv add <pacote>`.

2. **Rigor Jurídico e RAG**:
   - Nunca invente prazos, normas legais (CPC/CLT) ou cláusulas contratuais.
   - Respostas do RAG devem sempre indicar o documento ou embasamento legal recuperado.
   - Respeitar as diretrizes de tom e postura descritas em `prompts/agent_prompt.md` (respostas objetivas, profissionais e diretas).

3. **Segurança**:
   - Nunca comite chaves de API (`GEMINI_API_KEY` ou `GOOGLE_API_KEY`) no repositório. Mantenha-as exclusivamente no `.env`.
