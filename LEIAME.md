# Almoxarifado da Manutenção

Sistema de controle de peças e ordens de serviço.

```bash
pip install -r requirements.txt
python criar_banco.py
python app.py
```

Abra o endereço que o Flask mostrar (no Codespaces, a porta 5000).

O banco padrão fica ao lado dos scripts. A inicialização cria as tabelas e insere dados de exemplo somente quando as tabelas estão vazias; ela preserva os registros existentes.

Preencha o arquivo `.env` com `FLASK_SECRET_KEY` e `OPENAI_API_KEY`. Gere um segredo Flask aleatório (por exemplo, com `python -c "import secrets; print(secrets.token_hex(32))"`). A chave da OpenAI é opcional para as demais funções. O `.env` é local e não deve ser enviado ao Git.
