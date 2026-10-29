"""Mede o tempo de resposta do MVP (RNF03).

Uso: com o sistema em execução (python app.py), rode em outro terminal:
    python medir_desempenho.py [URL_BASE]

Cada operação é executada 1 vez para aquecimento e depois 5 vezes; o resultado
é a mediana, em milissegundos. O fluxo central é: abrir o formulário, enviar
uma entrada de 1 unidade e abrir o painel. ATENÇÃO: o teste grava movimentações
reais no banco; use uma cópia do banco, e não os dados do parceiro.
"""
import http.cookiejar
import platform
import statistics
import sys
import time
import urllib.parse
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000"
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def abrir(caminho):
    with opener.open(BASE + caminho) as resposta:
        return len(resposta.read())


def lancar():
    dados = urllib.parse.urlencode({
        "tipo": "Entrada", "produto": "Plástico Bolha (Metro)", "quantidade": "1",
        "data": "01/01/2026", "responsavel": "medicao",
    }).encode()
    with opener.open(urllib.request.Request(BASE + "/movimentacao", data=dados)) as resposta:
        return len(resposta.read())


def fluxo_central():
    abrir("/movimentacao")
    lancar()
    abrir("/")


def mediana_ms(funcao):
    funcao()  # aquecimento
    tempos = []
    for _ in range(5):
        inicio = time.perf_counter()
        funcao()
        tempos.append((time.perf_counter() - inicio) * 1000)
    return statistics.median(tempos)


print(f"Python {platform.python_version()} | {platform.platform()} | alvo: {BASE}")
print(f"Painel (GET /): {mediana_ms(lambda: abrir('/')):.1f} ms")
print(f"Formulário (GET /movimentacao): {mediana_ms(lambda: abrir('/movimentacao')):.1f} ms")
print(f"Tamanho do painel: {abrir('/')} bytes")
print(f"Fluxo central: {mediana_ms(fluxo_central):.1f} ms")
