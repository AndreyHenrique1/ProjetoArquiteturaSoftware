"""Rotas do serviço VENDEDORES. Só recebe a requisição e chama as regras."""

from flask import Blueprint, jsonify, request

import regras

rotas = Blueprint("vendedores", __name__, url_prefix="/api")


def _nao_encontrado():
    return jsonify(erro="Vendedor não encontrado."), 404


@rotas.post("/vendedores")
def criar():
    vendedor = regras.criar(request.get_json(silent=True) or {})
    return jsonify(vendedor.para_dict()), 201


@rotas.get("/vendedores")
def listar():
    return jsonify([v.para_dict() for v in regras.listar()])


@rotas.get("/vendedores/<int:vendedor_id>")
def buscar(vendedor_id):
    vendedor = regras.buscar(vendedor_id)
    return jsonify(vendedor.para_dict()) if vendedor else _nao_encontrado()


@rotas.put("/vendedores/<int:vendedor_id>")
def atualizar(vendedor_id):
    vendedor = regras.atualizar(vendedor_id, request.get_json(silent=True) or {})
    return jsonify(vendedor.para_dict()) if vendedor else _nao_encontrado()


@rotas.patch("/vendedores/<int:vendedor_id>/inativar")
def inativar(vendedor_id):
    vendedor = regras.inativar(vendedor_id)
    return jsonify(vendedor.para_dict()) if vendedor else _nao_encontrado()


@rotas.get("/vendedores/<int:vendedor_id>/ativo")
def esta_ativo(vendedor_id):
    vendedor = regras.buscar(vendedor_id)
    if vendedor is None:
        return _nao_encontrado()
    return jsonify(id=vendedor.id, ativo=vendedor.ativo)
