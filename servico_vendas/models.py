"""Modelos do serviço VENDAS. Apenas as tabelas ficam aqui."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Venda(db.Model):
    """Tabela de vendas do pet shop.

    cliente_id, produto_id e vendedor_id são apenas ids inteiros (sem ForeignKey):
    este serviço nunca acessa o banco dos outros, apenas consulta por HTTP.
    """

    __tablename__ = "vendas"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, nullable=False)
    produto_id = db.Column(db.Integer, nullable=False)
    vendedor_id = db.Column(db.Integer, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), nullable=False, default="concluida")  # concluida ou cancelada
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def para_dict(self):
        """Converte a venda em dicionário para resposta JSON."""
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "produto_id": self.produto_id,
            "vendedor_id": self.vendedor_id,
            "quantidade": self.quantidade,
            "valor_unitario": self.valor_unitario,
            "total": self.total,
            "status": self.status,
            "criado_em": self.criado_em.isoformat(timespec="seconds"),
        }
