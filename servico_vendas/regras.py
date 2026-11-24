"""Regras de negócio do serviço VENDAS (sem Flask, sem rotas).

Todas as consultas a outros serviços passam por integracao.chamar().
"""

from erros import RegraDeNegocioError
from models import Venda, db
import integracao


def _ativo_ok(destino, caminho, nome_servico):
    """Consulta GET /ativo de outro serviço. Retorna True se existir e estiver ativo."""
    resposta = integracao.chamar(destino, "GET", caminho)
    if resposta.status_code == 404:
        raise RegraDeNegocioError(f"{nome_servico} não encontrado.")
    dados = integracao.ler_json(resposta, destino)
    if not dados.get("ativo"):
        raise RegraDeNegocioError(f"{nome_servico} está inativo.")
    return True


def criar(dados):
    """Cria uma venda validando cliente, produto e vendedor nos outros serviços."""
    cliente_id = dados.get("cliente_id")
    produto_id = dados.get("produto_id")
    vendedor_id = dados.get("vendedor_id")
    quantidade = dados.get("quantidade")

    if cliente_id is None or produto_id is None or vendedor_id is None or quantidade is None:
        raise RegraDeNegocioError("campos obrigatórios: cliente_id, produto_id, vendedor_id, quantidade.")
    try:
        cliente_id = int(cliente_id)
        produto_id = int(produto_id)
        vendedor_id = int(vendedor_id)
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        raise RegraDeNegocioError("cliente_id, produto_id, vendedor_id e quantidade devem ser números inteiros.")
    if quantidade <= 0:
        raise RegraDeNegocioError("A quantidade deve ser maior que zero.")

    # Integração 2 (BUSCA): valida cliente, produto e vendedor antes de salvar.
    _ativo_ok("CLIENTES", f"/api/clientes/{cliente_id}/ativo", "Cliente")

    resposta_produto = integracao.chamar("PRODUTOS", "GET", f"/api/produtos/{produto_id}")
    if resposta_produto.status_code == 404:
        raise RegraDeNegocioError("Produto não encontrado.")
    produto = integracao.ler_json(resposta_produto, "PRODUTOS")
    if not produto.get("ativo"):
        raise RegraDeNegocioError("O produto está inativo.")
    if produto.get("estoque", 0) < quantidade:
        raise RegraDeNegocioError(
            f"Estoque insuficiente: tem {produto.get('estoque')} unid. e foram pedidas {quantidade}."
        )
    valor_unitario = float(produto.get("preco", 0))
    total = valor_unitario * quantidade

    _ativo_ok("VENDEDORES", f"/api/vendedores/{vendedor_id}/ativo", "Vendedor")

    # Salva a venda
    venda = Venda(cliente_id=cliente_id, produto_id=produto_id, vendedor_id=vendedor_id,
                  quantidade=quantidade, valor_unitario=valor_unitario, total=total,
                  status="concluida")
    db.session.add(venda)
    db.session.commit()
    venda_id = venda.id

    # Integração 3 (ALTERAÇÃO): baixa o estoque do produto após salvar a venda.
    try:
        resposta_baixa = integracao.chamar("PRODUTOS", "PATCH",
                                           f"/api/produtos/{produto_id}/baixar-estoque",
                                           json={"quantidade": quantidade})
        if resposta_baixa.status_code != 200:
            try:
                corpo = integracao.ler_json(resposta_baixa, "PRODUTOS")
                erro_json = corpo.get("erro", "")
            except RegraDeNegocioError:
                erro_json = ""
            raise RegraDeNegocioError(f"resposta {resposta_baixa.status_code} do serviço PRODUTOS: {erro_json}")
    except RegraDeNegocioError as falha:
        venda_para_apagar = db.session.get(Venda, venda_id)
        if venda_para_apagar is not None:
            db.session.delete(venda_para_apagar)
            db.session.commit()
        print(f"[VENDAS]   compensação: venda {venda_id} desfeita", flush=True)
        raise RegraDeNegocioError(
            f"A venda foi desfeita porque não foi possível baixar o estoque do produto: {falha}"
        )

    return venda


def dados_iniciais():
    """Não cria venda de exemplo: os outros serviços podem estar desligados ao iniciar."""
    pass


def listar():
    """Retorna todas as vendas ordenadas por id."""
    return Venda.query.order_by(Venda.id).all()


def buscar(venda_id):
    """Busca uma venda pelo id."""
    return db.session.get(Venda, venda_id)


def buscar_detalhes(venda_id):
    """Retorna a venda com os dados do cliente embutidos (Integração 1 - BUSCA).

    Se o serviço CLIENTES estiver fora do ar, a venda vem com 'cliente': null
    e um aviso claro (a consulta não falha por causa disso).
    """
    venda = buscar(venda_id)
    if venda is None:
        return None
    resultado = venda.para_dict()
    try:
        resposta = integracao.chamar("CLIENTES", "GET", f"/api/clientes/{venda.cliente_id}")
        if resposta.status_code == 200:
            cliente = integracao.ler_json(resposta, "CLIENTES")
            resultado["cliente"] = {
                "nome_tutor": cliente.get("nome_tutor"),
                "nome_pet": cliente.get("nome_pet"),
                "especie": cliente.get("especie"),
            }
        else:
            resultado["cliente"] = None
            resultado["aviso"] = "Não foi possível consultar os dados do cliente."
    except RegraDeNegocioError:
        resultado["cliente"] = None
        resultado["aviso"] = ("Serviço CLIENTES indisponível; venda consultada sem os dados do cliente.")
    return resultado


def atualizar_vendedor(venda_id, dados):
    """Permite trocar apenas o vendedor_id da venda."""
    venda = buscar(venda_id)
    if venda is None:
        return None
    vendedor_id = dados.get("vendedor_id")
    if vendedor_id is None:
        raise RegraDeNegocioError("O campo 'vendedor_id' é obrigatório.")
    try:
        vendedor_id = int(vendedor_id)
    except (TypeError, ValueError):
        raise RegraDeNegocioError("O campo 'vendedor_id' deve ser um número inteiro.")
    _ativo_ok("VENDEDORES", f"/api/vendedores/{vendedor_id}/ativo", "Vendedor")
    venda.vendedor_id = vendedor_id
    db.session.commit()
    return venda


def cancelar(venda_id):
    """Marca a venda como cancelada e repõe o estoque do produto.

    Se a reposição de estoque falhar, a venda não é cancelada.
    """
    venda = buscar(venda_id)
    if venda is None:
        return None
    if venda.status == "cancelada":
        raise RegraDeNegocioError("A venda já está cancelada.")
    venda.status = "cancelada"
    db.session.commit()

    try:
        resposta = integracao.chamar("PRODUTOS", "PATCH",
                                     f"/api/produtos/{venda.produto_id}/repor-estoque",
                                     json={"quantidade": venda.quantidade})
        if resposta.status_code != 200:
            try:
                corpo = integracao.ler_json(resposta, "PRODUTOS")
                erro_json = corpo.get("erro", "")
            except RegraDeNegocioError:
                erro_json = ""
            raise RegraDeNegocioError(f"resposta {resposta.status_code} do serviço PRODUTOS: {erro_json}")
    except Exception as falha:
        # Não cancelar: volta o status para concluída e avisa.
        venda.status = "concluida"
        db.session.commit()
        print(f"[VENDAS]   reposição de estoque falhou; venda {venda.id} mantida como concluída", flush=True)
        raise RegraDeNegocioError(
            f"Não foi possível cancelar: falha ao repôr estoque ({falha}). Venda mantida como concluída."
        )
    return venda
