"""Regras de negócio do serviço PRODUTOS (sem Flask, sem rotas)."""

from erros import RegraDeNegocioError
from models import Produto, db


def criar(dados):
    """Cria um novo produto validando os campos obrigatórios."""
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise RegraDeNegocioError("O campo 'nome' é obrigatório.")
    categoria = (dados.get("categoria") or "").strip()
    try:
        preco = float(dados.get("preco", 0) or 0)
    except (TypeError, ValueError):
        raise RegraDeNegocioError("O campo 'preco' deve ser um número.")
    try:
        estoque = int(dados.get("estoque", 0) or 0)
    except (TypeError, ValueError):
        raise RegraDeNegocioError("O campo 'estoque' deve ser um número inteiro.")
    if preco <= 0:
        raise RegraDeNegocioError("O preço deve ser maior que zero.")
    if estoque < 0:
        raise RegraDeNegocioError("O estoque não pode ser negativo.")
    produto = Produto(nome=nome, categoria=categoria, preco=preco, estoque=estoque)
    db.session.add(produto)
    db.session.commit()
    return produto


def dados_iniciais():
    """Cria produtos de exemplo se o banco estiver vazio."""
    if Produto.query.count() == 0:
        db.session.add(Produto(nome="Ração Premium 10kg", categoria="Ração", preco=89.90, estoque=20))
        db.session.add(Produto(nome="Coleira M", categoria="Acessórios", preco=35.00, estoque=15))
        db.session.add(Produto(nome="Brinquedo Bolinha", categoria="Brinquedos", preco=12.50, estoque=30))
        db.session.commit()


def listar():
    """Retorna todos os produtos ordenados por id."""
    return Produto.query.order_by(Produto.id).all()


def buscar(produto_id):
    """Busca um produto pelo id."""
    return db.session.get(Produto, produto_id)


def atualizar(produto_id, dados):
    """Atualiza os campos de um produto existente."""
    produto = buscar(produto_id)
    if produto is None:
        return None
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise RegraDeNegocioError("O campo 'nome' é obrigatório.")
    produto.nome = nome
    produto.categoria = (dados.get("categoria") or "").strip()
    try:
        preco = float(dados.get("preco", produto.preco) or 0)
        estoque = int(dados.get("estoque", produto.estoque) or 0)
    except (TypeError, ValueError):
        raise RegraDeNegocioError("Preço e estoque devem ser números válidos.")
    if preco <= 0:
        raise RegraDeNegocioError("O preço deve ser maior que zero.")
    if estoque < 0:
        raise RegraDeNegocioError("O estoque não pode ser negativo.")
    produto.preco = preco
    produto.estoque = estoque
    db.session.commit()
    return produto


def inativar(produto_id):
    """Marca o produto como inativo."""
    produto = buscar(produto_id)
    if produto is None:
        return None
    if not produto.ativo:
        raise RegraDeNegocioError("O produto já está inativo.")
    produto.ativo = False
    db.session.commit()
    return produto


def baixar_estoque(produto_id, quantidade):
    """Reduz o estoque de um produto. Usado pelo serviço VENDAS."""
    if quantidade <= 0:
        raise RegraDeNegocioError("A quantidade deve ser maior que zero.")
    produto = buscar(produto_id)
    if produto is None:
        return None
    if not produto.ativo:
        raise RegraDeNegocioError("O produto está inativo, não é possível baixar estoque.")
    if produto.estoque < quantidade:
        raise RegraDeNegocioError(
            f"Estoque insuficiente: tem {produto.estoque} unid. e foram pedidas {quantidade}."
        )
    produto.estoque -= quantidade
    db.session.commit()
    return produto


def repor_estoque(produto_id, quantidade):
    """Soma ao estoque de um produto. Usado pelo serviço VENDAS (cancelar venda)."""
    if quantidade <= 0:
        raise RegraDeNegocioError("A quantidade deve ser maior que zero.")
    produto = buscar(produto_id)
    if produto is None:
        return None
    produto.estoque += quantidade
    db.session.commit()
    return produto
