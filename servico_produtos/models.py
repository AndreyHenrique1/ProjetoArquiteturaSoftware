"""Modelos do serviço PRODUTOS. Apenas as tabelas ficam aqui."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Produto(db.Model):
    """Tabela de produtos do pet shop (somente as tabelas ficam aqui)."""

    __tablename__ = "produtos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False, default="")
    preco = db.Column(db.Float, nullable=False, default=0.0)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def para_dict(self):
        """Converte o produto em dicionário para resposta JSON."""
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "preco": self.preco,
            "estoque": self.estoque,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat(timespec="seconds"),
        }
