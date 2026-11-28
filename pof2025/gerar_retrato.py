"""Gera retrato/moedas.html ("Cem moedas"), a reportagem do Retrato com a POF 2024-2025.

Injeta no modelo (pof2025/moedas_modelo.html) os dados ja conferidos:
  docs/v73/engel_tabelas.json         Engel por faixa de rendimento (tabelas publicadas do IBGE)
  pof2025/resultados/painel_v75.json  indicadores por UF e por fator (microdados, IC95%)
Os numeros escritos no texto do modelo sao conferidos contra esses dados no fim (conferir()).
Uso: python3 -I gerar_retrato.py   (a partir da raiz do repositorio)
"""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(RAIZ, 'docs/v73/engel_tabelas.json'), encoding='utf-8'))
P = json.load(open(os.path.join(RAIZ, 'pof2025/resultados/painel_v75.json'), encoding='utf-8'))
I = {i['id']: i for i in P['ind']}


def c(ind, rec, cat):
    return I[ind]['dados'][rec][cat]


UFN = {'AC': 'Acre', 'AL': 'Alagoas', 'AM': 'Amazonas', 'AP': 'Amapá', 'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal',
       'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão', 'MG': 'Minas Gerais', 'MS': 'Mato Grosso do Sul', 'MT': 'Mato Grosso',
       'PA': 'Pará', 'PB': 'Paraíba', 'PE': 'Pernambuco', 'PI': 'Piauí', 'PR': 'Paraná', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
       'RO': 'Rondônia', 'RR': 'Roraima', 'RS': 'Rio Grande do Sul', 'SC': 'Santa Catarina', 'SE': 'Sergipe', 'SP': 'São Paulo', 'TO': 'Tocantins'}
FX = ['até R$ 3.036', 'R$ 3.036 a 4.554', 'R$ 4.554 a 9.108', 'R$ 9.108 a 15.180', 'R$ 15.180 a 22.770', 'R$ 22.770 a 37.950', 'mais de R$ 37.950']
SM = ['até 2 SM', '2 a 3 SM', '3 a 6 SM', '6 a 10 SM', '10 a 15 SM', '15 a 25 SM', 'mais de 25 SM']
D = {
    'br': {'engel': c('engel_desp', 'total', 'Brasil'), 'engel18': T['2018_BR']['total']['engel_desp'], 'alim': T['2025_BR']['total']['alim_total'],
           'fora': c('pct_fora', 'total', 'Brasil'), 'pc': c('alim_pc', 'total', 'Brasil')},
    'faixas': [{'fx': FX[k], 'sm': SM[k], 'engel': x['engel_desp'], 'alim': x['alim_total'], 'fora': x['pct_fora']} for k, x in enumerate(T['2025_BR']['classes'])],
    'uf': {u: {'nome': UFN[u], 'e': c('engel_desp', 'uf', u), 'e18': P['uf2018'][u]['engel_desp'], 'bf': c('bf', 'uf', u)} for u in UFN},
    'grupos': sorted([[i['curto'], i['dados']['total']['Brasil'][0]] for i in P['ind'] if i['familia'] == 'composicao'], key=lambda g: -g[1]),
    'arroz': {k: {'arroz': c('s1011', 'faixa_renda', k), 'feijao': c('s1012', 'faixa_renda', k), 'refri': c('s1122', 'faixa_renda', k)}
              for k in ('Até 1/4 SM', 'Mais de 5 SM')},
    'sem': {k: {'total': c('nao_monet', 'sit_dom', k), 'prod': c('prod_propria', 'sit_dom', k), 'doado': c('doado', 'sit_dom', k),
                'fam_prod': c('fam_prod', 'sit_dom', k)} for k in ('Urbano', 'Rural')},
    'bf': {'total': c('bf', 'total', 'Brasil'), 'crianca': c('bf', 'crianca5', 'Com criança <5'), 'renda': c('bf', 'faixa_renda', '1/4 a 1/2 SM'),
           'parte_renda': c('bf_renda', 'total', 'Brasil'), 'engel_bf': c('bf_engel', 'total', 'Brasil')},
    'regiao': {k: v for k, v in I['engel_desp']['dados']['regiao'].items()},
}
modelo = open(os.path.join(RAIZ, 'pof2025/moedas_modelo.html'), encoding='utf-8').read()
html = modelo.replace('__DADOS__', json.dumps(D, ensure_ascii=False, separators=(',', ':')))
open(os.path.join(RAIZ, 'retrato/moedas.html'), 'w', encoding='utf-8').write(html)


def conferir():
    """Confere numeros escritos no texto contra os dados (arredondamento indicado em cada par)."""
    f1 = lambda v: f'{(v[0] if isinstance(v, list) else v):.1f}'.replace('.', ',')   # celulas do painel sao [est, ic_inf, ic_sup, ...]
    esperados = [f1(D['br']['engel']), f1(D['br']['engel18']), f1(D['uf']['AM']['e']), f1(D['uf']['AM']['e18']), f1(D['uf']['RN']['e']),
                 f1(D['uf']['RN']['e18']), f1(D['uf']['DF']['e']), f1(D['regiao']['Norte'][0]), f1(D['regiao']['Centro-Oeste'][0]),
                 f1(D['sem']['Rural']['total'][0]), f1(D['sem']['Rural']['prod'][0]), f1(D['sem']['Rural']['doado'][0]),
                 f1(D['arroz']['Até 1/4 SM']['arroz'][0]), f1(D['arroz']['Até 1/4 SM']['feijao'][0]),
                 f1(D['arroz']['Mais de 5 SM']['arroz'][0]), f1(D['arroz']['Mais de 5 SM']['feijao'][0])]
    texto = re.sub(r'<script>.*?</script>', '', html, flags=re.S)
    faltam = [e for e in esperados if e not in texto]
    print('numeros conferidos no texto:', len(esperados) - len(faltam), 'de', len(esperados), '| ausentes:', faltam)


conferir()
print('gravado retrato/moedas.html', len(html), 'bytes')
