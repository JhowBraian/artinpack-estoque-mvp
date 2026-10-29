from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
# A chave de sessão vem do ambiente; sem ela, gera-se uma chave aleatória a cada execução.
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

DB_NAME = os.environ.get('DB_PATH', 'database.db')
MAX_QUANTIDADE = 100000

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                minimo INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                produto TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                data TEXT NOT NULL,
                responsavel TEXT NOT NULL
            )
        ''')
        # Inserir dados iniciais de exemplo
        cursor.execute("INSERT INTO produtos (nome, quantidade, minimo) VALUES ('Caixa de Papelão Reforçada', 15, 5)")
        cursor.execute("INSERT INTO produtos (nome, quantidade, minimo) VALUES ('Fita Adesiva Padrão', 2, 10)")
        cursor.execute("INSERT INTO produtos (nome, quantidade, minimo) VALUES ('Plástico Bolha (Metro)', 48, 10)")
        conn.commit()
        conn.close()

def ler_quantidade(valor):
    """Converte o campo de quantidade; texto inválido vira 0 (recusado na validação)."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0

def validar_movimentacao(tipo, quantidade, data, responsavel, saldo, produto=''):
    """Retorna a mensagem de erro da movimentação ou None se ela for válida.
    saldo é a quantidade atual do produto, ou None se o produto não existir."""
    if tipo not in ('Entrada', 'Saída'):
        return 'Tipo de operação inválido.'
    if quantidade <= 0:
        return 'A quantidade deve ser maior que zero.'
    if quantidade > MAX_QUANTIDADE:
        return f'A quantidade máxima por lançamento é {MAX_QUANTIDADE}.'
    if not data or len(data) > 30:
        return 'Informe a data (até 30 caracteres).'
    if not responsavel or len(responsavel) > 100:
        return 'Informe o responsável (até 100 caracteres).'
    if saldo is None:
        return 'Produto não encontrado.'
    if tipo == 'Saída' and quantidade > saldo:
        return f'Estoque insuficiente: há apenas {saldo} unidade(s) de "{produto}".'
    return None

@app.route('/saude')
def saude():
    """Verificação de disponibilidade usada pelo monitoramento: confirma que o banco responde."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("SELECT COUNT(*) FROM produtos").fetchone()
        conn.close()
        return {'status': 'ok'}, 200
    except sqlite3.Error:
        return {'status': 'erro'}, 503

@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= minimo")
    estoque_baixo = cursor.fetchone()[0]
    
    cursor.execute("SELECT nome, quantidade FROM produtos WHERE quantidade <= minimo")
    criticos = cursor.fetchall()

    cursor.execute("SELECT data FROM movimentacoes ORDER BY id DESC LIMIT 1")
    ultima = cursor.fetchone()
    ultima_movimentacao = ultima[0] if ultima else None

    conn.close()
    return render_template('index.html', total_produtos=total_produtos, estoque_baixo=estoque_baixo,
                           criticos=criticos, ultima_movimentacao=ultima_movimentacao)

@app.route('/movimentacao', methods=['GET', 'POST'])
def movimentacao():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == 'POST':
        tipo = request.form.get('tipo', '')
        produto = request.form.get('produto', '')
        data = request.form.get('data', '').strip()
        responsavel = request.form.get('responsavel', '').strip()

        quantidade = ler_quantidade(request.form.get('quantidade', ''))

        cursor.execute("SELECT quantidade FROM produtos WHERE nome = ?", (produto,))
        linha = cursor.fetchone()
        saldo = linha[0] if linha else None

        erro = validar_movimentacao(tipo, quantidade, data, responsavel, saldo, produto)

        if erro:
            flash(erro, 'erro')
        else:
            cursor.execute("INSERT INTO movimentacoes (tipo, produto, quantidade, data, responsavel) VALUES (?, ?, ?, ?, ?)",
                           (tipo, produto, quantidade, data, responsavel))
            delta = quantidade if tipo == 'Entrada' else -quantidade
            cursor.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE nome = ?", (delta, produto))
            conn.commit()
            flash('Movimentação registrada com sucesso!', 'sucesso')

        conn.close()
        return redirect(url_for('movimentacao'))

    cursor.execute("SELECT id, nome FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()
    conn.close()
    data_hoje = datetime.now().strftime('%d/%m/%Y %H:%M')
    return render_template('movimentacao.html', produtos=produtos, data_hoje=data_hoje)

# Cria o banco também quando o app é servido pelo gunicorn (produção), e não só via python app.py.
init_db()

if __name__ == '__main__':
    # Modo de depuração só quando solicitado (FLASK_DEBUG=1); escuta apenas em 127.0.0.1.
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1', host='127.0.0.1')