import json
import pandas as pd
import requests
import streamlit as st

# ======== CONFIGURAÇÃO ========
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODELO = 'llama3.2:3b'

# ======== CARREGAR DADOS ========
perfil = json.load(open('./data/perfil_investidor.json', encoding='utf-8'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json', encoding='utf-8'))

# ======== PROCESSAR GASTOS COM PANDAS (EVITA ERRO DE CÁLCULO DA IA) ========
saidas = transacoes[transacoes['tipo'] == 'saida']
resumo_gastos = saidas.groupby('categoria')['valor'].sum().sort_values(ascending=False)
resumo_gastos_texto = "\n".join([f"- {cat.capitalize()}: R$ {val:.2f}" for cat, val in resumo_gastos.items()])
total_saidas = saidas['valor'].sum()

# ======== MONTAR CONTEXTO MASTIGADO ========
contexto = f"""
DADOS DO CLIENTE:
- Nome: {perfil['nome']}, {perfil['idade']} anos, Perfil: {perfil['perfil_investidor']}
- Objetivo Atual: {perfil['objetivo_principal']}
- Patrimônio Total: R$ {perfil['patrimonio_total']:.2f} | Reserva Atual: R$ {perfil['reserva_emergencia_atual']:.2f}

RESUMO EXATO DE GASTOS DO MÊS (TOTAL: R$ {total_saidas:.2f}):
{resumo_gastos_texto}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

# ======== SYSTEM PROMPT COM EXEMPLO (FEW-SHOT) ========
SYSTEM_PROMPT = """Você é o Léo, um educador financeiro amigável, acolhedor e didático.

DIRETRIZES DE RESPOSTA:
1. Responda DIRETAMENTE ao que o usuário perguntou.
2. Se a pergunta for sobre GASTOS: mostre os 2 maiores gastos (Moradia e Alimentação) e a proporção de quase 80%.
3. Se a pergunta for sobre INVESTIR / AÇÕES / RESERVA:
   - Avise que você NÃO faz recomendações de compra ou venda (você é apenas educador).
   - Explique o conceito: ações oscilam muito (risco alto) e não são indicadas para reserva de emergência.
   - Explique que reserva de emergência exige segurança e liquidez diária (como Tesouro Selic ou CDB).
4. Se for FORA DE FINANÇAS ou pedir senhas: recuse com educação.
5. Escreva de forma simples, em tom de conversa de amigo, em no máximo 2 parágrafos curtos.

EXEMPLOS DE COMPORTAMENTO:

Pergunta: Onde estou gastando mais este mês?
Resposta: Olá, João! Analisando suas contas deste mês, o seu maior gasto foi com Moradia (R$ 1.380,00), seguido por Alimentação (R$ 570,00). Juntas, essas duas despesas somam quase 80% do seu orçamento. É super normal essas contas pesarem mais, mas podemos olhar juntos onde economizar para acelerar sua reserva de emergência. O que acha?

Pergunta: Vale a pena colocar minha reserva de emergência em ações?
Resposta: Olá, João! Como educador financeiro, eu não recomendo investimentos específicos, mas posso te explicar como funciona. Ações têm oscilação diária e risco mais alto, então não são indicadas para reserva de emergência, onde você precisa de dinheiro seguro e fácil de resgatar a qualquer momento. Para a sua reserva, o ideal são aplicações de baixo risco e liquidez diária, como Tesouro Selic ou CDB 100% do CDI. Quer que eu te explique a diferença entre eles?

Pergunta: Qual a previsão do tempo para amanhã?
Resposta: Olá! Sou especializado exclusivamente em finanças e não tenho informações sobre o tempo. Como posso te ajudar com seu planejamento ou dúvidas financeiras hoje?
"""


def perguntar(msg):
    prompt = f"""{SYSTEM_PROMPT}

DADOS ATUAIS DO CLIENTE:
{contexto}

Pergunta do cliente: {msg}
Resposta do Léo:"""

    payload = {
        'model': MODELO,
        'prompt': prompt,
        'stream': False,
        'options': {'temperature': 0.3},
    }
    r = requests.post(OLLAMA_URL, json=payload)
    resposta = r.json()['response']

    return resposta.replace('$', r'\$').replace('`', '')

# ======== INTERFACE STREAMLIT ========
st.title("Léo, seu educador financeiro")

if pergunta := st.chat_input("Sua dúvida sobre finanças..."):
    st.chat_message("user").write(pergunta)
    with st.spinner("Léo está pensando..."):
        st.chat_message("assistant").write(perguntar(pergunta))
