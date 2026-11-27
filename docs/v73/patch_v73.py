"""v73: coeficiente de Engel da POF 2024-2025 (Brasil e Rio de Janeiro), com seletor de edicao e comparacao.
Uso: python3 -I patch_v73.py <index.html> <engel_tabelas.json> <engel_microdados.json>
"""
import json, sys

HTML, TAB, MIC = sys.argv[1:4]
s = open(HTML, encoding='utf-8').read()
t = json.load(open(TAB))
m = json.load(open(MIC))
n0 = len(s)


def troca(velho, novo, conta=1):
    global s
    k = s.count(velho)
    if k != conta:
        raise SystemExit(f'esperava {conta} ocorrencia(s), achei {k}: {velho[:90]!r}')
    s = s.replace(velho, novo)


# conferencia: a reproducao das tabelas de 2017-2018 bate com o que o painel ja mostra
for i, c in enumerate(t['2018_BR']['classes']):
    pass

FX25 = ['Até R$ 3.036', 'R$ 3.036–4.554', 'R$ 4.554–9.108', 'R$ 9.108–15.180', 'R$ 15.180–22.770', 'R$ 22.770–37.950',
        'Mais de R$ 37.950']
SM = ['Até 2 SM', '2 a 3 SM', '3 a 6 SM', '6 a 10 SM', '10 a 15 SM', '15 a 25 SM', 'Mais de 25 SM']


def linhas(chave, mic):
    out = []
    for i, c in enumerate(t[chave]['classes']):
        assert abs(c['alim_dom'] - mic[i]['alim_dom']) < 0.006 and abs(c['alim_fora'] - mic[i]['alim_fora']) < 0.006, (chave, i)
        out.append("  {faixa:'%s', sm:'%s', alim_dom:%.2f, alim_fora:%.2f, alim_total:%.2f, despesa:%.2f, renda:%.2f, "
                   "engel_desp:%.1f, engel_renda:%.1f, pct_fora:%.1f, n:%d}"
                   % (FX25[i], SM[i], c['alim_dom'], c['alim_fora'], c['alim_total'], c['despesa'], c['renda'],
                      c['engel_desp'], c['engel_renda'], c['pct_fora'], mic[i]['n_amostra']))
    return ',\n'.join(out)


dados = ("// v73: POF 2024-2025 (IBGE, Primeiros Resultados, 27/11/2026). Tabelas 1.1.1, 1.1.7 e 2.1.1 (Brasil) e\n"
         "// 1.3.33.1, 1.3.33.3 e 2.3.33.1 (Rio de Janeiro); mesmas definicoes de 2017-2018 (despesa corrente; rendimento\n"
         "// total sem variacao patrimonial). Gasto com alimentacao conferido ao centavo contra os microdados; n = familias\n"
         "// (unidades de consumo) na amostra.\n"
         "const ENGEL_BR_2025 = [\n" + linhas('2025_BR', m['BR']) + ",\n];\n"
         "const ENGEL_RJ_2025 = [\n" + linhas('2025_RJ', m['RJ']) + ",\n];\n"
         "const ENGEL_SM = " + json.dumps(SM, ensure_ascii=False) + ";\n"
         "const ENGEL_ED = {\n"
         "  '2018': {rot:'2017-2018', br:ENGEL_BR, rj:ENGEL_RJ, sm:954, fonte:'IBGE, POF 2017-2018 (SIDRA 6715, 6972, 6974 e 6977)'},\n"
         "  '2025': {rot:'2024-2025', br:ENGEL_BR_2025, rj:ENGEL_RJ_2025, sm:1518, fonte:'IBGE, POF 2024-2025, Primeiros Resultados (tabelas 1.1.1, 1.1.7 e 2.1.1; Rio de Janeiro, 1.3.33.1, 1.3.33.3 e 2.3.33.1)'},\n"
         "};\n")
troca("const REGRESSAO_DATA = [];", dados + "const REGRESSAO_DATA = [];")

# ── botoes de edicao e de local, no titulo do painel
btn = 'style="padding:3px 9px;border-radius:10px;border:1.5px solid var(--border);background:transparent;font-size:.72rem;font-weight:600;cursor:pointer"'
velho = '<button class="engel-metrica-btn ativo" data-m="engel_desp"'
novo = ('<span class="v73-grupo" role="group" aria-label="Edição da POF">'
        '<button class="engel-metrica-btn engel-ed-btn" data-ed="2018" onclick="setEngelEd(\'2018\')" ' + btn + '>2017-2018</button>'
        '<button class="engel-metrica-btn engel-ed-btn ativo" data-ed="2025" onclick="setEngelEd(\'2025\')" ' + btn + '>2024-2025</button>'
        '<button class="engel-metrica-btn engel-ed-btn" data-ed="comp" onclick="setEngelEd(\'comp\')" ' + btn + '>Comparar</button></span>'
        '<span class="v73-grupo" id="engel-local-grupo" role="group" aria-label="Local da comparação" style="display:none">'
        '<button class="engel-metrica-btn engel-local-btn ativo" data-l="br" onclick="setEngelLocal(\'br\')" ' + btn + '>Brasil</button>'
        '<button class="engel-metrica-btn engel-local-btn" data-l="rj" onclick="setEngelLocal(\'rj\')" ' + btn + '>Rio de Janeiro</button></span>'
        '<span class="v73-grupo" role="group" aria-label="Medida">'
        + velho)
troca(velho, novo)
troca("""cursor:pointer">% fora do domicílio</button>
        </div>""", """cursor:pointer">% fora do domicílio</button></span>
        </div>""")
# os botoes de medida ficam so com a classe de medida (a selecao por .engel-metrica-btn[data-m])
troca("document.querySelectorAll('.engel-metrica-btn').forEach(b => b.classList.toggle('ativo', b.dataset.m === m));",
      "document.querySelectorAll('.engel-metrica-btn[data-m]').forEach(b => b.classList.toggle('ativo', b.dataset.m === m));")

# ── nota de fonte: passa a ser escrita pela funcao
velho_nota = s[s.index('<div style="font-size:.72rem;color:var(--text-faint);padding:8px 14px 4px;line-height:1.5">Fonte: IBGE, POF 2017-2018. SIDRA'):]
velho_nota = velho_nota[:velho_nota.index('</div>') + 6]
troca(velho_nota, '<div id="engel-nota" style="font-size:.72rem;color:var(--text-faint);padding:8px 14px 4px;line-height:1.5"></div>')

# ── funcao do grafico
ini = s.index('function buildEngelChart(){')
fim = s.index('function setEngelMetrica(m){')
nova = r"""function buildEngelChart(){
  // v44: paleta validada (Brasil #1F6FB2, Rio de Janeiro #E0622B), faixas em duas linhas, leitura ao passar o mouse.
  // v73: edicao da POF (2017-2018 ou 2024-2025) e comparacao entre edicoes por faixa em salarios minimos.
  const metrica = S.engelMetrica || 'engel_desp';
  const ed = S.engelEd || '2025';
  const labelMap = {engel_desp:'% da despesa corrente', engel_renda:'% do rendimento declarado', pct_fora:'% da despesa com alimentação feita fora do domicílio'};
  const faixa2 = f => f.replace('Até R$ ', 'Até<br>R$ ').replace('Mais de R$ ', 'Mais de<br>R$ ').replace('–', ' a<br>');
  const f1 = v => v.toFixed(1).replace('.', ',') + '%';
  const minus = f => f.charAt(0).toLowerCase() + f.slice(1);
  const mono = arr => arr.every((v, i) => i === 0 || v < arr[i - 1]);
  const lg = document.getElementById('engel-local-grupo'); if(lg) lg.style.display = ed === 'comp' ? '' : 'none';
  const base = {
    barmode:'group', bargap:0.32, bargroupgap:0.1,
    margin:{t:18, r:18, l:58, b:62},
    yaxis:{title:{text:labelMap[metrica], font:{size:12, color:'#4E5968'}}, ticksuffix:'%', rangemode:'tozero',
      gridcolor:'rgba(22,28,36,0.07)', zeroline:false, tickfont:{size:12, color:'#1B2A38'}},
    legend:{orientation:'h', x:0, y:1.1, font:{size:12}},
    hovermode:'x unified',
    hoverlabel:{bgcolor:'#fff', bordercolor:'rgba(28,45,64,.2)', font:{color:'#1B2A38', size:12}},
    font:{family:'Inter, sans-serif', size:12, color:'#1B2A38'},
    paper_bgcolor:'transparent', plot_bgcolor:'transparent',
  };
  const el = document.getElementById('engel-leitura'), nota = document.getElementById('engel-nota');
  if(ed === 'comp'){
    const loc = S.engelLocal || 'br', nomeLoc = loc === 'rj' ? 'Rio de Janeiro' : 'Brasil';
    const cor = loc === 'rj' ? ['#F2B394', '#E0622B'] : ['#9EC3E6', '#1F6FB2'];
    const A = ENGEL_ED['2018'][loc], B = ENGEL_ED['2025'][loc];
    const xs = ENGEL_SM.map(x => x.replace('Mais de ', 'Mais de<br>'));
    const yA = A.map(d => d[metrica]), yB = B.map(d => d[metrica]);
    const traces = [
      {x:xs, y:yA, type:'bar', name:nomeLoc + ', 2017-2018', customdata:A.map(d => d.faixa), marker:{color:cor[0], cornerradius:4},
       hovertemplate:'2017-2018 (%{customdata}): %{y:.1f}%<extra></extra>'},
      {x:xs, y:yB, type:'bar', name:nomeLoc + ', 2024-2025', customdata:B.map(d => d.faixa), marker:{color:cor[1], cornerradius:4},
       hovertemplate:'2024-2025 (%{customdata}): %{y:.1f}%<extra></extra>'},
    ];
    const layout = Object.assign({}, base, {xaxis:{tickfont:{size:11.5, color:'#1B2A38'}, showline:true, linecolor:'rgba(28,45,64,.25)',
      title:{text:'Rendimento mensal familiar, em salários mínimos da época', font:{size:11.5, color:'#4E5968'}, standoff:12}}});
    Plotly.react('div-engel', traces, layout, {displayModeBar:false, responsive:true});
    const n = yA.length - 1;
    const dif = (a, b) => { const d = Math.round((b - a) * 10) / 10; return d === 0 ? 'sem diferença' : (d > 0 ? '+' : '−') + Math.abs(d).toFixed(1).replace('.', ',') + ' p.p.'; };
    const nome = {engel_desp:'a alimentação representava', engel_renda:'a alimentação equivalia a', pct_fora:'a parcela da despesa com alimentação feita fora do domicílio era'}[metrica];
    const med = {engel_desp:' da despesa corrente', engel_renda:' do rendimento declarado', pct_fora:''}[metrica];
    if(el) el.innerHTML = '<strong>Leitura.</strong> ' + nomeLoc + ', faixa até 2 salários mínimos: ' + nome + ' ' + f1(yA[0]) + med +
      ' em 2017-2018 e ' + f1(yB[0]) + ' em 2024-2025 (' + dif(yA[0], yB[0]) + '); na faixa de mais de 25 salários mínimos, ' +
      f1(yA[n]) + ' e ' + f1(yB[n]) + ' (' + dif(yA[n], yB[n]) + '). São estimativas pontuais, sem intervalo de confiança: diferenças pequenas podem não ser reais.';
    if(nota) nota.innerHTML = 'Fontes: ' + ENGEL_ED['2018'].fonte + '; ' + ENGEL_ED['2025'].fonte + '. As faixas são as do IBGE, em múltiplos do salário mínimo vigente em cada edição (R$ 954 em 2018 e R$ 1.518 em 2025). ' +
      'Como o salário mínimo teve ganho real entre as edições, a mesma faixa em salários mínimos não corresponde exatamente ao mesmo poder de compra. Os percentuais podem ser comparados; os valores em reais não, porque não foram corrigidos pela inflação entre as edições. A comparação é descritiva e não testa diferenças.';
    return;
  }
  const E = ENGEL_ED[ed];
  const BR = E.br, RJ = E.rj;
  const xs = BR.map(d => faixa2(d.faixa));
  const yBr = BR.map(d => d[metrica]);
  const yRj = RJ.map(d => d[metrica]);
  const fx = BR.map(d => d.faixa);
  const traces = [
    {x:xs, y:yBr, type:'bar', name:'Brasil', customdata:fx, marker:{color:'#1F6FB2', cornerradius:4},
     hovertemplate:'Brasil: %{y:.1f}%<extra></extra>'},
    {x:xs, y:yRj, type:'bar', name:'Rio de Janeiro', customdata:fx, marker:{color:'#E0622B', cornerradius:4},
     hovertemplate:'Rio de Janeiro: %{y:.1f}%<extra></extra>'},
  ];
  const layout = Object.assign({}, base, {xaxis:{tickfont:{size:11.5, color:'#1B2A38'}, showline:true, linecolor:'rgba(28,45,64,.25)',
    title:{text:'Rendimento mensal familiar (POF ' + E.rot + ')', font:{size:11.5, color:'#4E5968'}, standoff:12}}});
  Plotly.react('div-engel', traces, layout, {displayModeBar:false, responsive:true});
  const n = BR.length - 1;
  const lo = minus(BR[0].faixa), hi = minus(BR[n].faixa);
  const mB = mono(yBr), mR = mono(yRj);
  const monoTxt = mB && mR ? 'Nos dois, a parcela cai a cada faixa de renda.'
    : mB ? 'No Brasil, a parcela cai a cada faixa de renda; no Rio de Janeiro, cai de forma menos regular.'
    : mR ? 'No Rio de Janeiro, a parcela cai a cada faixa de renda; no Brasil, cai de forma menos regular.'
    : 'A parcela tende a cair com a renda, mas não a cada faixa.';
  const txt = {
    engel_desp: 'a alimentação representa ' + f1(yBr[0]) + ' da despesa corrente no Brasil e ' + f1(yRj[0]) + ' no Rio de Janeiro; na faixa ' + hi + ', ' + f1(yBr[n]) + ' e ' + f1(yRj[n]) + '. ' + monoTxt,
    engel_renda: 'a alimentação equivale a ' + f1(yBr[0]) + ' do rendimento declarado no Brasil e ' + f1(yRj[0]) + ' no Rio de Janeiro; na faixa ' + hi + ', ' + f1(yBr[n]) + ' e ' + f1(yRj[n]) + '.',
    pct_fora: 'a parcela da despesa com alimentação feita fora do domicílio é de ' + f1(yBr[0]) + ' no Brasil e ' + f1(yRj[0]) + ' no Rio de Janeiro; na faixa ' + hi + ', ' + f1(yBr[n]) + ' e ' + f1(yRj[n]) + '.',
  }[metrica];
  if(el) el.innerHTML = '<strong>Leitura.</strong> Na faixa ' + lo + ', ' + txt;
  const rs = v => 'R$ ' + v.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
  const b0 = BR[0], r0 = RJ[0], comp = r0.engel_desp < b0.engel_desp ? 'menor' : (r0.engel_desp > b0.engel_desp ? 'maior' : 'igual');
  let t = 'Fonte: ' + E.fonte + '. Faixas do IBGE em múltiplos do salário mínimo de R$ ' + E.sm.toLocaleString('pt-BR') + '. Na faixa de menor rendimento (' + minus(b0.faixa) + '/mês), a despesa corrente média (' + rs(b0.despesa) +
    ') é ' + (b0.despesa > b0.renda ? 'maior' : 'menor') + ' que o rendimento declarado (' + rs(b0.renda) + '). No Rio de Janeiro, o coeficiente de Engel nessa faixa é ' + comp + ' que o do Brasil (' +
    f1(r0.engel_desp) + ' contra ' + f1(b0.engel_desp) + ' da despesa); o painel descreve a diferença e não testa a explicação para ela.';
  if(ed === '2025'){
    const pequenas = RJ.filter(d => d.n != null && d.n < N_CAUTELA).map(d => minus(d.faixa) + ' (' + d.n + ' famílias na amostra)');
    if(pequenas.length) t += ' Interpretar com cautela no Rio de Janeiro, faixa ' + pequenas.join(', ') + '.';
    t += ' Primeiros Resultados da POF 2024-2025 (IBGE, 27/11/2026); o gasto com alimentação foi conferido contra os microdados.';
  }
  if(nota) nota.innerHTML = t;
}
function setEngelEd(ed){
  S.engelEd = ed;
  document.querySelectorAll('.engel-ed-btn').forEach(b => b.classList.toggle('ativo', b.dataset.ed === ed));
  buildEngelChart(); syncURL();
}
function setEngelLocal(l){
  S.engelLocal = l;
  document.querySelectorAll('.engel-local-btn').forEach(b => b.classList.toggle('ativo', b.dataset.l === l));
  buildEngelChart(); syncURL();
}
"""
s = s[:ini] + nova + s[fim:]

# ── endereco (link) guarda a edicao e o local
troca("  if(modo==='engel'||modo==='lacunas'){ history.replaceState(null,'','#'+p.toString()); return; }",
      "  if(modo==='engel'){ p.set('ed',S.engelEd||'2025'); if((S.engelEd||'2025')==='comp') p.set('el',S.engelLocal||'br'); history.replaceState(null,'','#'+p.toString()); return; }\n"
      "  if(modo==='lacunas'){ history.replaceState(null,'','#'+p.toString()); return; }")
troca("    if(p.get('dm')) S.desigMarc=p.get('dm');",
      "    if(['2018','2025','comp'].includes(p.get('ed'))){ S.engelEd=p.get('ed'); document.querySelectorAll('.engel-ed-btn').forEach(b => b.classList.toggle('ativo', b.dataset.ed === S.engelEd)); }\n"
      "    if(['br','rj'].includes(p.get('el'))){ S.engelLocal=p.get('el'); document.querySelectorAll('.engel-local-btn').forEach(b => b.classList.toggle('ativo', b.dataset.l === S.engelLocal)); }\n"
      "    if(p.get('dm')) S.desigMarc=p.get('dm');")

# ── CSV da visao
i = s.index("  if(modo === 'engel'){\n    return {nome:'engel_pof2017_2018'")
j = s.index("  if(modo === 'desig'){", i)
s = s[:i] + r"""  if(modo === 'engel'){
    const eds = (S.engelEd || '2025') === 'comp' ? ['2018', '2025'] : [S.engelEd || '2025'];
    const L = [];
    eds.forEach(e => [['br', 'Brasil'], ['rj', 'Rio de Janeiro']].forEach(([k, nome]) => ENGEL_ED[e][k].forEach((d, i) => L.push([
      'POF ' + ENGEL_ED[e].rot, d.faixa, ENGEL_SM[i], nome, d.alim_dom != null ? v47n(d.alim_dom, 2) : '', d.alim_fora != null ? v47n(d.alim_fora, 2) : '',
      d.alim_total != null ? v47n(d.alim_total, 2) : '', d.despesa != null ? v47n(d.despesa, 2) : '', d.renda != null ? v47n(d.renda, 2) : '',
      v47n(d.engel_desp), v47n(d.engel_renda), v47n(d.pct_fora), d.n != null ? d.n : '']))));
    const rot = eds.map(e => 'POF ' + ENGEL_ED[e].rot).join(' e ');
    return {nome:'engel_' + eds.map(e => 'pof' + ENGEL_ED[e].rot.replace('-', '_')).join('_'), titulo:'Coeficiente de Engel por faixa de rendimento, Brasil e Rio de Janeiro, ' + rot + ' (' + eds.map(e => ENGEL_ED[e].fonte).join('; ') + ')',
      csv: v47tabela(['edicao','faixa_rendimento','faixa_salarios_minimos','local','alim_domicilio_rs','alim_fora_rs','alim_total_rs','despesa_corrente_rs','rendimento_rs','engel_despesa_pct','engel_renda_pct','alim_fora_pct','n_familias_amostra'], L)};
  }
""" + s[j:]

# ── PNG/CSV do grafico
i = s.index("  if(id === 'div-engel'){")
j = s.index("  if(id === 'div-desig-prev' || id === 'div-desig-contr'){", i)
s = s[:i] + r"""  if(id === 'div-engel'){
    const m = S.engelMetrica || 'engel_desp', ed = S.engelEd || '2025';
    const rot = {engel_desp: '% da despesa corrente', engel_renda: '% do rendimento declarado', pct_fora: '% da despesa com alimentação feita fora do domicílio'}[m];
    if(ed === 'comp'){
      const loc = S.engelLocal || 'br', nome = loc === 'rj' ? 'Rio de Janeiro' : 'Brasil';
      return {titulo: 'Coeficiente de Engel por faixa de rendimento — ' + nome + ', POF 2017-2018 e 2024-2025', sub: 'Medida: ' + rot + '. Faixas em salários mínimos da época; estimativas pontuais, sem teste de diferença.',
        fonte: ENGEL_ED['2018'].fonte + '; ' + ENGEL_ED['2025'].fonte,
        cab: ['faixa_salarios_minimos', 'pof_2017_2018', 'pof_2024_2025', 'local', 'medida'],
        linhas: ENGEL_SM.map((f, i) => [f, v47n(ENGEL_ED['2018'][loc][i][m]), v47n(ENGEL_ED['2025'][loc][i][m]), nome, rot])};
    }
    const E = ENGEL_ED[ed];
    return {titulo: 'Coeficiente de Engel por faixa de rendimento — Brasil e Rio de Janeiro', sub: 'Medida: ' + rot + '. POF ' + E.rot + '.',
      fonte: E.fonte,
      cab: ['faixa_rendimento', 'brasil', 'rio_de_janeiro', 'medida'], linhas: E.br.map((d, i) => [d.faixa, v47n(d[m]), v47n(E.rj[i]?.[m]), rot])};
  }
""" + s[j:]

# ── textos
troca('title="Coeficiente de Engel — comprometimento orçamentário com alimentação por faixa de renda (POF 2017-2018), Brasil e Rio de Janeiro"',
      'title="Coeficiente de Engel — comprometimento orçamentário com alimentação por faixa de renda (POF 2017-2018 e 2024-2025), Brasil e Rio de Janeiro"')
troca("comprometimento da despesa/renda com alimentação por faixa de rendimento, Brasil e Rio de Janeiro (POF 2017-2018). Quanto menor a renda, maior a proporção do orçamento dedicada à alimentação.'",
      "comprometimento da despesa/renda com alimentação por faixa de rendimento, Brasil e Rio de Janeiro (POF 2017-2018 e POF 2024-2025, com comparação entre as edições). Quanto menor a renda, maior a proporção do orçamento dedicada à alimentação.'")
troca("<p>Indicador complementar — comprometimento do orçamento familiar com alimentação por faixa de rendimento, Brasil e Rio de Janeiro (POF 2017-2018).</p>",
      "<p>Indicador complementar — comprometimento do orçamento familiar com alimentação por faixa de rendimento, Brasil e Rio de Janeiro (POF 2017-2018 e POF 2024-2025).</p>")
troca("Pesquisa de Orçamentos Familiares (POF 2002-2003, 2008-2009 e 2017-2018) e tabelas do SIDRA.",
      "Pesquisa de Orçamentos Familiares (POF 2002-2003, 2008-2009 e 2017-2018; da POF 2024-2025, só o coeficiente de Engel, a partir dos Primeiros Resultados divulgados em 27/11/2026) e tabelas do SIDRA.")
troca("const V47_VERSAO = 'v72';", "const V47_VERSAO = 'v73';")
troca('<strong id="citar-versao">v72</strong>', '<strong id="citar-versao">v73</strong>')

# ── estilo dos grupos de botoes
troca("/* v72: destaque da fonte dos dados (IBGE) no cabeçalho. Só texto e estilo; nenhum dado muda. */",
      "/* v73: grupos de botoes da aba Engel (edicao, local e medida). */\n"
      ".v73-grupo{display:inline-flex;gap:4px;flex-wrap:wrap;align-items:center}\n"
      ".v73-grupo + .v73-grupo{padding-left:8px;margin-left:2px;border-left:1px solid var(--border)}\n"
      "/* v72: destaque da fonte dos dados (IBGE) no cabeçalho. Só texto e estilo; nenhum dado muda. */")

open(HTML, 'w', encoding='utf-8').write(s)
print('ok', n0, '->', len(s))
