# artinpack-estoque-mvp
Sistema de Gestão de Estoque para a Artinpack (MVP em Python/Flask)

## Como executar
1. Instale o Python 3.12 ou superior.
2. Instale as dependências: `pip install -r requirements.txt`
3. Inicie o sistema: `python app.py`
4. Abra no navegador: http://127.0.0.1:5000

O banco de dados (`database.db`, SQLite) é criado automaticamente na primeira execução, com três produtos de exemplo.

## Testes
1. Instale as dependências de desenvolvimento: `pip install -r requirements-dev.txt`
2. Rode os testes unitários e de integração com cobertura: `python -m pytest -v --cov=app --cov-report=term-missing`

## Publicação e monitoramento
- Deploy no Render (plano grátis) pelo arquivo `render.yaml`: o serviço instala as dependências e sobe o app com `gunicorn app:app`, usando `/saude` como verificação de saúde.
- O workflow `.github/workflows/monitoramento.yml` consulta `APP_URL/saude` a cada 15 minutos e falha (status DOWN) se a resposta não for HTTP 200. A URL fica na variável `APP_URL` do repositório.
- No plano grátis o disco é temporário: o banco volta aos dados de exemplo quando o serviço reinicia. Use a versão publicada só para demonstração.

## Configuração (opcional)
- `SECRET_KEY`: chave usada para assinar a sessão. Sem ela, uma chave aleatória é gerada a cada execução.
- `FLASK_DEBUG=1`: ativa o modo de depuração. Use apenas em desenvolvimento.

## Funcionalidades
- Painel com total de produtos, alertas de estoque baixo, itens críticos e data da última movimentação.
- Registro de entradas e saídas com data e responsável, com atualização automática do saldo.
- Validações no servidor: saída maior que o saldo, quantidade inválida, campos vazios.

## Fora do escopo do MVP
Cadastro de produtos pela interface, login e perfis de acesso, relatórios, integrações e hospedagem na nuvem.

## Cópia de segurança
Copie periodicamente o arquivo `database.db` para outro local.
