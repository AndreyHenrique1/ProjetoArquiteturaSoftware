"""Rotas do serviço VENDAS. Só recebe a requisição e chama as regras."""

from flask import Blueprint, jsonify, request

import regras

rotas = Blueprint("vendas", __name__, url_prefix="/api")


def _nao_encontrado():
    return jsonify(erro="Venda não encontrada."), 404


@rotas.post("/vendas")
def criar():
    venda = regras.criar(request.get_json(silent=True) or {})
    return jsonify(venda.para_dict()), 201


@rotas.get("/vendas")
def listar():
    return jsonify([v.para_dict() for v in regras.listar()])


@rotas.get("/vendas/<int:venda_id>")
def buscar(venda_id):
    detalhe = regras.buscar_detalhes(venda_id)
    return jsonify(detalhe) if detalhe else _nao_encontrado()


@rotas.put("/vendas/<int:venda_id>")
def atualizar(venda_id):
    venda = regras.atualizar_vendedor(venda_id, request.get_json(silent=True) or {})
    return jsonify(venda.para_dict()) if venda else _nao_encontrado()


@rotas.patch("/vendas/<int:venda_id>/cancelar")
def cancelar(venda_id):
    venda = regras.cancelar(venda_id)
    return jsonify(venda.para_dict()) if venda else _nao_encontrado()
