"""Testes de seguranca (RNF01/RNF02): injecao de SQL, XSS, validacao de entradas, 404 sem traceback, debug e segredo.
Uso: python docs/verificacoes/verificar_seguranca.py [PASTA_TEMPORARIA]
Requer: pip install flask
"""
import tempfile
import sys, os, sqlite3
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
import sys as _s
OUT = _s.argv[1] if len(_s.argv) > 1 else tempfile.mkdtemp()
import app as a
a.DB_NAME = os.path.join(OUT, "sec.db")
if os.path.exists(a.DB_NAME): os.remove(a.DB_NAME)
a.init_db()
c = a.app.test_client()
base = dict(tipo="Entrada", produto="Fita Adesiva Padrão", quantidade="1", data="01/01/2026", responsavel="x")

def post(**kw):
    f = dict(base); f.update(kw)
    return c.post("/movimentacao", data=f, follow_redirects=True).get_data(as_text=True)

def tabelas():
    con = sqlite3.connect(a.DB_NAME)
    r = [x[0] for x in con.execute("select name from sqlite_master where type='table'")]
    n = con.execute("select count(*) from movimentacoes").fetchone()[0]
    con.close(); return r, n

print("1 SQLi produto:", "Produto não encontrado" in post(produto="x'; DROP TABLE produtos;--"), tabelas())
print("2 SQLi tipo:", "Tipo de operação inválido" in post(tipo="Entrada'; DROP TABLE produtos;--"), tabelas())
print("3 XSS em responsavel (aceito, mas nunca exibido):", "sucesso" in post(responsavel="<script>alert(1)</script>"))
print("4 XSS em data -> painel escapado:", end=" ")
post(data="<script>alert(2)</script>")
h = c.get("/").get_data(as_text=True)
print("<script>alert(2)" not in h and "&lt;script&gt;" in h)
print("5 responsavel vazio recusado:", "Informe o responsável" in post(responsavel="   "))
print("6 data vazia recusada:", "Informe a data" in post(data=""))
print("7 quantidade enorme recusada (sem erro 500):", "quantidade máxima" in post(quantidade=str(10**30)))
print("8 quantidade texto recusada:", "maior que zero" in post(quantidade="abc"))
r = c.post("/movimentacao", data={}, follow_redirects=True)
print("9 POST sem campos (sem 500):", r.status_code, "Tipo de operação inválido" in r.get_data(as_text=True))
r = c.get("/inexistente"); print("10 404 sem traceback:", r.status_code, "Traceback" not in r.get_data(as_text=True))
print("11 debug desligado por padrão:", a.app.debug is False, "| secret_key padrão fixa?", a.app.secret_key == 'artinpack_secret_key')
print("12 rotas:", sorted(r.rule for r in a.app.url_map.iter_rules() if r.endpoint != 'static'))
print("13 senhas no banco:", [x for t in tabelas()[0] for x in sqlite3.connect(a.DB_NAME).execute(f"pragma table_info({t})") if 'senha' in x[1].lower()])


