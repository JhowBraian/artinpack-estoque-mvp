from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
# A chave de sessão vem do ambiente; sem ela, gera-se uma chave aleatória a cada execução.
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

DB_NAME = 'database.db'
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

        try:
            quantidade = int(request.form.get('quantidade', ''))
        except ValueError:
            quantidade = 0

        cursor.execute("SELECT quantidade FROM produtos WHERE nome = ?", (produto,))
        linha = cursor.fetchone()

        erro = None
        if tipo not in ('Entrada', 'Saída'):
            erro = 'Tipo de operação inválido.'
        elif quantidade <= 0:
            erro = 'A quantidade deve ser maior que zero.'
        elif quantidade > MAX_QUANTIDADE:
            erro = f'A quantidade máxima por lançamento é {MAX_QUANTIDADE}.'
        elif not data or len(data) > 30:
            erro = 'Informe a data (até 30 caracteres).'
        elif not responsavel or len(responsavel) > 100:
            erro = 'Informe o responsável (até 100 caracteres).'
        elif linha is None:
            erro = 'Produto não encontrado.'
        elif tipo == 'Saída' and quantidade > linha[0]:
            erro = f'Estoque insuficiente: há apenas {linha[0]} unidade(s) de "{produto}".'

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

if __name__ == '__main__':
    init_db()
    # Modo de depuração só quando solicitado (FLASK_DEBUG=1); escuta apenas em 127.0.0.1.
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1', host='127.0.0.1')