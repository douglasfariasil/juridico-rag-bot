FROM python:3.12-slim

# Instalar ferramentas essenciais
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Instalar o uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copiar todo o projeto primeiro (incluindo pyproject.toml, README.md e a pasta src)
COPY . .

# Instalar dependências usando o uv em modo editável
RUN uv pip install --system --no-cache -e .

# Expor a porta da API
EXPOSE 8000

# Comando para iniciar a API
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
