"""Conferencia independente: despesa com alimentacao por classe de rendimento, POF 2024-2025, a partir dos microdados.

Segue a memoria de calculo do IBGE ("Memoria de calculo - Tabela de Alimentacao.R"):
  valor mensal = V8000_DEFLA * FATOR_ANUALIZACAO / 12 (despesa individual: quadros 23, 25, 28-31 e 33 tambem * V9011)
  codigo do produto com 6 digitos -> Tradutor_Alimentacao (NIVEL_1 = 1 no domicilio, 2 fora)
  media por unidade de consumo (familia), ponderada por PESO_FINAL
Classe de rendimento: RENDA_TOTAL da UC (rendimento total + variacao patrimonial), cortes de 2, 3, 6, 10, 15 e 25 salarios
minimos de R$ 1.518 (os mesmos limites das tabelas publicadas).
Uso: python3 -I engel_microdados.py <Dados.zip> <Tradutor_Alimentacao.xls> <saida.json>
"""
import json, sys, zipfile
import numpy as np, pandas as pd

ZIPF, TRAD, OUT = sys.argv[1:4]
z = zipfile.ZipFile(ZIPF)


def fwf(nome, widths, names, usecols):
    return pd.read_fwf(z.open(nome), widths=widths, names=names, usecols=usecols, header=None, dtype=str)


mor = fwf('MORADOR.txt', [2, 4, 1, 9, 2, 1, 2, 2, 1, 3, 1, 14, 14, 10],
          ['UF', 'ESTRATO_POF', 'SIT', 'COD_UPA', 'NUM_DOM', 'NUM_UC', 'COD_INFORMANTE', 'V010106', 'V010301', 'V010303',
           'V010304', 'PESO', 'PESO_FINAL', 'RENDA_TOTAL'],
          ['UF', 'COD_UPA', 'NUM_DOM', 'NUM_UC', 'PESO_FINAL', 'RENDA_TOTAL'])
uc = mor.drop_duplicates(['COD_UPA', 'NUM_DOM', 'NUM_UC']).copy()
for c in ('PESO_FINAL', 'RENDA_TOTAL'):
    uc[c] = uc[c].astype(float)
uc['UF'] = uc['UF'].astype(int)

cad = fwf('CADERNETA_COLETIVA.txt', [2, 4, 1, 9, 2, 1, 2, 3, 2, 8, 2, 10, 12, 10, 1, 2, 14, 14, 10],
          ['UF', 'ESTRATO_POF', 'SIT', 'COD_UPA', 'NUM_DOM', 'NUM_UC', 'QUADRO', 'SEQ', 'SEQ_PAI', 'V9001', 'V9002', 'V8000',
           'DEFLATOR', 'V8000_DEFLA', 'COD_IMPUT_VALOR', 'FATOR_ANUALIZACAO', 'PESO', 'PESO_FINAL', 'RENDA_TOTAL'],
          ['COD_UPA', 'NUM_DOM', 'NUM_UC', 'V9001', 'V8000_DEFLA', 'FATOR_ANUALIZACAO'])
cad['valor'] = cad['V8000_DEFLA'].astype(float) * cad['FATOR_ANUALIZACAO'].astype(float) / 12

ind = fwf('DESPESA_INDIVIDUAL.txt', [2, 4, 1, 9, 2, 1, 2, 2, 2, 8, 2, 10, 2, 2, 12, 10, 1, 2, 14, 14, 10, 1],
          ['UF', 'ESTRATO_POF', 'SIT', 'COD_UPA', 'NUM_DOM', 'NUM_UC', 'COD_INFORMANTE', 'QUADRO', 'SEQ', 'V9001', 'V9002',
           'V8000', 'V9010', 'V9011', 'DEFLATOR', 'V8000_DEFLA', 'COD_IMPUT_VALOR', 'FATOR_ANUALIZACAO', 'PESO',
           'PESO_FINAL', 'RENDA_TOTAL', 'V9012'],
          ['COD_UPA', 'NUM_DOM', 'NUM_UC', 'QUADRO', 'V9001', 'V9011', 'V8000_DEFLA', 'FATOR_ANUALIZACAO'])
mens = ind['QUADRO'].astype(int).isin([23, 25, 28, 29, 30, 31, 33])
v11 = pd.to_numeric(ind['V9011'], errors='coerce')
ind['valor'] = ind['V8000_DEFLA'].astype(float) * ind['FATOR_ANUALIZACAO'].astype(float) / 12
ind.loc[mens, 'valor'] = ind.loc[mens, 'valor'] * v11[mens]

desp = pd.concat([cad[['COD_UPA', 'NUM_DOM', 'NUM_UC', 'V9001', 'valor']],
                  ind[['COD_UPA', 'NUM_DOM', 'NUM_UC', 'V9001', 'valor']]])
desp['CODIGO'] = desp['V9001'].astype(int) // 100

trad = pd.read_excel(TRAD)[['CODIGO', 'NIVEL_1']].drop_duplicates()
desp = desp.merge(trad, on='CODIGO', how='inner')
porUC = desp.pivot_table(index=['COD_UPA', 'NUM_DOM', 'NUM_UC'], columns='NIVEL_1', values='valor', aggfunc='sum').fillna(0)
porUC.columns = ['dom' if c == 1 else 'fora' for c in porUC.columns]
base = uc.merge(porUC.reset_index(), on=['COD_UPA', 'NUM_DOM', 'NUM_UC'], how='left').fillna({'dom': 0, 'fora': 0})

SM = 1518
cortes = [-np.inf] + [k * SM for k in (2, 3, 6, 10, 15, 25)] + [np.inf]
base['classe'] = pd.cut(base['RENDA_TOTAL'], cortes, right=True, labels=False)


def medias(b):
    w = b['PESO_FINAL']
    out = []
    for k in range(7):
        m = b['classe'] == k
        out.append({'alim_dom': round(float((b.loc[m, 'dom'] * w[m]).sum() / w[m].sum()), 2),
                    'alim_fora': round(float((b.loc[m, 'fora'] * w[m]).sum() / w[m].sum()), 2),
                    'familias': round(float(w[m].sum())), 'n_amostra': int(m.sum())})
    return out


res = {'BR': medias(base), 'RJ': medias(base[base['UF'] == 33]),
       'n_uc': int(len(base)), 'n_uc_rj': int((base['UF'] == 33).sum())}
json.dump(res, open(OUT, 'w'), indent=1)
for k in ('BR', 'RJ'):
    print('==', k)
    for c in res[k]:
        print('  ', c)
print('UCs na amostra:', res['n_uc'], '| RJ:', res['n_uc_rj'])
