"""Confere a composicao do gasto (grupos e subgrupos) do painel com a Tabela 1.1.7 publicada (Brasil, POF 2024-2025).
A tabela segue a ordem do arquivo Indice_Alimentacao.xls (memoria de calculo do IBGE): a linha k da tabela, a partir
de "Despesas com alimentação", corresponde ao NIVEL da linha k do indice.
Uso: python3 -I conferir_composicao.py <painel.json> <Tab 1.1.7 ... .xlsx> <Indice_Alimentacao.xls>
"""
import json
import sys
import warnings

import pandas as pd

warnings.filterwarnings('ignore')
J = json.load(open(sys.argv[1], encoding='utf-8'))
tab = pd.read_excel(sys.argv[2], sheet_name='1.1.7', header=None)
ind = pd.read_excel(sys.argv[3])
ini = tab.index[tab[0].astype(str).str.strip() == 'Despesas com alimentação'][0]
vals = tab.iloc[ini:ini + len(ind), 1].astype(float).to_numpy()
pub = dict(zip(ind['NIVEL'].astype(int), vals))
dom = pub[1]
mx, n = 0.0, 0
for it in J['ind']:
    if it['familia'] not in ('composicao', 'composicao_sub'):
        continue
    nivel = int(it['id'][1:])
    p = 100 * pub[nivel] / dom
    e = it['dados']['total']['Brasil'][0]
    d = abs(e - p)
    mx, n = max(mx, d), n + 1
    if d > 0.01:
        print(f'  diferenca em {it["curto"]}: painel {e:.2f} publicado {p:.2f}')
print(f'{n} grupos e subgrupos conferidos; maior diferenca {mx:.3f} p.p. (arredondamento de 2 casas)')
