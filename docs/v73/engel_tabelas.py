"""Extrai o coeficiente de Engel das tabelas publicadas pelo IBGE (POF 2017-2018 e 2024-2025).

Definicoes (as mesmas da v72 do painel, conferidas contra ENGEL_BR de 2017-2018):
  alim_total = Despesas com alimentacao (Tab. 1.1.7 ou 1.3.UF.3)
  alim_dom / alim_fora = Alimentacao no / fora do domicilio (mesma tabela)
  despesa = Despesas correntes (Tab. 1.1.1 ou 1.3.UF.1)
  renda = Rendimento total, sem a variacao patrimonial (Tab. 2.1.1 ou 2.3.UF.1)
  engel_desp = alim_total / despesa; engel_renda = alim_total / renda; pct_fora = alim_fora / alim_total
Uso: python3 -I engel_tabelas.py <pasta_2017_2018> <pasta_2024_2025> <saida.json>
"""
import glob, json, sys, warnings
import pandas as pd

warnings.filterwarnings('ignore')
P18, P25, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def linha(df, rotulo):
    for r in df.itertuples(index=False):
        if pd.notna(r[0]) and str(r[0]).strip() == rotulo:
            v = [float(str(c).replace(',', '.')) for c in r[1:] if pd.notna(c) and str(c).strip() not in ('',)]
            return v[:8]   # total + 7 classes
    raise KeyError(rotulo)


def faixas(df):
    for r in df.itertuples(index=False):
        if pd.notna(r[0]) and str(r[0]).strip() in ('DESPESA',):
            return [' '.join(str(c).split()) for c in r[1:] if pd.notna(c)][:8]
    return None


def engel(f_desp, s_desp, f_alim, s_alim, f_rend, s_rend):
    d = pd.read_excel(f_desp, sheet_name=s_desp, header=None)
    a = pd.read_excel(f_alim, sheet_name=s_alim, header=None)
    r = pd.read_excel(f_rend, sheet_name=s_rend, header=None)
    desp = linha(d, 'Despesas correntes')
    at = linha(a, 'Despesas com alimentação')
    ad = linha(a, 'Alimentação no domicílio')
    af = linha(a, 'Alimentação fora do domicílio')
    rd = linha(r, 'Rendimento total')
    nf = linha(d, 'Número de famílias')
    out = []
    for i in range(8):
        out.append({'alim_dom': ad[i], 'alim_fora': af[i], 'alim_total': at[i], 'despesa': desp[i], 'renda': rd[i],
                    'familias': nf[i],
                    'engel_desp': round(100 * at[i] / desp[i], 1), 'engel_renda': round(100 * at[i] / rd[i], 1),
                    'pct_fora': round(100 * af[i] / at[i], 1)})
    return {'cabecalho': faixas(d), 'total': out[0], 'classes': out[1:]}


g = lambda p, pat: glob.glob(p + '/' + pat)[0]
sheet = lambda f, prefix: [s for s in pd.ExcelFile(f).sheet_names if s.strip() == prefix][0]

res = {}
# 2017-2018
f1, f7, f2 = g(P18, 'Tab 1.1.1 *'), g(P18, 'Tab 1.1.7*'), g(P18, 'Tab 2.1.1 *')
res['2018_BR'] = engel(f1, sheet(f1, '1.1.1'), f7, sheet(f7, '1.1.7'), f2, sheet(f2, '2.1.1'))
rj = g(P18, '33RJ*')
res['2018_RJ'] = engel(rj, sheet(rj, '1.3.19.1'), rj, sheet(rj, '1.3.19.3'), rj, sheet(rj, '2.3.19.1'))
# 2024-2025
f1, f7, f2 = g(P25, 'Tab 1.1.1 *'), g(P25, 'Tab 1.1.7*'), g(P25, 'Tab 2.1.1 *')
res['2025_BR'] = engel(f1, sheet(f1, '1.1.1'), f7, sheet(f7, '1.1.7'), f2, sheet(f2, '2.1.1'))
rj = g(P25, 'Tab UF 33*')
res['2025_RJ'] = engel(rj, sheet(rj, '1.3.33.1'), rj, sheet(rj, '1.3.33.3'), rj, sheet(rj, '2.3.33.1'))

json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
for k, v in res.items():
    print('==', k, v['cabecalho'])
    print('  total', {x: v['total'][x] for x in ('alim_total', 'despesa', 'renda', 'engel_desp', 'engel_renda', 'pct_fora')})
    for c in v['classes']:
        print('  ', c['alim_dom'], c['alim_fora'], c['alim_total'], c['despesa'], c['renda'], '|', c['engel_desp'], c['engel_renda'], c['pct_fora'], '| fam', int(c['familias']))
