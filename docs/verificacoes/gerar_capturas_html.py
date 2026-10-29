"""Gera os HTMLs das telas do prototipo com dados ficticios (depois fotografados com o Chrome em modo headless).
Uso: python docs/verificacoes/gerar_capturas_html.py [PASTA_TEMPORARIA]
Requer: pip install flask
"""
import tempfile
import sys, os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
import sys as _s
OUT = _s.argv[1] if len(_s.argv) > 1 else tempfile.mkdtemp()
import app as a

out = OUT
a.DB_NAME = os.path.join(out, "shots.db")
if os.path.exists(a.DB_NAME): os.remove(a.DB_NAME)
a.init_db()
c = a.app.test_client()

DEMO_DATA = "01/10/2026 09:30"

def demo(html, form=False, qty=None, saida=False, fita=False):
    html = html.replace("<span>Ronaldo94</span>", "<span>Operador Demo</span>")
    html = html.replace('value="Ronaldo94"', 'value="Operador Demo"')
    html = re.sub(r'(name="data" value=")[^"]*(")', r"\g<1>" + DEMO_DATA + r"\2", html)
    if qty: html = html.replace('value="10"', f'value="{qty}"')
    if saida: html = html.replace('<option value="Saída">', '<option value="Saída" selected>')
    if fita: html = html.replace('<option value="Fita Adesiva Padrão">', '<option value="Fita Adesiva Padrão" selected>')
    return html

def save(nome, html):
    with open(os.path.join(out, nome), "w", encoding="utf-8") as f: f.write(html)

# movimentação prévia (mantém a Fita Adesiva em 2 e preenche "Última Movimentação")
c.post("/movimentacao", data=dict(tipo="Entrada", produto="Plástico Bolha (Metro)", quantidade="5",
                                  data=DEMO_DATA, responsavel="Operador Demo"))
c.get("/movimentacao")  # consome a mensagem da movimentação de preparação
save("tela1.html", demo(c.get("/").get_data(as_text=True)))
save("tela2.html", demo(c.get("/movimentacao").get_data(as_text=True), qty=1, saida=True, fita=True))

# Tela 3: erro (saída de 50 com saldo 2)
r = c.post("/movimentacao", data=dict(tipo="Saída", produto="Fita Adesiva Padrão", quantidade="50",
                                      data=DEMO_DATA, responsavel="Operador Demo"), follow_redirects=True)
save("tela3_erro.html", demo(r.get_data(as_text=True), qty=1, saida=True, fita=True))

# Tela 3: sucesso (saída de 1) e painel atualizado
r = c.post("/movimentacao", data=dict(tipo="Saída", produto="Fita Adesiva Padrão", quantidade="1",
                                      data=DEMO_DATA, responsavel="Operador Demo"), follow_redirects=True)
save("tela3_sucesso.html", demo(r.get_data(as_text=True), qty=1, saida=True, fita=True))
save("tela3_painel_atualizado.html", demo(c.get("/").get_data(as_text=True)))
print("ok")

