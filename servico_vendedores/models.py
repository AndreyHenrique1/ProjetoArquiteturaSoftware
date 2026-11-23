"""Modelos do serviço VENDEDORES. Apenas as tabelas ficam aqui."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Vendedor(db.Model):
    """Tabela de vendedores do pet shop."""

    __tablename__ = "vendedores"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    turno = db.Column(db.String(20), nullable=False, default="manha")  # manha, tarde ou noite
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def para_dict(self):
        """Converte o vendedor em dicionário para resposta JSON."""
        return {
            "id": self.id,
            "nome": self.nome,
            "turno": self.turno,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat(timespec="seconds"),
        }
