import sqlite3

import pytest

import app as aplicacao


@pytest.fixture
def banco(tmp_path, monkeypatch):
    """Banco SQLite temporário, criado do zero para cada teste."""
    caminho = str(tmp_path / 'teste.db')
    monkeypatch.setattr(aplicacao, 'DB_NAME', caminho)
    aplicacao.init_db()
    return caminho


@pytest.fixture
def cliente(banco):
    aplicacao.app.config['TESTING'] = True
    with aplicacao.app.test_client() as c:
        yield c


@pytest.fixture
def saldo(banco):
    def ler(nome):
        conn = sqlite3.connect(banco)
        linha = conn.execute("SELECT quantidade FROM produtos WHERE nome = ?", (nome,)).fetchone()
        conn.close()
        return linha[0] if linha else None
    return ler
