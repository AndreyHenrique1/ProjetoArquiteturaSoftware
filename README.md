# Pet Shop - Microsserviços com Flask, Flask-SQLAlchemy e SQLite

## Propósito do sistema

Sistema de pet shop dividido em 4 microsserviços independentes que se comunicam somente por HTTP: cadastro de produtos, cadastro de clientes (tutores e pets), cadastro de vendedores e registro de vendas com baixa automática de estoque. Cada serviço tem o seu próprio banco de dados SQLite e nunca acessa o banco de outro serviço.

## Usuários

- Atendente / vendedor: cria e consulta vendas, altera o vendedor responsável e cancela vendas.
- Gerente da loja: cadastra e gerencia produtos, clientes e vendedores (cria, lista, busca, atualiza e inativa).

## Requisitos funcionais

1. O sistema deve permitir cadastrar, listar, buscar, atualizar e inativar produtos (nome, categoria, preço, estoque, ativo).
2. O sistema deve permitir baixar o estoque de um produto (somente se estiver ativo, com quantidade válida e estoque suficiente) e repor o estoque de um produto.
3. O sistema deve permitir cadastrar, listar, buscar, atualizar e inativar clientes (nome do tutor, nome do pet, espécie, telefone, ativo).
4. O sistema deve permitir cadastrar, listar, buscar, atualizar e inativar vendedores (nome, turno: manhã/tarde/noite, ativo).
5. O sistema deve permitir registrar uma venda informando cliente, produto, vendedor e quantidade; o serviço de vendas valida se cliente, produto e vendedor existem e estão ativos, se o produto tem estoque suficiente, calcula o total (preço × quantidade) e baixa o estoque do produto.
6. O sistema deve permitir consultar uma venda e ver os dados do cliente embutidos (nome do tutor, nome do pet e espécie).
7. O sistema deve permitir alterar apenas o vendedor de uma venda existente.
8. O sistema deve permitir cancelar uma venda, repondo o estoque do produto; se a reposição falhar, a venda não é cancelada.
9. Se a baixa de estoque falhar depois de a venda ser salva (serviço fora do ar, timeout ou erro), a venda é desfeita (compensação) e um erro claro é devolvido. Se o serviço de produtos já estiver fora do ar na validação, a venda nem é salva e o erro claro é devolvido.
10. Cada serviço deve criar dados de exemplo automaticamente quando o seu banco estiver vazio.

## Descritivo técnico

| Microsserviço | Porta | Banco | Função |
|---|---|---|---|
| servico_produtos | 5001 | produtos.db | Cadastro de produtos e controle de estoque |
| servico_clientes | 5002 | clientes.db | Cadastro de clientes (tutores e pets) |
| servico_vendedores | 5003 | vendedores.db | Cadastro de vendedores e turnos |
| servico_vendas | 5004 | vendas.db | Registro de vendas e integrações com os outros 3 serviços |

## Integrações

| # | Tipo | Quem chama | Quem responde | Rota usada | O que faz |
|---|---|---|---|---|---|
| 1 | Busca (GET) | servico_vendas | servico_clientes | GET /api/clientes/<id> | Embute os dados do cliente (nome_tutor, nome_pet, especie) na consulta de uma venda. Se o clientes estiver fora do ar, devolve a venda com "cliente": null e aviso claro. |
| 2 | Busca (GET) | servico_vendas | servico_produtos, servico_clientes, servico_vendedores | GET /api/produtos/<id>, GET /api/clientes/<id>/ativo, GET /api/vendedores/<id>/ativo | Antes de salvar a venda, valida que produto, cliente e vendedor existem e estão ativos, que o estoque é suficiente, pega o preço do produto e calcula o total. |
| 3 | Alteração (PATCH) | servico_vendas | servico_produtos | PATCH /api/produtos/<id>/baixar-estoque | Depois de salvar a venda, baixa o estoque. Se falhar (fora do ar, timeout ou resposta diferente de 200), apaga a venda (compensação) e devolve erro claro. |
| Extra | Alteração (PATCH) | servico_vendas | servico_produtos | PATCH /api/produtos/<id>/repor-estoque | Ao cancelar uma venda, repõe o estoque. Se falhar, a venda não é cancelada. |
42: 
43: As chamadas GET possuem retry (2 tentativas) em caso de falha de conexão ou timeout. URLs mal configuradas (sem https://, com barra final etc.) e respostas que não sejam JSON são tratadas com mensagem de erro clara.

## Como executar

1. Abra o PowerShell na pasta do projeto:
   ```powershell
   cd ProjetoArquiteturaSoftware
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```

3. No VS Code: selecione o interpretador da `.venv` (Ctrl+Shift+P > Python: Select Interpreter), abra Executar e Depurar e escolha **Iniciar os 4 serviços**.
   Se o Windows perguntar sobre o Firewall, clique em Permitir.

4. Alternativa sem VS Code: de dois cliques em `iniciar_servicos.bat`.

5. Importe `thunder-client-colecao.json` no Thunder Client e execute as requisições das pastas de cada serviço e da pasta Integrações.

6. Cada serviço expõe `GET /api/health` para conferir se está no ar.

## Interruptor de teste de falha (servico_produtos)

Definindo a variável de ambiente `SIMULAR_FALHA_BAIXA=1` antes de iniciar o serviço de produtos, o endpoint
`PATCH /api/produtos/<id>/baixar-estoque` devolve `500` com `{"erro": "falha simulada"}` sem mexer no estoque.
Isso serve para testar a compensação do serviço de vendas (a venda é desfeita).

Exemplo (PowerShell):
```powershell
$env:SIMULAR_FALHA_BAIXA="1"
python servico_produtos/app.py
```

## Publicação no Render

| Serviço | URL |
|---|---|
| servico_produtos | https://petshop-produtos.onrender.com |
| servico_clientes | https://petshop-clientes.onrender.com |
| servico_vendedores | https://servico-vendedores.onrender.com |
| servico_vendas | https://servico-vendas.onrender.com |

Teste de saúde de cada serviço: `GET <URL>/api/health`.

No `servico_vendas` as variáveis de ambiente são `PRODUTOS_URL`, `CLIENTES_URL` e `VENDEDORES_URL` (com `https://`, sem barra no final). Os outros três não precisam de variáveis de ambiente.

Avisos do plano gratuito: o serviço hiberna após ~15 min de inatividade e leva cerca de 1 minuto para acordar (chame `/api/health` antes de usar); o banco SQLite é apagado ao reiniciar/hibernar (dados de exemplo são recriados, vendas somem).

## Repositório

https://github.com/AndreyHenrique1/ProjetoArquiteturaSoftware

## Autor

Andrey Henrique João
