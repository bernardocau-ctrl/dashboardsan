"""Triagem das informacoes novas que a POF 2024-2025 ja permite, sem EBIA (liberacao de 27/11/2026).

Calcula, para o Brasil e com IC95% pelos pesos de replicacao:
  A. Coeficiente de Engel (% da despesa corrente) e % da alimentacao feita fora do domicilio pelos 9 fatores do painel
  B. Programas sociais: % de familias que recebem Bolsa Familia (inclui Auxilio Brasil) e BPC, por fator; Engel de quem
     recebe e de quem nao recebe Bolsa Familia
  C. Aquisicao nao monetaria de alimentos para o domicilio: parcela do valor que foi doada pelo governo, doada por
     outros ou de producao propria, por faixa de renda per capita e por situacao do domicilio
  D. Coeficiente de Engel por UF e Grande Regiao (conferido contra as tabelas publicadas por UF)
  E. Gasto mensal per capita com alimentacao por faixa de renda per capita
Uso: python3 -I explorar.py <base_uc.pkl> <saida.json>
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estimativas import diferenca, estimar, por_grupo  # noqa: E402
from base_familias import CATS  # noqa: E402

warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)
np.seterr(invalid='ignore', divide='ignore')   # grupos minusculos (4 familias sem rendimento) dao divisao por zero nas replicas
uc = pd.read_pickle(sys.argv[1])
OUT = sys.argv[2]
FATORES = ['sexo', 'idade_ref', 'crianca5', 'idoso60', 'tam_dom', 'sit_dom', 'capital', 'faixa_renda', 'ocupacao']
UF_SIG = {11: 'RO', 12: 'AC', 13: 'AM', 14: 'RR', 15: 'PA', 16: 'AP', 17: 'TO', 21: 'MA', 22: 'PI', 23: 'CE', 24: 'RN', 25: 'PB',
          26: 'PE', 27: 'AL', 28: 'SE', 29: 'BA', 31: 'MG', 32: 'ES', 33: 'RJ', 35: 'SP', 41: 'PR', 42: 'SC', 43: 'RS', 50: 'MS',
          51: 'MT', 52: 'GO', 53: 'DF'}

# variaveis derivadas
for k in ('doada_governo', 'doada_outros', 'producao_propria', 'outra_nao_monet', 'monetaria'):
    c = 'alim_dom_' + k
    if c not in uc:
        uc[c] = 0.0
uc['alim_dom_nao_monet'] = uc['alim_dom_doada_governo'] + uc['alim_dom_doada_outros'] + uc['alim_dom_producao_propria'] + uc['alim_dom_outra_nao_monet']
uc['tem_doacao_alim'] = ((uc['alim_dom_doada_governo'] + uc['alim_dom_doada_outros']) > 0).astype(int)
uc['tem_doacao_gov'] = (uc['alim_dom_doada_governo'] > 0).astype(int)
uc['tem_prod_propria'] = (uc['alim_dom_producao_propria'] > 0).astype(int)
uc['bf'] = pd.Categorical(np.where(uc['recebe_bolsa_familia'] == 1, 'Recebe Bolsa Família', 'Não recebe'),
                          categories=['Não recebe', 'Recebe Bolsa Família'])
uc['uf'] = uc['UF'].map(UF_SIG)
uc['alim_pc'] = uc['alim_total'] / uc['n_moradores']

res = {'A_engel_por_fator': {}, 'A_fora_por_fator': {}, 'B_bolsa_familia_por_fator': {}, 'B_bpc_por_fator': {}}
for f in FATORES:
    res['A_engel_por_fator'][f] = por_grupo(uc, f, 'razao', 'alim_total', 'despesa_corrente')
    res['A_fora_por_fator'][f] = por_grupo(uc, f, 'razao', 'alim_fora', 'alim_total')
    res['B_bolsa_familia_por_fator'][f] = por_grupo(uc, f, 'prop', 'recebe_bolsa_familia')
    res['B_bpc_por_fator'][f] = por_grupo(uc, f, 'prop', 'recebe_bpc')
res['B_engel_bf'] = por_grupo(uc, 'bf', 'razao', 'alim_total', 'despesa_corrente')
res['B_engel_bf_dif'] = diferenca(uc, 'bf', 'Não recebe', 'Recebe Bolsa Família', 'razao', 'alim_total', 'despesa_corrente')
bfsub = uc[uc['recebe_bolsa_familia'] == 1]
res['B_bf_parcela_da_renda'] = estimar(bfsub, 'razao', 'rend_bolsa_familia', 'RENDA_TOTAL')
res['B_bf_valor_medio'] = estimar(bfsub, 'media', 'rend_bolsa_familia')
res['B_bf_por_uf'] = por_grupo(uc, 'uf', 'prop', 'recebe_bolsa_familia')
res['C_nao_monet_por_renda'] = por_grupo(uc, 'faixa_renda', 'razao', 'alim_dom_nao_monet', 'alim_dom')
res['C_nao_monet_por_situacao'] = por_grupo(uc, 'sit_dom', 'razao', 'alim_dom_nao_monet', 'alim_dom')
res['C_doacao_gov_por_renda'] = por_grupo(uc, 'faixa_renda', 'razao', 'alim_dom_doada_governo', 'alim_dom')
res['C_doacao_outros_por_renda'] = por_grupo(uc, 'faixa_renda', 'razao', 'alim_dom_doada_outros', 'alim_dom')
res['C_prod_propria_por_situacao'] = por_grupo(uc, 'sit_dom', 'razao', 'alim_dom_producao_propria', 'alim_dom')
res['C_familias_com_doacao_por_renda'] = por_grupo(uc, 'faixa_renda', 'prop', 'tem_doacao_alim')
res['C_familias_prod_propria_por_situacao'] = por_grupo(uc, 'sit_dom', 'prop', 'tem_prod_propria')
res['D_engel_por_uf'] = por_grupo(uc, 'uf', 'razao', 'alim_total', 'despesa_corrente')
res['D_engel_por_regiao'] = por_grupo(uc, 'regiao', 'razao', 'alim_total', 'despesa_corrente')
res['E_alim_pc_por_renda'] = por_grupo(uc, 'faixa_renda', 'media', 'alim_pc')
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1, allow_nan=False)


def mostra(titulo, L, un='%'):
    print('\n' + titulo)
    for r in L:
        cv = f" cv {r['cv']:.1f}%" if r.get('cv') else ''
        icx = f"IC95% {r['ic95'][0]:7.1f} a {r['ic95'][1]:7.1f}" if r['ep'] is not None else 'IC95% indisponível (grupo pequeno)'
        print(f"   {r['grupo'][:48]:48s} {r['est']:9.1f}{un}  {icx}  n={r['n']}{cv}")


for f in FATORES:
    mostra('A. Engel (% despesa corrente) por ' + f, res['A_engel_por_fator'][f])
mostra('A. % fora do domicilio por faixa de renda', res['A_fora_por_fator']['faixa_renda'])
for f in ['faixa_renda', 'sexo', 'crianca5', 'sit_dom', 'idade_ref']:
    mostra('B. % familias com Bolsa Familia por ' + f, res['B_bolsa_familia_por_fator'][f])
mostra('B. Engel por recebimento de Bolsa Familia', res['B_engel_bf'])
print('   diferenca:', res['B_engel_bf_dif'])
print('   BF: parcela da renda das familias que recebem', res['B_bf_parcela_da_renda']['est'], '| valor medio R$', res['B_bf_valor_medio']['est'])
mostra('C. % do valor da alimentacao no domicilio que e nao monetario, por renda', res['C_nao_monet_por_renda'])
mostra('C. idem por situacao', res['C_nao_monet_por_situacao'])
mostra('C. % doado pelo governo, por renda', res['C_doacao_gov_por_renda'])
mostra('C. % doado por outros, por renda', res['C_doacao_outros_por_renda'])
mostra('C. % producao propria, por situacao', res['C_prod_propria_por_situacao'])
mostra('C. % familias que receberam alimento doado, por renda', res['C_familias_com_doacao_por_renda'])
mostra('C. % familias com producao propria, por situacao', res['C_familias_prod_propria_por_situacao'])
mostra('D. Engel por regiao', res['D_engel_por_regiao'])
mostra('D. Engel por UF', res['D_engel_por_uf'])
mostra('E. Gasto mensal per capita com alimentacao (R$) por renda', res['E_alim_pc_por_renda'], un='')
