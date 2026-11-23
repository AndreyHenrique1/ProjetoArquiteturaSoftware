"""Modelos do serviço CLIENTES. Apenas as tabelas ficam aqui."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Cliente(db.Model):
    """Tabela de clientes (tutores e seus pets) do pet shop."""

    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    nome_tutor = db.Column(db.String(100), nullable=False)
    nome_pet = db.Column(db.String(100), nullable=False, default="")
    especie = db.Column(db.String(50), nullable=False, default="")
    telefone = db.Column(db.String(20), nullable=False, default="")
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def para_dict(self):
        """Converte o cliente em dicionário para resposta JSON."""
        return {
            "id": self.id,
            "nome_tutor": self.nome_tutor,
            "nome_pet": self.nome_pet,
            "especie": self.especie,
            "telefone": self.telefone,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat(timespec="seconds"),
        }
