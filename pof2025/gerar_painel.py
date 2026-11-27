"""Gera os dados das informacoes novas da POF 2024-2025 para o painel (v74).

Para cada indicador, estima o valor no Brasil, nas 27 UFs, nas 5 Grandes Regioes e nas categorias dos 9 fatores do
painel, com IC95% pelos 200 pesos de replicacao (mesma formula de estimativas.py). Celulas com menos de 30 familias na
amostra ficam vazias; celulas com menos de 150 familias ou coeficiente de variacao acima de 15% levam aviso de cautela.

Uso: python3 -I gerar_painel.py <Dados_20261127.zip> <pasta_cache> <pasta_tradutores> <pasta_tabelas_2017_2018> <saida.json>
  pasta_cache: a mesma de base_familias.py (precisa de base_uc.pkl)
  pasta_tradutores: onde estao Tradutor_Alimentacao.xls e Tradutor_Despesa_Geral.xls
  pasta_tabelas_2017_2018: tabelas por UF da POF 2017-2018 (11RO.xls.xlsx etc.), para a comparacao do Engel por UF
"""
import glob
import json
import os
import re
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_familias import CATS  # noqa: E402
from estimativas import DIVISOR, REPS  # noqa: E402
from leitura import CHAVE_UC, ler, valor_mensal  # noqa: E402

warnings.filterwarnings('ignore')
np.seterr(invalid='ignore', divide='ignore')
ZIP, CACHE, TRAD, T18, OUT = sys.argv[1:6]

UF_SIG = {11: 'RO', 12: 'AC', 13: 'AM', 14: 'RR', 15: 'PA', 16: 'AP', 17: 'TO', 21: 'MA', 22: 'PI', 23: 'CE', 24: 'RN', 25: 'PB',
          26: 'PE', 27: 'AL', 28: 'SE', 29: 'BA', 31: 'MG', 32: 'ES', 33: 'RJ', 35: 'SP', 41: 'PR', 42: 'SC', 43: 'RS', 50: 'MS',
          51: 'MT', 52: 'GO', 53: 'DF'}
REG_NOME = {'N': 'Norte', 'NE': 'Nordeste', 'SE': 'Sudeste', 'S': 'Sul', 'CO': 'Centro-Oeste'}
FATORES = ['sexo', 'idade_ref', 'crianca5', 'idoso60', 'tam_dom', 'sit_dom', 'capital', 'faixa_renda', 'ocupacao']
ROT_FATOR = {'sexo': 'Sexo da pessoa de referência', 'idade_ref': 'Idade da pessoa de referência', 'crianca5': 'Criança menor de 5 anos',
             'idoso60': 'Idoso de 60 anos ou mais', 'tam_dom': 'Tamanho da família', 'sit_dom': 'Urbano ou rural',
             'capital': 'Capital ou interior', 'faixa_renda': 'Rendimento per capita', 'ocupacao': 'Posição na ocupação (pessoa de referência)'}
N_MIN, N_CAUT, CV_CAUT = 30, 150, 15.0

uc = pd.read_pickle(os.path.join(CACHE, 'base_uc.pkl'))
uc = uc.copy()

# ── variaveis adicionais a partir dos registros de despesa ──────────────────────────────────────────────
ta = pd.read_excel(glob.glob(os.path.join(TRAD, 'Tradutor_Alimenta*.xls'))[0])
td = pd.read_excel(os.path.join(TRAD, 'Tradutor_Despesa_Geral.xls'))
ind_nomes = pd.read_excel(glob.glob(os.path.join(TRAD, 'R', 'Indice_Alimentacao.xls'))[0])
NOME_NIVEL = dict(zip(ind_nomes['NIVEL'], ind_nomes['DESCRICAO']))
reg = []
for arq in ('CADERNETA_COLETIVA', 'DESPESA_INDIVIDUAL', 'DESPESA_COLETIVA'):
    d = ler(arq, ZIP, CACHE)
    reg.append(pd.DataFrame({**{k: d[k] for k in CHAVE_UC}, 'V9001': d['V9001'], 'V9002': d['V9002'], 'valor': valor_mensal(d, arq), 'arq': arq}))
reg = pd.concat(reg, ignore_index=True).dropna(subset=['valor'])
reg['CODIGO'] = reg['V9001'] // 100
alim = reg[reg['arq'] != 'DESPESA_COLETIVA'].merge(ta[['CODIGO', 'NIVEL_1', 'NIVEL_2', 'NIVEL_3']].drop_duplicates('CODIGO'), on='CODIGO')
grp = alim[alim['NIVEL_1'] == 1].pivot_table(index=CHAVE_UC, columns='NIVEL_2', values='valor', aggfunc='sum').fillna(0)
GRUPOS = [int(c) for c in grp.columns]
grp.columns = [f'g{int(c)}' for c in grp.columns]
sub = alim[(alim['NIVEL_1'] == 1) & alim['NIVEL_3'].notna()].pivot_table(index=CHAVE_UC, columns='NIVEL_3', values='valor', aggfunc='sum').fillna(0)
SUBGRUPOS = sorted(int(c) for c in sub.columns)
sub.columns = [f's{int(c)}' for c in sub.columns]
grp = grp.join(sub, how='outer').fillna(0)
cod_gas = set(td.loc[td['DESCRICAO_5'].astype(str).str.strip().str.lower() == 'gas domestico', 'CODIGO'])
extras = pd.DataFrame({
    'gas': reg[reg['CODIGO'].isin(cod_gas) & (reg['arq'] == 'DESPESA_COLETIVA')].groupby(CHAVE_UC)['valor'].sum(),
    'cesta_basica': reg[reg['CODIGO'] == 390005].groupby(CHAVE_UC)['valor'].sum(),
    'alim_escolar': reg[reg['CODIGO'] == 430065].groupby(CHAVE_UC)['valor'].sum(),
    'desc_cesta': reg[reg['CODIGO'] == 433019].groupby(CHAVE_UC)['valor'].sum(),
})
uc = uc.merge(grp.reset_index(), on=CHAVE_UC, how='left').merge(extras.reset_index(), on=CHAVE_UC, how='left')
for c in list(grp.columns) + list(extras.columns):
    uc[c] = uc[c].fillna(0.0)
for k in ('doada_governo', 'doada_outros', 'producao_propria', 'outra_nao_monet'):
    if 'alim_dom_' + k not in uc:
        uc['alim_dom_' + k] = 0.0
uc['alim_dom_nao_monet'] = uc[['alim_dom_doada_governo', 'alim_dom_doada_outros', 'alim_dom_producao_propria', 'alim_dom_outra_nao_monet']].sum(1)
uc['alim_dom_doada'] = uc['alim_dom_doada_governo'] + uc['alim_dom_doada_outros']
uc['tem_doacao'] = (uc['alim_dom_doada'] > 0).astype(float)
uc['tem_prod_propria'] = (uc['alim_dom_producao_propria'] > 0).astype(float)
uc['tem_cesta'] = (uc['cesta_basica'] > 0).astype(float)
uc['tem_alim_escolar'] = (uc['alim_escolar'] > 0).astype(float)
uc['tem_desc_cesta'] = (uc['desc_cesta'] > 0).astype(float)
uc['um'] = 1.0
uc['uf'] = uc['UF'].map(UF_SIG)
uc['regiao_nome'] = uc['regiao'].map(REG_NOME)
uc['bf'] = uc['recebe_bolsa_familia'].astype(float)

# ── estimador vetorizado: somas por grupo para os 201 pesos de uma vez ──────────────────────────────────
W = uc[['PESO_FINAL'] + REPS].to_numpy(dtype=float)          # n x 201


def somas(x, grupos):
    """Somas ponderadas de x por grupo (k x 201)."""
    xw = W * uc[x].to_numpy(dtype=float)[:, None] if isinstance(x, str) else W * x[:, None]
    codes, cats = pd.factorize(grupos, sort=False)
    out = np.zeros((len(cats), W.shape[1]))
    ok = codes >= 0
    np.add.at(out, codes[ok], xw[ok])
    return out, list(cats)


def estimar_por(num, den, recorte, fator=100.0, universo=None):
    """Razao sum(w*num)/sum(w*den) por categoria do recorte, com IC95% bootstrap. Devolve {categoria: celula}."""
    g = pd.Series('Brasil', index=uc.index) if recorte == 'total' else uc[recorte].astype(object)
    if universo is not None:
        g = g.where(uc[universo] > 0)
    g = g.where(g.notna(), None).to_numpy()
    N, cats = somas(num, g)
    D, _ = somas(den, g)
    n = pd.Series(g).value_counts()
    res = {}
    for i, c in enumerate(cats):
        if c is None:
            continue
        nn = int(n.get(c, 0))
        if nn < N_MIN:
            res[str(c)] = None
            continue
        t = N[i] / D[i] * fator
        est = float(t[0])
        ep = float(np.sqrt(((t[1:] - est) ** 2).sum() / DIVISOR))
        cv = 100 * ep / est if est else None
        caut = 1 if (nn < N_CAUT or (cv is not None and cv > CV_CAUT)) else 0
        res[str(c)] = [round(est, 2), round(max(est - 1.96 * ep, 0.0) if est >= 0 else est - 1.96 * ep, 2), round(est + 1.96 * ep, 2), nn, round(cv, 1) if cv is not None else None, caut]
    return res


def indicador(id_, familia, secao, rot, curto, unid, desc, num, den, fator=100.0, universo=None, cautela='', nd=1):
    dados = {'total': estimar_por(num, den, 'total', fator, universo), 'uf': estimar_por(num, den, 'uf', fator, universo),
             'regiao': estimar_por(num, den, 'regiao_nome', fator, universo)}
    for f in FATORES:
        dados[f] = estimar_por(num, den, f, fator, universo)
    print(f'  {id_:24s} Brasil {dados["total"]["Brasil"]}')
    return {'id': id_, 'familia': familia, 'secao': secao, 'rot': rot, 'curto': curto, 'unid': unid, 'nd': nd, 'desc': desc,
            'cautela': cautela, 'universo': universo, 'dados': dados}


IND = []
E = 'engel'
A = 'acesso'
print('Indicadores:')
IND.append(indicador('engel_desp', E, 'Orçamento', 'Coeficiente de Engel: alimentação em % da despesa corrente', 'Engel (% da despesa)', '%',
                     'Despesa com alimentação (no e fora do domicílio) dividida pela despesa corrente, as mesmas definições da aba.', 'alim_total', 'despesa_corrente'))
IND.append(indicador('pct_fora', E, 'Orçamento', 'Alimentação fora do domicílio, em % da despesa com alimentação', '% fora do domicílio', '%',
                     'Parte da despesa com alimentação feita fora de casa (restaurantes, lanches, refeições no trabalho e na escola pagas).', 'alim_fora', 'alim_total'))
IND.append(indicador('alim_pc', E, 'Orçamento', 'Despesa mensal com alimentação por pessoa (R$)', 'Gasto por pessoa (R$)', 'R$',
                     'Despesa mensal com alimentação no e fora do domicílio dividida pelo número de moradores (valores de 2024-2025).', 'alim_total', 'n_moradores', fator=1.0, nd=2,
                     cautela='Descreve gasto, não quantidade nem qualidade da alimentação.'))
IND.append(indicador('gas_desp', E, 'Orçamento', 'Gás de cozinha, em % da despesa corrente', 'Gás (% da despesa)', '%',
                     'Despesa com gás de botijão e gás encanado dividida pela despesa corrente.', 'gas', 'despesa_corrente', nd=2,
                     cautela='O gás é usado no preparo dos alimentos, mas também no aquecimento de água; o indicador não separa os usos.'))
CAUT_PROG = 'O recebimento é declarado pela família e pode estar subdeclarado em relação aos registros administrativos do programa.'
IND.append(indicador('bf', A, 'Transferências de renda', 'Famílias que recebem Bolsa Família (%)', 'Bolsa Família (% das famílias)', '%',
                     'Famílias em que algum morador declarou rendimento do Bolsa Família ou do Auxílio Brasil no período da pesquisa.', 'bf', 'um', cautela=CAUT_PROG))
IND.append(indicador('bf_renda', A, 'Transferências de renda', 'Bolsa Família em % do rendimento total, nas famílias que recebem', 'Bolsa Família (% da renda de quem recebe)', '%',
                     'Rendimento do Bolsa Família dividido pelo rendimento total (com variação patrimonial), só nas famílias que recebem.', 'rend_bolsa_familia', 'RENDA_TOTAL',
                     universo='recebe_bolsa_familia', cautela=CAUT_PROG))
IND.append(indicador('bf_engel', A, 'Transferências de renda', 'Coeficiente de Engel das famílias que recebem Bolsa Família', 'Engel de quem recebe Bolsa Família', '%',
                     'Despesa com alimentação em % da despesa corrente, só nas famílias que recebem Bolsa Família.', 'alim_total', 'despesa_corrente',
                     universo='recebe_bolsa_familia', cautela='Descreve o orçamento de quem recebe; não é efeito do programa.'))
IND.append(indicador('bpc', A, 'Transferências de renda', 'Famílias que recebem BPC (%)', 'BPC (% das famílias)', '%',
                     'Famílias em que algum morador declarou receber o Benefício de Prestação Continuada (idosos e pessoas com deficiência de baixa renda).', 'recebe_bpc', 'um', cautela=CAUT_PROG))
IND.append(indicador('aux_gas', A, 'Transferências de renda', 'Famílias que recebem auxílio-gás (%)', 'Auxílio-gás (% das famílias)', '%',
                     'Famílias em que algum morador declarou receber o auxílio-gás.', 'recebe_aux_gas', 'um', cautela=CAUT_PROG))
IND.append(indicador('aux_alim', A, 'Transferências de renda', 'Famílias com auxílio-alimentação do trabalho (%)', 'Vale-alimentação (% das famílias)', '%',
                     'Famílias em que algum morador recebe auxílio, tíquete ou cartão alimentação do empregador.', 'recebe_aux_alimentacao', 'um'))
IND.append(indicador('nao_monet', A, 'Forma de aquisição', 'Alimentos obtidos sem compra, em % do valor da alimentação no domicílio', 'Não monetário (% do valor)', '%',
                     'Valor dos alimentos para casa obtidos por doação, produção própria, troca, retirada do negócio ou outra forma sem pagamento, em % do valor total.',
                     'alim_dom_nao_monet', 'alim_dom', cautela='O valor dos alimentos não comprados é estimado pelo informante ou pelo IBGE.'))
IND.append(indicador('prod_propria', A, 'Forma de aquisição', 'Produção própria, em % do valor da alimentação no domicílio', 'Produção própria (% do valor)', '%',
                     'Valor dos alimentos de produção própria em % do valor da alimentação no domicílio.', 'alim_dom_producao_propria', 'alim_dom', nd=2))
IND.append(indicador('doado', A, 'Forma de aquisição', 'Alimentos doados, em % do valor da alimentação no domicílio', 'Doados (% do valor)', '%',
                     'Valor dos alimentos doados pelo governo ou por outros (familiares, vizinhos, instituições) em % do valor da alimentação no domicílio.',
                     'alim_dom_doada', 'alim_dom', nd=2))
IND.append(indicador('fam_doacao', A, 'Forma de aquisição', 'Famílias que receberam alimento doado (%)', 'Receberam doação (% das famílias)', '%',
                     'Famílias que registraram ao menos um alimento doado (pelo governo ou por outros) no período da caderneta.', 'tem_doacao', 'um',
                     cautela='A caderneta cobre 7 dias; doações menos frequentes podem não aparecer.'))
IND.append(indicador('fam_prod', A, 'Forma de aquisição', 'Famílias com alimento de produção própria (%)', 'Produção própria (% das famílias)', '%',
                     'Famílias que registraram ao menos um alimento de produção própria.', 'tem_prod_propria', 'um',
                     cautela='A caderneta cobre 7 dias; produção sazonal pode não aparecer.'))
IND.append(indicador('fam_cesta', A, 'Forma de aquisição', 'Famílias que adquiriram cesta básica (%)', 'Cesta básica (% das famílias)', '%',
                     'Famílias que registraram a aquisição de cesta básica (comprada, doada ou recebida) no período da caderneta.', 'tem_cesta', 'um', nd=2,
                     cautela='A caderneta cobre 7 dias; aquisições mensais podem não aparecer.'))
IND.append(indicador('fam_escolar', A, 'Forma de aquisição', 'Famílias com despesa com alimentação escolar (%)', 'Alimentação escolar paga (% das famílias)', '%',
                     'Famílias com despesa declarada com alimentação escolar (paga pela família; não inclui a merenda gratuita).', 'tem_alim_escolar', 'um', nd=2))
IND.append(indicador('val_escolar', A, 'Forma de aquisição', 'Despesa mensal com alimentação escolar, nas famílias que têm essa despesa (R$)', 'Alimentação escolar paga (R$ por mês)', 'R$',
                     'Despesa mensal média com alimentação escolar (paga pela família), só nas famílias que declararam essa despesa.', 'alim_escolar', 'um', fator=1.0, nd=2,
                     universo='tem_alim_escolar', cautela='Não inclui a alimentação escolar gratuita.'))
IND.append(indicador('val_cesta', A, 'Forma de aquisição', 'Despesa mensal média com cesta básica, por família (R$, todas as famílias)', 'Cesta básica (R$ por mês, média de todas as famílias)', 'R$',
                     'Valor mensal das cestas básicas registradas na caderneta (compradas, doadas ou recebidas), em média por família, contando as que não adquiriram.',
                     'cesta_basica', 'um', fator=1.0, nd=2,
                     cautela='A caderneta cobre 7 dias e o IBGE converte essa semana em valor mensal; por isso o valor só é válido como média de todas as famílias, não como gasto de quem comprou. Poucas famílias registraram cesta básica: a estimativa é imprecisa.'))
IND.append(indicador('fam_desc_cesta', A, 'Forma de aquisição', 'Famílias com desconto de cesta básica no salário (%)', 'Desconto de cesta básica (% das famílias)', '%',
                     'Famílias em que algum morador declarou desconto de cesta básica no salário (cesta fornecida pelo empregador e descontada da remuneração).',
                     'tem_desc_cesta', 'um', nd=2, cautela='Despesa rara na amostra; a estimativa é imprecisa e, por recorte, quase sempre fica suprimida ou com aviso.'))
for gcod in GRUPOS:
    nome = str(NOME_NIVEL.get(gcod, gcod))
    IND.append(indicador(f'g{gcod}', 'composicao', 'Composição do gasto no domicílio', f'{nome}, em % da despesa com alimentação no domicílio', nome, '%',
                         f'Despesa com o grupo "{nome}" (classificação do IBGE na tabela de alimentação) em % da despesa com alimentação no domicílio.',
                         f'g{gcod}', 'alim_dom', nd=1, cautela='Participação no gasto, não na quantidade adquirida nem no consumo.'))

for scod in SUBGRUPOS:
    nome, pai = str(NOME_NIVEL.get(scod, scod)), str(NOME_NIVEL.get(scod // 10, scod // 10))
    rot = nome if nome.lower() not in ('outros', 'outras', 'orgânicos', 'light e diet') else f'{nome} ({pai.lower()})'
    IND.append(indicador(f's{scod}', 'composicao_sub', 'Subgrupos: ' + pai, f'{rot}, em % da despesa com alimentação no domicílio', rot, '%',
                         f'Despesa com "{rot}" (subgrupo de "{pai}" na tabela de alimentação do IBGE) em % da despesa com alimentação no domicílio.',
                         f's{scod}', 'alim_dom', nd=2, cautela='Participação no gasto, não na quantidade adquirida nem no consumo.'))

# ── Engel e % fora por UF na POF 2017-2018 (tabelas publicadas, sem IC) ──────────────────────────────────


def linha(df, rotulo):
    for r in df.itertuples(index=False):
        if pd.notna(r[0]) and str(r[0]).strip() == rotulo:
            return float(r[1])


uf2018 = {}
for f in glob.glob(os.path.join(T18, '[0-9][0-9][A-Z][A-Z].xls*')):
    sig = re.search(r'(\d\d)([A-Z]{2})', os.path.basename(f)).group(2)
    x = pd.read_excel(f, sheet_name=None, header=None)
    s1 = [s for s in x if s.strip().endswith('.1') and s.strip().startswith('1.3')][0]
    s3 = [s for s in x if s.strip().endswith('.3') and s.strip().startswith('1.3')][0]
    at, af, dc = linha(x[s3], 'Despesas com alimentação'), linha(x[s3], 'Alimentação fora do domicílio'), linha(x[s1], 'Despesas correntes')
    uf2018[sig] = {'engel_desp': round(100 * at / dc, 2), 'pct_fora': round(100 * af / at, 2)}
print('UFs 2017-2018:', len(uf2018), '| RJ', uf2018.get('RJ'))

RECORTES = [{'id': 'uf', 'rot': 'Unidade da Federação'}, {'id': 'regiao', 'rot': 'Grande Região', 'cats': list(REG_NOME.values())}] + \
           [{'id': f, 'rot': ROT_FATOR[f], 'cats': CATS[f]} for f in FATORES]
out = {'gerado': '27/11/2026, pof2025/gerar_painel.py, microdados da POF 2024-2025 de 27/11/2026',
       'regras': {'n_min': N_MIN, 'n_cautela': N_CAUT, 'cv_cautela': CV_CAUT,
                  'celula': '[estimativa, ic95_inf, ic95_sup, n_familias_amostra, cv_pct, cautela]'},
       'recortes': RECORTES, 'ind': IND, 'uf2018': uf2018}
json.dump(out, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'), allow_nan=False)
print('gravado', OUT, os.path.getsize(OUT), 'bytes;', len(IND), 'indicadores')
