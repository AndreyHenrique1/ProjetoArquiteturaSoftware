"""Rotas do serviço PRODUTOS. Só recebe a requisição e chama as regras."""

from flask import Blueprint, jsonify, request

import regras
from erros import RegraDeNegocioError

rotas = Blueprint("produtos", __name__, url_prefix="/api")


def _nao_encontrado():
    return jsonify(erro="Produto não encontrado."), 404


@rotas.post("/produtos")
def criar():
    produto = regras.criar(request.get_json(silent=True) or {})
    return jsonify(produto.para_dict()), 201


@rotas.get("/produtos")
def listar():
    return jsonify([p.para_dict() for p in regras.listar()])


@rotas.get("/produtos/<int:produto_id>")
def buscar(produto_id):
    produto = regras.buscar(produto_id)
    return jsonify(produto.para_dict()) if produto else _nao_encontrado()


@rotas.put("/produtos/<int:produto_id>")
def atualizar(produto_id):
    produto = regras.atualizar(produto_id, request.get_json(silent=True) or {})
    return jsonify(produto.para_dict()) if produto else _nao_encontrado()


@rotas.patch("/produtos/<int:produto_id>/inativar")
def inativar(produto_id):
    produto = regras.inativar(produto_id)
    return jsonify(produto.para_dict()) if produto else _nao_encontrado()


@rotas.get("/produtos/<int:produto_id>/ativo")
def esta_ativo(produto_id):
    produto = regras.buscar(produto_id)
    if produto is None:
        return _nao_encontrado()
    return jsonify(id=produto.id, ativo=produto.ativo)


@rotas.patch("/produtos/<int:produto_id>/baixar-estoque")
def baixar_estoque(produto_id):
    """Baixa o estoque. Se SIMULAR_FALHA_BAIXA=1, devolve 500 sem mexer no estoque."""
    import os

    if os.environ.get("SIMULAR_FALHA_BAIXA") == "1":
        return jsonify(erro="falha simulada"), 500
    dados = request.get_json(silent=True) or {}
    quantidade = dados.get("quantidade")
    if quantidade is None:
        raise RegraDeNegocioError("O campo 'quantidade' é obrigatório.")
    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        raise RegraDeNegocioError("O campo 'quantidade' deve ser um número inteiro.")
    produto = regras.baixar_estoque(produto_id, quantidade)
    return jsonify(produto.para_dict()) if produto else _nao_encontrado()


@rotas.patch("/produtos/<int:produto_id>/repor-estoque")
def repor_estoque(produto_id):
    """Repõe o estoque de um produto."""
    dados = request.get_json(silent=True) or {}
    quantidade = dados.get("quantidade")
    if quantidade is None:
        raise RegraDeNegocioError("O campo 'quantidade' é obrigatório.")
    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        raise RegraDeNegocioError("O campo 'quantidade' deve ser um número inteiro.")
    produto = regras.repor_estoque(produto_id, quantidade)
    return jsonify(produto.para_dict()) if produto else _nao_encontrado()
