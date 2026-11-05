# Almoxarifado da Manutenção

Aplicação web em Flask para controlar peças, níveis mínimos de estoque e ordens de serviço de manutenção.

## Funcionalidades

- Cadastro e busca de peças por nome.
- Registro de baixa com validação para impedir estoque negativo.
- Consulta de itens no estoque mínimo ou abaixo dele.
- Relatório com quantidade de peças cadastradas e valor total do estoque.
- Abertura e listagem de ordens de serviço.
- Resumo de ordem com IA, quando `OPENAI_API_KEY` estiver configurada.

## Requisitos

- Python 3.10 ou superior.
- Uma chave da OpenAI somente para usar o resumo com IA.

## Instalação

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell, ative-o com:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

Crie seu arquivo local de configuração a partir do modelo:

```bash
cp .env.example .env
```

Gere uma chave de sessão Flask:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Cole o resultado no campo `FLASK_SECRET_KEY` de `.env`. Para habilitar os resumos com IA, preencha `OPENAI_API_KEY` com sua chave. Essa variável é opcional para as demais funcionalidades.

O arquivo `.env` contém segredos e é ignorado pelo Git. Não publique nem compartilhe seu conteúdo.

## Banco de dados

Inicialize o banco e os dados de exemplo:

```bash
python criar_banco.py
```

O banco SQLite padrão (`almoxarifado.db`) é criado ao lado dos scripts, independentemente do diretório de onde o comando for executado. O inicializador cria tabelas ausentes e insere dados de exemplo apenas em tabelas vazias; não apaga registros existentes. Para usar outro arquivo de banco, informe seu caminho:

```bash
python criar_banco.py caminho/para/outro.db
```

## Executar

Com o ambiente virtual ativado:

```bash
python app.py
```

Abra o endereço local mostrado pelo Flask, normalmente `http://127.0.0.1:5000`.

## Imagens

As capturas de tela da aplicação ainda não estão disponíveis neste repositório.