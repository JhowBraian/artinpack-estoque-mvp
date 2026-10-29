def movimentar(cliente, **campos):
    dados = dict(tipo='Entrada', produto='Fita Adesiva Padrão', quantidade='10',
                 data='29/10/2026 10:00', responsavel='Ronaldo94')
    dados.update(campos)
    return cliente.post('/movimentacao', data=dados, follow_redirects=True)


def test_painel_mostra_totais_e_item_critico(cliente):
    html = cliente.get('/').get_data(as_text=True)
    assert '<p>3</p>' in html
    assert '<p class="alerta">1</p>' in html
    assert 'Fita Adesiva Padrão' in html
    assert 'Nenhuma movimentação' in html


def test_formulario_lista_produtos_do_banco(cliente):
    html = cliente.get('/movimentacao').get_data(as_text=True)
    for nome in ('Caixa de Papelão Reforçada', 'Fita Adesiva Padrão', 'Plástico Bolha (Metro)'):
        assert nome in html


def test_entrada_atualiza_saldo_e_painel(cliente, saldo):
    resposta = movimentar(cliente, quantidade='10')
    assert 'Movimentação registrada com sucesso!' in resposta.get_data(as_text=True)
    assert saldo('Fita Adesiva Padrão') == 12

    painel = cliente.get('/').get_data(as_text=True)
    assert '<p class="alerta">0</p>' in painel
    assert 'Nenhum produto em nível crítico.' in painel
    assert '29/10/2026 10:00' in painel


def test_saida_reduz_saldo(cliente, saldo):
    movimentar(cliente, tipo='Saída', produto='Plástico Bolha (Metro)', quantidade='8')
    assert saldo('Plástico Bolha (Metro)') == 40


def test_saida_maior_que_saldo_nao_altera_estoque(cliente, saldo):
    html = movimentar(cliente, tipo='Saída', quantidade='3').get_data(as_text=True)
    assert 'Estoque insuficiente' in html
    assert 'role="alert"' in html
    assert saldo('Fita Adesiva Padrão') == 2


def test_quantidade_em_texto_e_recusada_sem_erro_500(cliente, saldo):
    resposta = movimentar(cliente, quantidade='abc')
    assert resposta.status_code == 200
    assert 'A quantidade deve ser maior que zero.' in resposta.get_data(as_text=True)
    assert saldo('Fita Adesiva Padrão') == 2


def test_post_sem_campos_nao_quebra(cliente):
    resposta = cliente.post('/movimentacao', data={}, follow_redirects=True)
    assert resposta.status_code == 200
    assert 'Tipo de operação inválido.' in resposta.get_data(as_text=True)


def test_injecao_de_sql_no_produto_nao_altera_banco(cliente, saldo):
    html = movimentar(cliente, produto="Fita Adesiva Padrão' OR '1'='1").get_data(as_text=True)
    assert 'Produto não encontrado.' in html
    assert saldo('Fita Adesiva Padrão') == 2
    assert saldo('Caixa de Papelão Reforçada') == 15


def test_data_com_script_e_escapada_no_painel(cliente):
    movimentar(cliente, data='<script>alert(1)</script>')
    html = cliente.get('/').get_data(as_text=True)
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html


def test_rota_inexistente_retorna_404(cliente):
    assert cliente.get('/nao-existe').status_code == 404
