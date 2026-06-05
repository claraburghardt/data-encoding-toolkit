import socket
import json
import threading

from crc_module import CRC4
from hamming_module_2 import Hamming74
from repetition_module import Repeticao

HOST = "127.0.0.1"
PORT = 65432

crc = CRC4()
hamming = Hamming74()
repeticao = Repeticao()


def processar(dados: dict) -> dict:
    """
    Processa a requisição recebida do cliente.

    Campos esperados em dados:
        - algoritmo: "CRC-4", "Hamming (7,4)" ou "Repetição"
        - bits: string binária (mensagem a verificar/corrigir)
        - padding (opcional): int, necessário para Hamming
        - r (opcional): int, necessário para Repetição

    Retorna dict com o resultado.
    """
    algoritmo = dados.get("algoritmo", "")
    bits = dados.get("bits", "")

    if not bits or not all(c in "01" for c in bits):
        return {"erro": "Entrada binária inválida."}

    if algoritmo == "CRC-4":
        try:
            sem_erro, resto = crc.verificar(bits)
        except ValueError as e:
            return {"erro": str(e)}

        bits_sem_crc = bits[:-4]
        return {
            "algoritmo": "CRC-4",
            "mensagem_recebida": bits,
            "resto": resto,
            "sem_erro": sem_erro,
            "mensagem_sem_crc": bits_sem_crc if sem_erro else None,
        }

    elif algoritmo == "Hamming (7,4)":
        padding = int(dados.get("padding", 0))
        try:
            resultado, erros = hamming.decoder(bits, padding)
        except ValueError as e:
            return {"erro": str(e)}

        return {
            "algoritmo": "Hamming (7,4)",
            "mensagem_recebida": bits,
            "mensagem_corrigida": resultado,
            "erros": erros,
        }

    elif algoritmo == "Repetição":
        r = int(dados.get("r", 3))
        try:
            resultado, erros = repeticao.decoder(bits, r)
        except ValueError as e:
            return {"erro": str(e)}

        return {
            "algoritmo": "Repetição",
            "mensagem_recebida": bits,
            "mensagem_corrigida": resultado,
            "erros": erros,
        }

    else:
        return {"erro": f"Algoritmo desconhecido: '{algoritmo}'"}


def handle_client(conn, addr):
    print(f"[Servidor] Conexão de {addr}")
    try:
        dados_raw = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            dados_raw += chunk
            if dados_raw.endswith(b"\n"):
                break

        dados = json.loads(dados_raw.decode("utf-8"))
        print(f"[Servidor] Recebido: {dados}")

        resposta = processar(dados)
        print(f"[Servidor] Enviando: {resposta}")

        conn.sendall((json.dumps(resposta) + "\n").encode("utf-8"))
    except Exception as e:
        erro = {"erro": str(e)}
        conn.sendall((json.dumps(erro) + "\n").encode("utf-8"))
    finally:
        conn.close()


def iniciar_servidor():
    """Inicia o servidor TCP em localhost:65432."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[Servidor] Aguardando conexões em {HOST}:{PORT}...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    iniciar_servidor()
