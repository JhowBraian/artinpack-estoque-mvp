"""Confere que os dados de demonstracao das telas funcionam como descrito (painel, formulario, erro e sucesso).
Uso: python docs/verificacoes/verificar_demo.py [PASTA_TEMPORARIA]
Requer: pip install flask
"""
import tempfile
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
import sys as _s
OUT = _s.argv[1] if len(_s.argv) > 1 else tempfile.mkdtemp()
import app as a
a.DB_NAME = os.path.join(OUT, "demo.db")
if os.path.exists(a.DB_NAME): os.remove(a.DB_NAME)
a.init_db()
c = a.app.test_client()
h = c.get("/").get_data(as_text=True)
print("T1: Total 3 / Fita Adesiva Padrão / 2 / Estoque crítico / Nenhuma movimentação:",
      "Fita Adesiva Padrão" in h, "Estoque crítico" in h, "Nenhuma movimentação" in h)
h = c.get("/movimentacao").get_data(as_text=True)
print("T2: ID #2 = Fita Adesiva Padrão:", "Fita Adesiva Padrão - ID #2" in h, "| IDs:", [s for s in ("ID #1", "ID #2", "ID #3") if s in h])
f = dict(tipo="Saída", produto="Fita Adesiva Padrão", quantidade="50", data="01/10/2026 09:30", responsavel="Operador Demo")
h = c.post("/movimentacao", data=f, follow_redirects=True).get_data(as_text=True)
print("T3 erro:", "Estoque insuficiente: há apenas 2 unidade(s) de &#34;Fita Adesiva Padrão&#34;" in h or "há apenas 2 unidade(s)" in h)
f["quantidade"] = "1"
h = c.post("/movimentacao", data=f, follow_redirects=True).get_data(as_text=True)
print("T3 sucesso:", "Movimentação registrada com sucesso!" in h)
h = c.get("/").get_data(as_text=True)
print("T1 após sucesso: 01/10/2026 09:30 e quantidade 1:", "01/10/2026 09:30" in h, "<td>1</td>" in h)

