import json
import pandas as pd
import requests
import streamlit as st

# ======== CONFIGURAÇÃO ========
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODELO = 'gpt-oss'


# ======== CARREGAR DADOS ========
perfil = json.load(open('./data/perfil_investidor.json'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json'))

# ======== MONTAR CONTEXTO ========
contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos, perfil {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}
PATRIMONIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

# ======== SYSTEM PROMPT ========
SYSTEM_PROMPT = """Você é o Léo, um educador financeiro amigável e didático.

OBJETIVO:
Ensinar conceitos de finanças pessoais de forma simples, usando os dados do cliente como exemplos práticos.

REGRAS:
1. NUNCA recomende investimentos específicos - apenas explique como funcionam
2. Use dados fornecidos para dar exemplos personalizados
3. Linguagem simples, como se explicasse para um amigo
4. Se não souber algo, admita: "Não tenho essa informação, mas posso explicar..."
5. Sempre pergunte se o cliente entendeu
6. Responda de forma sucinta e direta, no máximo 3 parágrafos
7. NÃO RESPONDA coisas que não são da especialidade de FINANÇAS. Sempre lembre que você é um educador financeiro.
"""


# ======== CHAMAR OLLAMA ========
def perguntar(msg):
    prompt = f"""
    {SYSTEM_PROMPT}

    CONTEXTO DO CLIENTE:
    {contexto}

    Pergunta: {msg}"""

    payload = {"model": MODELO, "prompt": prompt, "stream": False}

    r = requests.post(OLLAMA_URL, json=payload)
    return r.json()['response']


# ======== INTERFACE ========
st.title("Léo, seu educador financeiro")

if pergunta := st.chat_input("Sua dúvida sobre finanças..."):
    st.chat_message("user").write(pergunta)
    with st.spinner("..."):
        st.chat_message("assistant").write(perguntar(pergunta))
