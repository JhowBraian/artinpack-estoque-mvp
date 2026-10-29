import sqlite3

import app as aplicacao


def test_init_db_cria_tabelas_e_produtos_de_exemplo(banco):
    conn = sqlite3.connect(banco)
    tabelas = {t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    produtos = conn.execute("SELECT nome, quantidade, minimo FROM produtos ORDER BY id").fetchall()
    conn.close()
    assert {'produtos', 'movimentacoes'} <= tabelas
    assert produtos == [
        ('Caixa de Papelão Reforçada', 15, 5),
        ('Fita Adesiva Padrão', 2, 10),
        ('Plástico Bolha (Metro)', 48, 10),
    ]


def test_init_db_nao_sobrescreve_banco_existente(banco, saldo):
    conn = sqlite3.connect(banco)
    conn.execute("UPDATE produtos SET quantidade = 99 WHERE nome = 'Fita Adesiva Padrão'")
    conn.commit()
    conn.close()
    aplicacao.init_db()
    assert saldo('Fita Adesiva Padrão') == 99
