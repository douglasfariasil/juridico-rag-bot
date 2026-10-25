# ⚖️ Lex & Associados — Assistente Jurídico Inteligente com RAG

Assistente de Inteligência Artificial corporativa projetada para o ecossistema jurídico interno. O sistema processa contratos, prazos processuais, regulamentos da OAB e base documental proprietária utilizando uma arquitetura **RAG (Retrieval-Augmented Generation)** com o **Google Gemini** e banco vetorial **PostgreSQL (`pgvector`)**.

---

## 🚀 Arquitetura & Tecnologias

O projeto adota padrões modernos de engenharia de software, backend e infraestrutura de IA:

* **Linguagem & Ambiente:** Python 3.12 (gerenciado via [uv](https://github.com/astral-sh/uv))
* **Orquestração RAG:** [LlamaIndex](https://www.llamaindex.ai/)
* **Modelos de IA (Google Gemini):**
  * **LLM:** `gemini-2.5-flash` (geração de respostas fundamentadas)
  * **Embeddings:** `gemini-embedding-001` (vetorização semântica)
* **Banco de Dados Vetorial:** PostgreSQL 16 com extensão **`pgvector`**
* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) com Uvicorn e validação via Pydantic
* **Frontend:** [Streamlit](https://streamlit.io/) (Interface de chat com visualização de fontes citadas)
* **Containerização:** Docker & Docker Compose
* **CI/CD:** GitHub Actions (automação de testes com `pytest` e `httpx`)

---

## 📂 Estrutura do Projeto

```text
juridico-rag-bot/
├── .github/
│   └── workflows/
│       └── ci.yml          # Pipeline de Integração Contínua (GitHub Actions)
├── data/                   # Pasta para armazenamento dos PDFs (contratos e leis)
├── prompts/
│   └── agent_prompt.md     # Persona e diretrizes do agente jurídico
├── src/
│   ├── __init__.py
│   ├── api.py              # Endpoints REST da API FastAPI
│   ├── app.py              # Interface gráfica Streamlit
│   ├── bot.py              # Motor RAG com PGVectorStore e Gemini
│   └── ingest.py           # Pipeline ETL: leitura de PDFs, chunking e indexação no pgvector
├── Dockerfile              # Container da API FastAPI
├── Dockerfile.streamlit    # Container da interface Streamlit
├── docker-compose.yml      # Orquestração de serviços (Postgres pgvector + API + Streamlit)
├── pyproject.toml          # Gerenciamento de dependências via uv
└── README.md
```

---

## ⚙️ Pré-requisitos

* **Docker** e **Docker Compose** instalados na máquina.
* **Chave de API do Google Gemini** (obtida no [Google AI Studio](https://aistudio.google.com/)).
* *(Opcional)* [uv](https://docs.astral.sh/uv/) instalado caso queira rodar localmente sem Docker.

---

## 🕹️ Como Executar

### Opção 1: Via Docker Compose (Recomendado)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/douglasfariasil/juridico-rag-bot.git
   cd juridico-rag-bot
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.exemplo .env
   ```
   Edite o `.env` e insira sua `GEMINI_API_KEY` (e altere as senhas do PostgreSQL se desejar).

3. **Adicione os documentos PDF:**
   Coloque os arquivos PDF (contratos, resoluções, normas) dentro da pasta `data/`.

4. **Inicie os containers:**
   ```bash
   docker compose up --build
   ```

5. **Acesse as aplicações:**
   * 💬 **Interface do Chat (Streamlit):** [http://localhost:8501](http://localhost:8501)
   * 📖 **Documentação Interativa da API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
   * 🩺 **Healthcheck da API:** [http://localhost:8000/](http://localhost:8000/)

---

### Opção 2: Localmente (com `uv`)

```bash
# 1. Instalar dependências
uv sync

# 2. Configurar variáveis de ambiente
cp .env.exemplo .env

# 3. Executar o pipeline de ingestão
uv run python src/ingest.py

# 4. Iniciar a API Backend
uv run uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

# 5. Em outro terminal, iniciar o frontend Streamlit
uv run streamlit run src/app.py
```

---

## 🧪 Pipeline de Testes e CI/CD

O projeto possui validação automatizada de testes com `pytest` e `httpx`, executada a cada push ou pull request via GitHub Actions.

Para rodar os testes localmente:
```bash
uv run pytest -v
```

---

## 🎯 Roadmap

- [x] Ingestão de PDFs e chunking com LlamaIndex
- [x] Armazenamento vetorial com PostgreSQL + `pgvector`
- [x] API REST assíncrona FastAPI e interface Web Streamlit
- [x] Pipeline de CI/CD automatizado via GitHub Actions
- [ ] Implementar busca híbrida (BM25 + vetorial com Reranking Cross-Encoder)
- [ ] Adicionar suporte a histórico de conversação multi-turn com memória persistente
- [ ] Implementar autenticação e autorização via JWT na API

---

## 📄 Licença

Projeto distribuído sob a licença **MIT**.

---

## 👥 Autor

Desenvolvido por **Douglas Faria da Silva**  
📧 Contato: [douglasfariasil@outlook.com](mailto:douglasfariasil@outlook.com)
