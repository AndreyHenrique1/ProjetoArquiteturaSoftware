"""O "telefone" deste serviço para falar com os outros serviços.

Uso (dentro de regras.py):
    import integracao
    resposta = integracao.chamar("PRODUTOS", "GET", "/api/produtos/1")
"""
import os

import requests

from erros import RegraDeNegocioError

URLS = {
    "PRODUTOS": os.environ.get("PRODUTOS_URL", "http://127.0.0.1:5001"),
    "CLIENTES": os.environ.get("CLIENTES_URL", "http://127.0.0.1:5002"),
    "VENDEDORES": os.environ.get("VENDEDORES_URL", "http://127.0.0.1:5003"),
    "VENDAS": os.environ.get("VENDAS_URL", "http://127.0.0.1:5004"),
}
TIMEOUT = 5
EU = "CLIENTES"


def chamar(destino, metodo, caminho, **kwargs):
    """Faz a chamada HTTP e mostra no terminal. Se o destino falhar, vira erro 400 claro."""
    print(f"[{EU}]   >>> ligando para {destino}: {metodo} {caminho}", flush=True)
    try:
        resposta = requests.request(metodo, URLS[destino] + caminho, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        print(f"[{EU}]   <<< {destino} não atendeu (fora do ar?)", flush=True)
        raise RegraDeNegocioError(f"O serviço {destino} está indisponível. Tente mais tarde.")
    except requests.exceptions.Timeout:
        print(f"[{EU}]   <<< {destino} demorou demais (timeout)", flush=True)
        raise RegraDeNegocioError(f"O serviço {destino} demorou demais (timeout).")
    print(f"[{EU}]   <<< {destino} respondeu {resposta.status_code}", flush=True)
    return resposta
