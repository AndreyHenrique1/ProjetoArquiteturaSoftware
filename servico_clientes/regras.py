"""Regras de negócio do serviço CLIENTES (sem Flask, sem rotas)."""

from erros import RegraDeNegocioError
from models import Cliente, db


def criar(dados):
    """Cria um novo cliente validando o campo obrigatório nome_tutor."""
    nome_tutor = (dados.get("nome_tutor") or "").strip()
    if not nome_tutor:
        raise RegraDeNegocioError("O campo 'nome_tutor' é obrigatório.")
    nome_pet = (dados.get("nome_pet") or "").strip()
    especie = (dados.get("especie") or "").strip()
    telefone = (dados.get("telefone") or "").strip()
    cliente = Cliente(nome_tutor=nome_tutor, nome_pet=nome_pet,
                      especie=especie, telefone=telefone)
    db.session.add(cliente)
    db.session.commit()
    return cliente


def dados_iniciais():
    """Cria clientes de exemplo se o banco estiver vazio."""
    if Cliente.query.count() == 0:
        db.session.add(Cliente(nome_tutor="Ana Silva", nome_pet="Rex", especie="Cachorro", telefone="11 9999-0001"))
        db.session.add(Cliente(nome_tutor="Carlos Souza", nome_pet="Mia", especie="Gato", telefone="11 9888-0002"))
        db.session.commit()


def listar():
    """Retorna todos os clientes ordenados por id."""
    return Cliente.query.order_by(Cliente.id).all()


def buscar(cliente_id):
    """Busca um cliente pelo id."""
    return db.session.get(Cliente, cliente_id)


def atualizar(cliente_id, dados):
    """Atualiza os campos de um cliente existente."""
    cliente = buscar(cliente_id)
    if cliente is None:
        return None
    nome_tutor = (dados.get("nome_tutor") or "").strip()
    if not nome_tutor:
        raise RegraDeNegocioError("O campo 'nome_tutor' é obrigatório.")
    cliente.nome_tutor = nome_tutor
    cliente.nome_pet = (dados.get("nome_pet") or "").strip()
    cliente.especie = (dados.get("especie") or "").strip()
    cliente.telefone = (dados.get("telefone") or "").strip()
    db.session.commit()
    return cliente


def inativar(cliente_id):
    """Marca o cliente como inativo."""
    cliente = buscar(cliente_id)
    if cliente is None:
        return None
    if not cliente.ativo:
        raise RegraDeNegocioError("O cliente já está inativo.")
    cliente.ativo = False
    db.session.commit()
    return cliente
