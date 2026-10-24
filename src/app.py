import os
import streamlit as st
import requests

# Configuração da página
st.set_page_config(
    page_title="Lex & Associados - Assistente Jurídico",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ Lex & Associados — Assistente Jurídico")
st.markdown(
    "Consulte prazos processuais, regras da OAB e cláusulas contratuais de forma rápida e segura."
)

# URL do endpoint da nossa API FastAPI (usa variável de ambiente no Docker ou fallback local)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/chat")

# Inicializar o histórico do chat na sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir mensagens anteriores do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de input para a pergunta do usuário
if prompt := st.chat_input(
    "Ex: Qual é o prazo para contestação no CPC ou o que diz o contrato sobre multas?"
):
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Faz a requisição para a API FastAPI
    with st.chat_message("assistant"):
        with st.spinner("Consultando base de conhecimento e regras do escritório..."):
            try:
                response = requests.post(API_URL, json={"question": prompt})

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Sem resposta.")
                    sources = data.get("sources", [])

                    # Exibe a resposta do agente
                    st.markdown(answer)

                    # Exibe as fontes de referência (RAG) em um menu expansível
                    if sources:
                        with st.expander("📚 Fontes e Documentos Consultados"):
                            for source in sources:
                                st.caption(f"- {source}")

                    # Salva a resposta no histórico
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                else:
                    st.error(f"Erro na API ({response.status_code}): {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(
                    f"⚠️ Não foi possível conectar à API FastAPI. Verifique se o servidor está rodando em `{API_URL}`."
                )
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {str(e)}")
