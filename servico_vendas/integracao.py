"""O "telefone" deste serviço para falar com os outros serviços.

Uso (dentro de regras.py):
    import integracao
    resposta = integracao.chamar("PRODUTOS", "GET", "/api/produtos/1")
"""
import os

import requests

from erros import RegraDeNegocioError

URLS = {
    "PRODUTOS": os.environ.get("PRODUTOS_URL", "http://127.0.0.1:5001").strip().rstrip("/"),
    "CLIENTES": os.environ.get("CLIENTES_URL", "http://127.0.0.1:5002").strip().rstrip("/"),
    "VENDEDORES": os.environ.get("VENDEDORES_URL", "http://127.0.0.1:5003").strip().rstrip("/"),
    "VENDAS": os.environ.get("VENDAS_URL", "http://127.0.0.1:5004").strip().rstrip("/"),
}
TIMEOUT = 5
EU = "VENDAS"


def chamar(destino, metodo, caminho, **kwargs):
    """Faz a chamada HTTP e mostra no terminal. Se o destino falhar, vira erro 400 claro."""
    print(f"[{EU}]   >>> ligando para {destino}: {metodo} {caminho}", flush=True)
    tentativas = 2 if metodo.upper() == "GET" else 1
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.request(metodo, URLS[destino] + caminho, timeout=TIMEOUT, **kwargs)
            print(f"[{EU}]   <<< {destino} respondeu {resposta.status_code}", flush=True)
            return resposta
        except requests.exceptions.ConnectionError:
            print(f"[{EU}]   <<< {destino} não atendeu (fora do ar?)", flush=True)
            if tentativa == 1 and tentativas == 2:
                print(f"[{EU}]   tentativa 2", flush=True)
                continue
            raise RegraDeNegocioError(f"O serviço {destino} está indisponível. Tente mais tarde.")
        except requests.exceptions.Timeout:
            print(f"[{EU}]   <<< {destino} demorou demais (timeout)", flush=True)
            if tentativa == 1 and tentativas == 2:
                print(f"[{EU}]   tentativa 2", flush=True)
                continue
            raise RegraDeNegocioError(f"O serviço {destino} demorou demais (timeout).")
        except requests.exceptions.RequestException:
            print(f"[{EU}]   <<< {destino} URL mal configurada", flush=True)
            raise RegraDeNegocioError(f"A URL do serviço {destino} está mal configurada. Confira a variável {destino}_URL.")


def ler_json(resposta, destino):
    """Tenta decodificar JSON da resposta; em caso de falha, lança RegraDeNegocioError."""
    try:
        return resposta.json()
    except ValueError:
        print(f"[{EU}]   <<< {destino} respondeu algo inesperado (status {resposta.status_code})", flush=True)
        raise RegraDeNegocioError(f"O serviço {destino} respondeu algo inesperado (status {resposta.status_code}). Ele pode estar acordando; tente de novo em instantes.")
