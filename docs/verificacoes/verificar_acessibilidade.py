"""Verificacoes de acessibilidade (RNF04): contrastes calculados, rotulos associados, regioes, papeis das mensagens.
Uso: python docs/verificacoes/verificar_acessibilidade.py [PASTA_TEMPORARIA]
Requer: pip install flask
"""
import tempfile
import sys, os, re
from html.parser import HTMLParser
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
import sys as _s
OUT = _s.argv[1] if len(_s.argv) > 1 else tempfile.mkdtemp()
import app as a
a.DB_NAME = os.path.join(OUT, "a11y.db")
if os.path.exists(a.DB_NAME): os.remove(a.DB_NAME)
a.init_db()
c = a.app.test_client()

def lum(h):
    h = h.lstrip('#'); r, g, b = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    f = lambda v: v/12.92 if v <= 0.03928 else ((v+0.055)/1.055)**2.4
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b)
def cr(fg, bg):
    l1, l2 = sorted((lum(fg), lum(bg)), reverse=True); return (l1+0.05)/(l2+0.05)

pares = {
 "texto #1f2d3d / fundo #f4f6f9": ("#1f2d3d", "#f4f6f9"),
 "texto #1f2d3d / branco": ("#1f2d3d", "#ffffff"),
 "link #0056b3 / branco": ("#0056b3", "#ffffff"),
 "link #0056b3 / fundo #f4f6f9": ("#0056b3", "#f4f6f9"),
 "botão branco / #0056b3": ("#ffffff", "#0056b3"),
 "botão branco / hover #003d80": ("#ffffff", "#003d80"),
 "cabeçalho branco / #1f2d3d": ("#ffffff", "#1f2d3d"),
 "alerta erro #721c24 / #f8d7da": ("#721c24", "#f8d7da"),
 "alerta sucesso #155724 / #d4edda": ("#155724", "#d4edda"),
 "número alerta #b02a37 / branco": ("#b02a37", "#ffffff"),
 "título card #4a4a4a / branco": ("#4a4a4a", "#ffffff"),
 "borda campo #5f6b7a / branco (não-texto, mín 3)": ("#5f6b7a", "#ffffff"),
 "foco #1f2d3d / branco (mín 3)": ("#1f2d3d", "#ffffff"),
 "ANTES: azul #007bff / branco": ("#007bff", "#ffffff"),
}
for k, (f, b) in pares.items(): print(f"{cr(f, b):5.2f}:1  {k}")

class P(HTMLParser):
    def __init__(s): super().__init__(); s.ids=set(); s.fors=[]; s.ctrls=[]; s.tags=[]; s.attrs=[]
    def handle_starttag(s, t, at):
        d = dict(at); s.tags.append(t); s.attrs.append((t, d))
        if 'id' in d: s.ids.add(d['id'])
        if t == 'label': s.fors.append(d.get('for'))
        if t in ('input', 'select', 'textarea'): s.ctrls.append(d.get('id'))
for rota in ("/", "/movimentacao"):
    h = c.get(rota).get_data(as_text=True); p = P(); p.feed(h)
    print(rota, "| lang:", 'lang="pt-BR"' in h, "| viewport:", 'name="viewport"' in h,
          "| main:", 'main' in p.tags, "| nav:", 'nav' in p.tags, "| h1:", p.tags.count('h1'))
    print("   controles sem rótulo:", [x for x in p.ctrls if x not in p.fors], "| for sem id:", [x for x in p.fors if x not in p.ids])

base = dict(tipo="Saída", produto="Fita Adesiva Padrão", quantidade="50", data="01/01/2026", responsavel="x")
h = c.post("/movimentacao", data=base, follow_redirects=True).get_data(as_text=True)
print('erro com role="alert" e ícone/texto:', 'role="alert"' in h and "Atenção:" in h and "&#9888;" in h)
base["quantidade"] = "1"
h = c.post("/movimentacao", data=base, follow_redirects=True).get_data(as_text=True)
print('sucesso com role="status" e ícone/texto:', 'role="status"' in h and "Sucesso:" in h)
h = c.get("/").get_data(as_text=True)
print("painel: situação em texto:", "Estoque crítico" in h, "| caption:", "<caption>" in h, '| th scope:', 'scope="col"' in h)
# painel sem itens críticos
import sqlite3; con = sqlite3.connect(a.DB_NAME); con.execute("update produtos set quantidade=99"); con.commit(); con.close()
print("painel sem críticos mostra mensagem:", "Nenhum produto em nível crítico" in c.get("/").get_data(as_text=True))
# altura mínima declarada
for f in ("index.html", "movimentacao.html"):
    css = open(os.path.join(os.path.join(ROOT, "templates"), f), encoding="utf-8").read()
    print(f, "min-height:44px:", css.count("min-height: 44px"), "| font-size em px fixo (<16):", re.findall(r"font-size:\s*(\d+)px", css))


