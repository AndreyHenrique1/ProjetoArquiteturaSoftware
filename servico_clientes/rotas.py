"""Rotas do serviço CLIENTES. Só recebe a requisição e chama as regras."""

from flask import Blueprint, jsonify, request

import regras

rotas = Blueprint("clientes", __name__, url_prefix="/api")


def _nao_encontrado():
    return jsonify(erro="Cliente não encontrado."), 404


@rotas.post("/clientes")
def criar():
    cliente = regras.criar(request.get_json(silent=True) or {})
    return jsonify(cliente.para_dict()), 201


@rotas.get("/clientes")
def listar():
    return jsonify([c.para_dict() for c in regras.listar()])


@rotas.get("/clientes/<int:cliente_id>")
def buscar(cliente_id):
    cliente = regras.buscar(cliente_id)
    return jsonify(cliente.para_dict()) if cliente else _nao_encontrado()


@rotas.put("/clientes/<int:cliente_id>")
def atualizar(cliente_id):
    cliente = regras.atualizar(cliente_id, request.get_json(silent=True) or {})
    return jsonify(cliente.para_dict()) if cliente else _nao_encontrado()


@rotas.patch("/clientes/<int:cliente_id>/inativar")
def inativar(cliente_id):
    cliente = regras.inativar(cliente_id)
    return jsonify(cliente.para_dict()) if cliente else _nao_encontrado()


@rotas.get("/clientes/<int:cliente_id>/ativo")
def esta_ativo(cliente_id):
    cliente = regras.buscar(cliente_id)
    if cliente is None:
        return _nao_encontrado()
    return jsonify(id=cliente.id, ativo=cliente.ativo)
