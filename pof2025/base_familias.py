"""Base de familias (unidades de consumo) da POF 2024-2025 com os fatores do painel.

Uma linha por unidade de consumo (UC), que e a "familia" das tabelas do IBGE e, no questionario POF 6, a unidade
em que a EBIA e perguntada a pessoa de referencia. Quando o IBGE liberar a EBIA, basta juntar pela chave
COD_UPA + NUM_DOM + NUM_UC.

Fatores do painel (os 11 da PNADC) e como cada um sai da POF 2024-2025 liberada em 27/11/2026:
  sexo        sexo de nascimento da pessoa de referencia da UC (V010304)                  pronto
  idade_ref   idade da pessoa de referencia: ate 29, 30-44, 45-59, 60+ (V010303)           pronto
  crianca5    algum morador da UC com menos de 5 anos                                       pronto
  idoso60     algum morador da UC com 60 anos ou mais                                       pronto
  tam_dom     moradores da UC: 1, 2-3, 4-5, 6+                                              pronto
  sit_dom     urbano ou rural (TIPO_SITUACAO_REG)                                           pronto
  capital     estrato "Municipio da Capital" (area urbana da capital) ou nao                pronto, com diferenca
  faixa_renda rendimento per capita da UC em salarios minimos                                pronto, com diferenca
  ocupacao    posicao no trabalho principal da pessoa de referencia nos 12 meses            parcial (categorias agrupadas)
  cor_raca    nao liberada
  instrucao   nao liberada
Moradores contados: todos os da UC, exceto pensionista, empregado domestico e parente do empregado domestico
(V010106 17, 18 e 19), como no rendimento per capita da PNADC.

Variaveis acrescentadas (informacoes novas, sem EBIA): gasto mensal com alimentacao no e fora do domicilio, por forma
de aquisicao (monetaria, doada pelo governo, doada por outros, producao propria e outras nao monetarias), despesa
corrente, rendimento de programas sociais (Bolsa Familia/Auxilio Brasil, BPC, auxilio-gas, outros) e auxilio-alimentacao.

Uso: python3 -I base_familias.py <Dados_20261127.zip> <Tradutor_Alimentacao.xls> <Tradutor_Despesa_Geral.xls> <pasta_cache>
Grava <pasta_cache>/base_uc.pkl e imprime a conferencia com as tabelas publicadas.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from leitura import CHAVE_UC, ler, valor_mensal  # noqa: E402

SM_2025 = 1518.0
NAO_MORADOR_PC = {17, 18, 19}

# estratos "Municipio da Capital" (arquivo "Estratos POF 2024 2025.xlsx" da documentacao)
_CAPITAL = {11: (1101, 1102), 12: (1201, 1201), 13: (1301, 1306), 14: (1401, 1402), 15: (1501, 1503), 16: (1601, 1602),
            17: (1701, 1701), 21: (2101, 2103), 22: (2201, 2203), 23: (2301, 2306), 24: (2401, 2402), 25: (2501, 2503),
            26: (2601, 2603), 27: (2701, 2703), 28: (2801, 2802), 29: (2901, 2906), 31: (3101, 3106), 32: (3201, 3202),
            33: (3301, 3309), 35: (3501, 3509), 41: (4101, 4105), 42: (4201, 4202), 43: (4301, 4306), 50: (5001, 5003),
            51: (5101, 5102), 52: (5201, 5203), 53: (5301, 5306)}
REGIAO = {1: 'N', 2: 'NE', 3: 'SE', 4: 'S', 5: 'CO'}

CATS = {
    'sexo': ['Homem', 'Mulher'],
    'idade_ref': ['Até 29 anos', '30 a 44 anos', '45 a 59 anos', '60 anos ou mais'],
    'crianca5': ['Sem criança <5', 'Com criança <5'],
    'idoso60': ['Sem idoso ≥60', 'Com idoso ≥60'],
    'tam_dom': ['1 pessoa', '2–3 pessoas', '4–5 pessoas', '6+ pessoas'],
    'sit_dom': ['Urbano', 'Rural'],
    'capital': ['Interior / RM', 'Capital estadual'],
    'faixa_renda': ['Até 1/4 SM', '1/4 a 1/2 SM', '1/2 a 1 SM', '1 a 2 SM', '2 a 3 SM', '3 a 5 SM', 'Mais de 5 SM',
                    'Sem rendimento / ignorado'],
    'ocupacao': ['Empregado do setor privado (com ou sem carteira)', 'Trabalhador doméstico', 'Setor público (inclui militar)',
                 'Empregador', 'Conta própria', 'Outros (sem trabalho no período ou não remunerado)'],
}

# codigos (6 digitos) de rendimento de programas sociais e auxilio-alimentacao, do "Cadastro de Produtos"
PROG = {'bolsa_familia': {505001, 508008},          # Bolsa Familia e Auxilio Brasil; abono natalino do Bolsa Familia
        'bpc': {505002, 508009},                    # BPC-LOAS (e auxilio a portadores de deficiencia); abono natalino do BPC
        'aux_gas': {505003},
        'aux_alimentacao': {503001}}                # auxilio/tiquete/cartao alimentacao (do trabalho)


def _categoria(x, cortes, rotulos):
    return pd.Categorical(pd.cut(x, cortes, right=False, labels=False).map(dict(enumerate(rotulos))), categories=rotulos)


def montar(zip_dados, trad_alim, trad_desp, cache):
    mor = ler('MORADOR', zip_dados, cache)
    uc = mor.drop_duplicates(CHAVE_UC)[['UF', 'ESTRATO_POF', 'TIPO_SITUACAO_REG'] + CHAVE_UC + ['PESO', 'PESO_FINAL', 'RENDA_TOTAL']].copy()
    pessoas = mor[~mor['V010106'].isin(NAO_MORADOR_PC)]
    g = pessoas.groupby(CHAVE_UC)
    comp = pd.DataFrame({'n_moradores': g.size(), 'n_criancas5': g['V010303'].apply(lambda a: int((a < 5).sum())),
                         'n_idosos60': g['V010303'].apply(lambda a: int((a >= 60).sum()))}).reset_index()
    ref = mor[mor['V010106'] == 1][CHAVE_UC + ['COD_INFORMANTE', 'V010303', 'V010304']].rename(
        columns={'COD_INFORMANTE': 'inf_ref', 'V010303': 'idade_ref_anos', 'V010304': 'sexo_ref'})
    uc = uc.merge(comp, on=CHAVE_UC, how='left').merge(ref, on=CHAVE_UC, how='left')
    n_dom = mor.drop_duplicates(CHAVE_UC).groupby(['COD_UPA', 'NUM_DOM']).size().rename('n_uc_no_domicilio').reset_index()
    uc = uc.merge(n_dom, on=['COD_UPA', 'NUM_DOM'], how='left')

    # territorio
    uc['regiao'] = (uc['UF'] // 10).map(REGIAO)
    lo = uc['UF'].map(lambda u: _CAPITAL[u][0]); hi = uc['UF'].map(lambda u: _CAPITAL[u][1])
    uc['capital_bin'] = ((uc['ESTRATO_POF'] >= lo) & (uc['ESTRATO_POF'] <= hi)).astype(int)

    # trabalho principal da pessoa de referencia (o de mais meses no periodo; empate, o de maior valor)
    rt = ler('RENDIMENTO_TRABALHO', zip_dados, cache)
    rt = rt[rt['SUB_QUADRO'].str.strip() == 'A'].merge(ref[CHAVE_UC + ['inf_ref']], on=CHAVE_UC)
    rt = rt[rt['COD_INFORMANTE'] == rt['inf_ref']].sort_values(['V9011', 'V8500_DEFLA'], ascending=False)
    pos = rt.drop_duplicates(CHAVE_UC)[CHAVE_UC + ['V050203']].rename(columns={'V050203': 'pos_ocup_ref'})
    uc = uc.merge(pos, on=CHAVE_UC, how='left')

    # fatores com os rotulos do painel
    uc['sexo'] = pd.Categorical(uc['sexo_ref'].map({1: 'Homem', 2: 'Mulher'}), categories=CATS['sexo'])
    uc['idade_ref'] = _categoria(uc['idade_ref_anos'], [0, 30, 45, 60, 999], CATS['idade_ref'])
    uc['crianca5'] = pd.Categorical(np.where(uc['n_criancas5'] > 0, CATS['crianca5'][1], CATS['crianca5'][0]), categories=CATS['crianca5'])
    uc['idoso60'] = pd.Categorical(np.where(uc['n_idosos60'] > 0, CATS['idoso60'][1], CATS['idoso60'][0]), categories=CATS['idoso60'])
    uc['tam_dom'] = _categoria(uc['n_moradores'], [1, 2, 4, 6, 999], CATS['tam_dom'])
    uc['sit_dom'] = pd.Categorical(uc['TIPO_SITUACAO_REG'].map({1: 'Urbano', 2: 'Rural'}), categories=CATS['sit_dom'])
    uc['capital'] = pd.Categorical(uc['capital_bin'].map({0: CATS['capital'][0], 1: CATS['capital'][1]}), categories=CATS['capital'])
    uc['renda_pc'] = uc['RENDA_TOTAL'] / uc['n_moradores']
    uc['renda_pc_sm'] = uc['renda_pc'] / SM_2025
    fr = pd.cut(uc['renda_pc_sm'], [0, .25, .5, 1, 2, 3, 5, np.inf], right=True, labels=False)
    uc['faixa_renda'] = pd.Categorical(np.where(uc['RENDA_TOTAL'] > 0, fr.map(dict(enumerate(CATS['faixa_renda'][:7]))), CATS['faixa_renda'][7]),
                                       categories=CATS['faixa_renda'])
    mapa_oc = {3: 0, 1: 1, 2: 2, 4: 2, 5: 3, 6: 4, 7: 5}
    uc['ocupacao'] = pd.Categorical(uc['pos_ocup_ref'].map(mapa_oc).fillna(5).astype(int).map(dict(enumerate(CATS['ocupacao']))),
                                    categories=CATS['ocupacao'])

    # despesas: alimentacao (no/fora do domicilio, por forma de aquisicao) e despesa corrente
    ta = pd.read_excel(trad_alim)[['CODIGO', 'NIVEL_1']].drop_duplicates('CODIGO')
    td = pd.read_excel(trad_desp)
    # cada registro pode ter mais de um valor (V8000, INSS, previdencia, IR, ISS, deducoes); o tradutor de despesa
    # diz, pela coluna VARIAVEL, qual valor conta para cada codigo (como na memoria de calculo da Tabela de Despesa Geral)
    partes = []
    for arq in ('ALUGUEL_ESTIMADO', 'DESPESA_COLETIVA', 'CADERNETA_COLETIVA', 'DESPESA_INDIVIDUAL'):
        d = ler(arq, zip_dados, cache)
        v = d['V8000_DEFLA'] * d['V9011'] * d['FATOR_ANUALIZACAO'] / 12 if arq == 'ALUGUEL_ESTIMADO' else valor_mensal(d, arq)
        partes.append(pd.DataFrame({**{k: d[k] for k in CHAVE_UC + ['V9001', 'V9002']}, 'VARIAVEL': 'v8000', 'valor': v}))
        if arq == 'DESPESA_COLETIVA':
            partes.append(pd.DataFrame({**{k: d[k] for k in CHAVE_UC + ['V9001', 'V9002']}, 'VARIAVEL': 'v020904',
                                        'valor': d['V020904_DEFLA'] * d['V9011'] * d['FATOR_ANUALIZACAO'] / 12}))
    rt_ = ler('RENDIMENTO_TRABALHO', zip_dados, cache)
    for var, col in (('v05021212', 'V05021212_DEFLA'), ('v05021222', 'V05021222_DEFLA'), ('v05021232', 'V05021232_DEFLA')):
        partes.append(pd.DataFrame({**{k: rt_[k] for k in CHAVE_UC + ['V9001']}, 'V9002': np.nan, 'VARIAVEL': var,
                                    'valor': rt_[col] * rt_['V9011'] * rt_['FATOR_ANUALIZACAO'] / 12}))
    or_ = ler('OUTROS_RENDIMENTOS', zip_dados, cache)
    m3 = or_['QUADRO'].isin([3, 5, 6, 7])
    partes.append(pd.DataFrame({**{k: or_[k] for k in CHAVE_UC + ['V9001']}, 'V9002': np.nan, 'VARIAVEL': 'v8501',
                                'valor': or_['V8501_DEFLA'] * or_['FATOR_ANUALIZACAO'] * or_['V9011'].where(m3, 1) / 12}))
    desp = pd.concat(partes, ignore_index=True).dropna(subset=['valor'])
    desp['CODIGO'] = desp['V9001'] // 100
    al = desp[desp['VARIAVEL'] == 'v8000'].merge(ta, on='CODIGO', how='inner')
    al['forma'] = pd.cut(al['V9002'], [0, 6, 7, 8, 10, 11, 99], labels=['monetaria', 'doada_governo', 'doada_outros', 'outra_nao_monet', 'producao_propria', 'outra_nao_monet2'])
    al['forma'] = al['forma'].astype(str).replace({'outra_nao_monet2': 'outra_nao_monet'})
    piv = al.pivot_table(index=CHAVE_UC, columns='NIVEL_1', values='valor', aggfunc='sum').rename(columns={1: 'alim_dom', 2: 'alim_fora'})
    piv2 = al[al['NIVEL_1'] == 1].pivot_table(index=CHAVE_UC, columns='forma', values='valor', aggfunc='sum').add_prefix('alim_dom_')
    # despesa corrente: NIVEL_1 = 1 ("Despesas Correntes") do tradutor de despesa geral, casando codigo e variavel
    # O tradutor oficial repete em duas linhas identicas 10 codigos de deducoes do quadro 7 de outros rendimentos
    # (507001 a 507010); como o programa do IBGE junta pelo codigo, essas deducoes entram duas vezes na despesa
    # corrente publicada. `despesa_corrente` replica a tabela publicada; `despesa_corrente_sem_dupl` conta uma vez.
    td_ = td[['CODIGO', 'VARIAVEL', 'NIVEL_1']].assign(VARIAVEL=td['VARIAVEL'].astype(str).str.strip().str.lower())
    dc1 = desp.merge(td_[td_['NIVEL_1'] == 1].drop_duplicates(), on=['CODIGO', 'VARIAVEL'], how='inner').groupby(CHAVE_UC)['valor'].sum().rename('despesa_corrente_sem_dupl')
    dc = desp.merge(td_[td_['NIVEL_1'] == 1], on=['CODIGO', 'VARIAVEL'], how='inner').groupby(CHAVE_UC)['valor'].sum().rename('despesa_corrente')
    uc = uc.merge(dc1.reset_index(), on=CHAVE_UC, how='left').merge(piv.reset_index(), on=CHAVE_UC, how='left').merge(piv2.reset_index(), on=CHAVE_UC, how='left').merge(dc.reset_index(), on=CHAVE_UC, how='left')
    for c in [c for c in uc.columns if c.startswith('alim_') or c.startswith('despesa_corrente')]:
        uc[c] = uc[c].fillna(0.0)
    uc['alim_total'] = uc['alim_dom'] + uc['alim_fora']

    # rendimentos de programas sociais e auxilio-alimentacao
    orr = ler('OUTROS_RENDIMENTOS', zip_dados, cache)
    orr = orr.assign(valor=valor_mensal(orr, 'OUTROS_RENDIMENTOS'), CODIGO=orr['V9001'] // 100)
    for k, cods_ in PROG.items():
        s_ = orr[orr['CODIGO'].isin(cods_)].groupby(CHAVE_UC)['valor'].sum().rename('rend_' + k)
        uc = uc.merge(s_.reset_index(), on=CHAVE_UC, how='left')
        uc['rend_' + k] = uc['rend_' + k].fillna(0.0)
        uc['recebe_' + k] = (uc['rend_' + k] > 0).astype(int)

    # pesos de replicacao (bootstrap) por domicilio
    rep = ler('PESOS_REPLICACAO', zip_dados, cache)
    uc = uc.merge(rep, on=['COD_UPA', 'NUM_DOM'], how='left')
    return uc


def conferir(uc, tab_alvo):
    w = uc['PESO_FINAL']
    r = {'familias': w.sum(), 'tamanho_medio': (uc['n_moradores'] * w).sum() / w.sum(),
         'renda_media_com_var_patrimonial': (uc['RENDA_TOTAL'] * w).sum() / w.sum(),
         'alim_total_media': (uc['alim_total'] * w).sum() / w.sum(),
         'despesa_corrente_media': (uc['despesa_corrente'] * w).sum() / w.sum(),
         'despesa_corrente_sem_dupl_media': (uc['despesa_corrente_sem_dupl'] * w).sum() / w.sum(),
         'sem_peso_replicacao': int(uc['REP_POF_1'].isna().sum()),
         'sem_pessoa_referencia': int(uc['sexo'].isna().sum())}
    print('\nConferencia com a POF 2024-2025 publicada (Tabelas 1.1.1 e 2.1.1, Brasil):')
    for k, v in r.items():
        alvo = tab_alvo.get(k)
        print(f'  {k:34s} {v:16,.2f}' + (f'   publicado {alvo:16,.2f}   dif {v - alvo:+,.2f}' if alvo is not None else ''))
    print('\nDistribuicao ponderada das familias por fator (%):')
    for f in CATS:
        d = uc.groupby(f, observed=False)['PESO_FINAL'].sum() / w.sum() * 100
        n = uc.groupby(f, observed=False).size()
        print('  ' + f + ': ' + '; '.join(f'{c} {d[c]:.1f}% (n={n[c]})' for c in CATS[f]))
    return r


if __name__ == '__main__':
    zip_dados, trad_alim, trad_desp, cache = sys.argv[1:5]
    uc = montar(zip_dados, trad_alim, trad_desp, cache)
    uc.to_pickle(os.path.join(cache, 'base_uc.pkl'))
    print('UCs:', len(uc), '| colunas:', uc.shape[1])
    conferir(uc, {'familias': 79561637, 'tamanho_medio': 2.67, 'renda_media_com_var_patrimonial': 9240.04,
                  'alim_total_media': 1113.00, 'despesa_corrente_media': 7331.88})
