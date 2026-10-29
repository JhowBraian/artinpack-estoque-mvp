import pytest

from app import MAX_QUANTIDADE, ler_quantidade, validar_movimentacao


def valida(**campos):
    padrao = dict(tipo='Entrada', quantidade=5, data='29/10/2026 10:00', responsavel='Ronaldo94', saldo=10, produto='Caixa')
    padrao.update(campos)
    return validar_movimentacao(**padrao)


def test_movimentacao_valida_nao_retorna_erro():
    assert valida() is None


def test_saida_igual_ao_saldo_e_permitida():
    assert valida(tipo='Saída', quantidade=10, saldo=10) is None


def test_saida_maior_que_saldo_e_recusada():
    assert valida(tipo='Saída', quantidade=11, saldo=10, produto='Caixa') == \
        'Estoque insuficiente: há apenas 10 unidade(s) de "Caixa".'


def test_entrada_maior_que_saldo_e_permitida():
    assert valida(tipo='Entrada', quantidade=500, saldo=1) is None


@pytest.mark.parametrize('tipo', ['', 'entrada', 'Transferência', "Entrada' OR 1=1"])
def test_tipo_invalido(tipo):
    assert valida(tipo=tipo) == 'Tipo de operação inválido.'


@pytest.mark.parametrize('quantidade', [0, -1])
def test_quantidade_zero_ou_negativa(quantidade):
    assert valida(quantidade=quantidade) == 'A quantidade deve ser maior que zero.'


def test_quantidade_acima_do_limite():
    assert valida(quantidade=MAX_QUANTIDADE + 1) == f'A quantidade máxima por lançamento é {MAX_QUANTIDADE}.'


@pytest.mark.parametrize('data', ['', 'x' * 31])
def test_data_vazia_ou_longa(data):
    assert valida(data=data) == 'Informe a data (até 30 caracteres).'


@pytest.mark.parametrize('responsavel', ['', 'x' * 101])
def test_responsavel_vazio_ou_longo(responsavel):
    assert valida(responsavel=responsavel) == 'Informe o responsável (até 100 caracteres).'


def test_produto_inexistente():
    assert valida(saldo=None) == 'Produto não encontrado.'


@pytest.mark.parametrize('entrada, esperado', [('7', 7), ('-3', -3), ('abc', 0), ('', 0), (None, 0), ('2.5', 0)])
def test_ler_quantidade(entrada, esperado):
    assert ler_quantidade(entrada) == esperado
