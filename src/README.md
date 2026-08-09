# Passo a Passo de Execução


## Setup do Ollama (5 minutos)

``` bash
# 1. Instalar Ollama (Ollama.com)
# 2. Baixar um modelo leve
ollama pull llama3.2:3b

# 3. Testar se funciona
ollama run llama3.2:3b "Olá!"
```

## Código Completo

Todo o código fonte está no arquivo `app.py`.

## Como Rodar

```bash
# Instalar dependências
pip install streamlit pandas requests

# Garantir que o Ollama está rodando
ollama serve

# Rodar o app
streamlit run .\src\app.py
```

## Evidencias de Execução

<img width="1304" height="655" alt="image" src="https://github.com/user-attachments/assets/16935a3f-f6a5-4b6c-8469-62479c974d33" />

