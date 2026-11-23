"""Regras de negócio do serviço VENDEDORES (sem Flask, sem rotas)."""

from erros import RegraDeNegocioError
from models import Vendedor, db


def criar(dados):
    """Cria um novo vendedor validando o campo obrigatório e o turno."""
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise RegraDeNegocioError("O campo 'nome' é obrigatório.")
    turno = (dados.get("turno") or "manha").strip().lower()
    if turno not in ("manha", "tarde", "noite"):
        raise RegraDeNegocioError("O turno deve ser 'manha', 'tarde' ou 'noite'.")
    vendedor = Vendedor(nome=nome, turno=turno)
    db.session.add(vendedor)
    db.session.commit()
    return vendedor


def dados_iniciais():
    """Cria vendedores de exemplo se o banco estiver vazio."""
    if Vendedor.query.count() == 0:
        db.session.add(Vendedor(nome="Mariana Alves", turno="manha"))
        db.session.add(Vendedor(nome="Pedro Lima", turno="tarde"))
        db.session.commit()


def listar():
    """Retorna todos os vendedores ordenados por id."""
    return Vendedor.query.order_by(Vendedor.id).all()


def buscar(vendedor_id):
    """Busca um vendedor pelo id."""
    return db.session.get(Vendedor, vendedor_id)


def atualizar(vendedor_id, dados):
    """Atualiza os campos de um vendedor existente."""
    vendedor = buscar(vendedor_id)
    if vendedor is None:
        return None
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise RegraDeNegocioError("O campo 'nome' é obrigatório.")
    vendedor.nome = nome
    turno = (dados.get("turno", vendedor.turno) or "manha").strip().lower()
    if turno not in ("manha", "tarde", "noite"):
        raise RegraDeNegocioError("O turno deve ser 'manha', 'tarde' ou 'noite'.")
    vendedor.turno = turno
    db.session.commit()
    return vendedor


def inativar(vendedor_id):
    """Marca o vendedor como inativo."""
    vendedor = buscar(vendedor_id)
    if vendedor is None:
        return None
    if not vendedor.ativo:
        raise RegraDeNegocioError("O vendedor já está inativo.")
    vendedor.ativo = False
    db.session.commit()
    return vendedor
