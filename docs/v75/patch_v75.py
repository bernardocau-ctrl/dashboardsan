"""v75: subgrupos da composicao do gasto (arroz, feijao, refrigerantes etc.), valor da alimentacao escolar e da cesta
basica, e desconto de cesta basica no salario, na aba Renda e acesso. Troca o bloco de dados V74 pelo novo arquivo.
Uso: python3 -I patch_v75.py <index.html> <painel_v75.json>
"""
import json
import re
import sys

HTML, DADOS = sys.argv[1:3]
s = open(HTML, encoding='utf-8').read()
V = json.load(open(DADOS, encoding='utf-8'))


def troca(velho, novo, conta=1):
    global s
    k = s.count(velho)
    if k != conta:
        raise SystemExit(f'esperava {conta}, achei {k}: {velho[:100]!r}')
    s = s.replace(velho, novo)


m = re.search(r'const V74 = (\{.*?\});\n', s)
if not m:
    raise SystemExit('bloco V74 nao encontrado')
s = s[:m.start(1)] + json.dumps(V, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
troca("acesso: {familias:['acesso', 'composicao'],", "acesso: {familias:['acesso', 'composicao', 'composicao_sub'],")
i = s.index("  acesso:  '<strong>Renda e acesso (POF 2024-2025):</strong>"); j = s.index("',\n", i)
s = s[:i] + "  acesso:  '<strong>Renda e acesso (POF 2024-2025):</strong> transferências de renda, alimentos obtidos sem compra, cesta básica, alimentação escolar e composição do gasto com alimentação, por UF e características das famílias, com IC95%. Não medem insegurança alimentar." + s[j:]
# introducao da aba Engel mais curta (a da v74 nao cabia no cartao de contexto e ficava escondida)
i = s.index("  engel:   '<strong>Orçamento familiar (Coeficiente de Engel):</strong>"); j = s.index("',\n", i)
s = s[:i] + "  engel:   '<strong>Orçamento familiar (Coeficiente de Engel):</strong> parte da despesa e da renda gasta com alimentação, por faixa de rendimento (POF 2017-2018 e 2024-2025) e, abaixo, por UF e características das famílias (2024-2025). Quanto menor a renda, maior essa parte." + s[j:]
troca("const V47_VERSAO = 'v74';", "const V47_VERSAO = 'v75';")
troca('<strong id="citar-versao">v74</strong>', '<strong id="citar-versao">v75</strong>')
open(HTML, 'w', encoding='utf-8').write(s)
print('ok', len(s), len(V['ind']), 'indicadores')
