"""v74: informacoes novas da POF 2024-2025 no painel.
- aba Orcamento familiar: bloco "Por UF e por caracteristicas das familias" (Engel, % fora, gasto por pessoa, gas)
- aba nova "Renda e acesso": transferencias de renda, forma de aquisicao e composicao do gasto com alimentacao
Uso: python3 -I patch_v74.py <index.html> <painel_v74.json>
"""
import json
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


# ── HTML: bloco na aba Engel e painel novo ───────────────────────────────────────────────
troca('<div id="engel-nota" style="font-size:.72rem;color:var(--text-faint);padding:8px 14px 4px;line-height:1.5"></div>',
      '<div id="engel-nota" style="font-size:.72rem;color:var(--text-faint);padding:8px 14px 4px;line-height:1.5"></div>\n'
      '      <div id="v74-engel" class="v74-box"></div>')
troca('    <div id="panel-consumo" class="panel v41-panel" style="display:none">',
      '''    <div id="panel-acesso" class="panel v41-panel" style="display:none">
      <div class="panel-title"><span>Renda, transferências e acesso aos alimentos: Brasil, UFs e características das famílias, POF 2024-2025</span></div>
      <div id="v74-acesso" class="v74-box"></div>
    </div>
    <div id="panel-consumo" class="panel v41-panel" style="display:none">''')
ICONE = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
         'aria-hidden="true" focusable="false"><path d="M3 11h4l3 3h4a2 2 0 0 0 0-4h-3"/><path d="M7 15l-4 0"/><path d="M14 10l5-2a2 2 0 0 1 2 3l-7 5H8"/>'
         '<circle cx="15" cy="5" r="2"/></svg>')
troca('      <button class="tab-modo consumo" id="tab-consumo"',
      '      <button class="tab-modo acesso" id="tab-acesso" onclick="setModo(\'acesso\')" aria-pressed="false" '
      'title="Renda, transferências e acesso aos alimentos (POF 2024-2025): Bolsa Família, BPC, auxílios, alimentos doados e de produção própria e composição do gasto, por UF e características das famílias">'
      + ICONE + '<span>Renda e acesso</span></button>\n      <button class="tab-modo consumo" id="tab-consumo"')

# ── CSS ───────────────────────────────────────────────────────────────────────────────────
troca("/* v73: grupos de botoes da aba Engel (edicao, local e medida). */",
      r"""/* v74: explorador das informacoes novas da POF 2024-2025 */
#panel-engel{ height:auto !important; }
@media (min-width: 961px){ #mode-tabs .tab-modo{ padding-top:7px !important; padding-bottom:7px !important; } }
#mode-tabs .tab-modo.acesso{ color:#5a6472; border-left:3px solid transparent; border-bottom:1px solid rgba(28,45,64,.06); }
#mode-tabs .tab-modo.acesso.ativo{ background:#F3E7D8; color:#7C332C; border-left-color:var(--fao-accent); }
.v74-box{ padding:4px 14px 12px; }
#v74-engel{ border-top:1px solid var(--border); margin-top:10px; padding-top:12px; }
.v74-tit{ font-weight:700; font-size:.86rem; margin:2px 0 8px; color:var(--text); }
.v74-ctrl{ display:flex; gap:8px 14px; align-items:center; flex-wrap:wrap; font-size:.76rem; margin-bottom:6px; }
.v74-ctrl label{ color:var(--text-soft, #4E5968); }
.v74-ctrl select{ font:inherit; font-size:.78rem; padding:4px 6px; border-radius:8px; border:1.5px solid var(--border-strong, #BFC7D1); background:var(--surface, #fff); color:var(--text); max-width:100%; }
.v74-ctrl .v49-exp{ margin-left:auto; }
.v74-graf{ display:grid; grid-template-columns:minmax(0,1fr); gap:10px; }
.v74-graf.com-mapa{ grid-template-columns:minmax(0,1fr) minmax(0,1fr); }
@media (max-width: 900px){ .v74-graf.com-mapa{ grid-template-columns:minmax(0,1fr); } }
.v74-mapa{ height:420px; }
.v74-nota{ font-size:.72rem; color:var(--text-faint); line-height:1.5; margin-top:6px; }
.v74-nota p{ margin:0 0 4px; }
/* v73: grupos de botoes da aba Engel (edicao, local e medida). */""")

# ── JS: dados e componente ───────────────────────────────────────────────────────────────────
JS = r"""
// ════════ v74: informações novas da POF 2024-2025 (Engel por UF e por fator; aba Renda e acesso) ════════
// Dados de pof2025/gerar_painel.py (microdados de 27/11/2026). Célula: [estimativa, ic95_inf, ic95_sup, n, cv, cautela].
const V74 = __DADOS__;
const V74_BOX = {
  engel: {familias:['engel'], ind0:'engel_desp', rec0:'uf', cor:'#1F6FB2', escala:[[0,'#EAF2FA'],[1,'#164B7A']],
          tit:'Por UF e por características das famílias (POF 2024-2025, com IC95%)'},
  acesso: {familias:['acesso', 'composicao'], ind0:'bf', rec0:'faixa_renda', cor:'#2A7F62', escala:[[0,'#E8F4EE'],[1,'#1C5B45']], tit:''},
};
S.v74 = {engel:{ind:'engel_desp', rec:'uf', c18:true}, acesso:{ind:'bf', rec:'faixa_renda', c18:false}};
const V74_FONTE = 'IBGE, microdados da POF 2024-2025 (liberados em 27/11/2026); elaboração própria; IC95% pelos 200 pesos de replicação';
function v74Ind(b){ return V74.ind.find(i => i.id === S.v74[b].ind) || V74.ind.find(i => i.id === V74_BOX[b].ind0); }
function v74Rec(b){ return V74.recortes.find(r => r.id === S.v74[b].rec) || V74.recortes[0]; }
function v74Fmt(v, it){ if(v == null) return '—'; const t = v.toLocaleString('pt-BR', {minimumFractionDigits:it.nd, maximumFractionDigits:it.nd}); return it.unid === 'R$' ? 'R$ ' + t : t + '%'; }
function v74Tem18(b){ const it = v74Ind(b); return b === 'engel' && S.v74[b].rec === 'uf' && (it.id === 'engel_desp' || it.id === 'pct_fora'); }
function v74Linhas(b){
  // categorias na ordem de exibição: [rótulo, chave, célula]
  const it = v74Ind(b), rc = v74Rec(b), D = it.dados[rc.id] || {};
  if(rc.id === 'uf') return Object.keys(UF_META).map(u => [UF_META[u].nome, u, D[u]]).filter(l => l[2]).sort((x, y) => y[2][0] - x[2][0]);
  return (rc.cats || Object.keys(D)).filter(c => D[c]).map(c => [c, c, D[c]]);   // células suprimidas (n < 30) ficam de fora
}
function v74Monta(b){
  const box = document.getElementById('v74-' + b); if(!box || box.dataset.ok) return;
  box.dataset.ok = '1';
  const C = V74_BOX[b], secoes = {};
  V74.ind.filter(i => C.familias.includes(i.familia)).forEach(i => { (secoes[i.secao] = secoes[i.secao] || []).push(i); });
  const opts = Object.keys(secoes).map(sc => '<optgroup label="' + sc + '">' + secoes[sc].map(i => '<option value="' + i.id + '">' + i.curto + '</option>').join('') + '</optgroup>').join('');
  const recs = V74.recortes.map(r => '<option value="' + r.id + '">' + r.rot + '</option>').join('');
  box.innerHTML = (C.tit ? '<div class="v74-tit">' + C.tit + '</div>' : '') +
    '<div class="v74-ctrl"><label for="v74-' + b + '-ind">Indicador</label><select id="v74-' + b + '-ind" onchange="v74Set(\'' + b + '\',\'ind\',this.value)">' + opts + '</select>' +
    '<label for="v74-' + b + '-rec">Recorte</label><select id="v74-' + b + '-rec" onchange="v74Set(\'' + b + '\',\'rec\',this.value)">' + recs + '</select>' +
    (b === 'engel' ? '<label id="v74-' + b + '-c18w"><input type="checkbox" id="v74-' + b + '-c18" onchange="v74Set(\'' + b + '\',\'c18\',this.checked)"> mostrar 2017-2018</label>' : '') +
    '<span id="v74-' + b + '-exp"></span></div>' +
    '<p class="v43-leitura" id="v74-' + b + '-leitura"></p>' +
    '<div class="v74-graf" id="v74-' + b + '-graf"><div id="div-v74-' + b + '-plot"></div><div class="v74-mapa" id="div-v74-' + b + '-mapa"></div></div>' +
    '<div class="v74-nota" id="v74-' + b + '-nota"></div>';
  const exp = document.getElementById('v74-' + b + '-exp');
  if(exp && typeof v49Barra === 'function'){ const e = v49Barra('div-v74-' + b + '-plot'); e.dataset.g = 'div-v74-' + b + '-plot'; exp.appendChild(e); }
}
function v74Encaixa(){
  // o menu ganhou uma aba: o cartão de contexto passa a ser posto logo abaixo dele, qualquer que seja a altura
  const t = document.getElementById('mode-tabs'), i = document.getElementById('intro-bar'); if(!t || !i) return;
  i.style.removeProperty('top'); i.style.removeProperty('max-height');
  if(getComputedStyle(i).position === 'static') return;
  const d = t.getBoundingClientRect().bottom + 12 - i.getBoundingClientRect().top;
  if(d > 0){
    const cs = getComputedStyle(i), mh = parseFloat(cs.maxHeight);
    i.style.setProperty('top', (parseFloat(cs.top) + d) + 'px', 'important');
    if(mh) i.style.setProperty('max-height', Math.max(90, mh - d) + 'px', 'important');
  }
}
window.addEventListener('load', () => {
  setTimeout(v74Encaixa, 50);
  // reencaixa a cada troca de aba (a altura do seletor de anos muda entre as abas)
  const sm = window.setModo; window.setModo = function(){ const r = sm.apply(this, arguments); setTimeout(v74Encaixa, 0); return r; };
});
window.addEventListener('resize', () => setTimeout(v74Encaixa, 50));
function v74Set(b, k, v){ S.v74[b][k] = v; v74Render(b); syncURL(); }
function v74Render(b){
  v74Monta(b);
  const it = v74Ind(b), rc = v74Rec(b), C = V74_BOX[b], st = S.v74[b];
  const si = document.getElementById('v74-' + b + '-ind'), sr = document.getElementById('v74-' + b + '-rec'), c18 = document.getElementById('v74-' + b + '-c18');
  if(si) si.value = it.id; if(sr) sr.value = rc.id; if(c18){ c18.checked = !!st.c18; document.getElementById('v74-' + b + '-c18w').style.display = (it.id === 'engel_desp' || it.id === 'pct_fora') && rc.id === 'uf' ? '' : 'none'; }
  const L = v74Linhas(b), br = it.dados.total.Brasil, mostra18 = v74Tem18(b) && st.c18;
  const ehUF = rc.id === 'uf';
  document.getElementById('v74-' + b + '-graf').classList.toggle('com-mapa', ehUF);
  const mapa = document.getElementById('div-v74-' + b + '-mapa'); mapa.style.display = ehUF ? '' : 'none';
  // barras horizontais com IC
  const ys = L.map(l => l[0]), xs = L.map(l => l[2][0]);
  const hov = L.map(l => '<b>' + l[0] + '</b><br>' + v74Fmt(l[2][0], it) + ' (IC95% ' + v74Fmt(l[2][1], it) + ' a ' + v74Fmt(l[2][2], it) + ')<br>' +
    l[2][3].toLocaleString('pt-BR') + ' famílias na amostra' + (l[2][4] != null ? '; CV ' + String(l[2][4]).replace('.', ',') + '%' : '') + (l[2][5] ? '<br>† interpretar com cautela' : ''));
  const traces = [{type:'bar', orientation:'h', y:ys, x:xs, name:'2024-2025',
    marker:{color:L.map(l => (l[2][5] || l[2][4] == null) ? C.cor + '66' : C.cor), cornerradius:3},
    error_x:{type:'data', symmetric:false, array:L.map(l => l[2][2] - l[2][0]), arrayminus:L.map(l => l[2][0] - l[2][1]), color:'rgba(27,42,56,.55)', thickness:1.2, width:3},
    text:L.map(l => (l[2][5] || l[2][4] == null) ? '†' : ''), textposition:'outside', cliponaxis:false, hovertext:hov, hoverinfo:'text'}];
  if(mostra18){
    const v18 = L.map(l => V74.uf2018[l[1]]?.[it.id]);
    traces.push({type:'scatter', mode:'markers', y:ys, x:v18, name:'2017-2018 (tabelas do IBGE, sem IC)',
      marker:{symbol:'diamond', size:8, color:'#E0622B', line:{color:'#fff', width:1}},
      hovertext:L.map((l, i) => l[0] + ', 2017-2018: ' + v74Fmt(v18[i], it)), hoverinfo:'text'});
  }
  const alt = Math.max(260, 26 * L.length + 90);
  const layout = {height:alt, margin:{t:mostra18 ? 34 : 14, r:28, l:ehUF ? 132 : 210, b:46}, barmode:'overlay', showlegend:mostra18,
    legend:{orientation:'h', x:0, y:1.06, font:{size:11}},
    xaxis:{title:{text:it.unid === 'R$' ? 'R$ por mês' : '%', font:{size:11.5, color:'#4E5968'}}, rangemode:'tozero', gridcolor:'rgba(22,28,36,0.07)', zeroline:false,
      tickfont:{size:11, color:'#1B2A38'}, separatethousands:true},
    yaxis:{autorange:'reversed', tickfont:{size:11.5, color:'#1B2A38'}, automargin:true},
    shapes:br ? [{type:'line', xref:'x', yref:'paper', x0:br[0], x1:br[0], y0:0, y1:1, line:{color:'#7C332C', width:1.4, dash:'dot'}}] : [],
    annotations:br ? [{xref:'x', yref:'paper', x:br[0], y:1, yanchor:'bottom', text:'Brasil ' + v74Fmt(br[0], it), showarrow:false, font:{size:10.5, color:'#7C332C'}}] : [],
    font:{family:'Inter, sans-serif', size:12, color:'#1B2A38'}, paper_bgcolor:'transparent', plot_bgcolor:'transparent',
    hoverlabel:{bgcolor:'#fff', bordercolor:'rgba(28,45,64,.2)', font:{color:'#1B2A38', size:12}}};
  Plotly.react('div-v74-' + b + '-plot', traces, layout, {displayModeBar:false, responsive:true});
  if(ehUF){
    const ufs = L.map(l => l[1]), z = L.map(l => l[2][0]);
    Plotly.react('div-v74-' + b + '-mapa', [{type:'choropleth', geojson:GEOJSON, featureidkey:'properties.sigla', locations:ufs, z:z,
      colorscale:C.escala, marker:{line:{color:'#fff', width:0.8}}, hovertext:hov, hoverinfo:'text',
      colorbar:{thickness:10, len:0.55, x:0.98, y:0.3, ticksuffix:it.unid === '%' ? '%' : '', tickfont:{size:10}, outlinewidth:0}}],
      {margin:{t:0, b:0, l:0, r:0}, paper_bgcolor:'transparent', dragmode:false,
       geo:{scope:'world', resolution:50, fitbounds:'locations', visible:false, bgcolor:'rgba(0,0,0,0)', projection:{type:'mercator'}}},
      {displayModeBar:false, responsive:true});
  } else { try { Plotly.purge(mapa); } catch(e){} }
  // leitura
  const ok = L.filter(l => l[2] && !l[2][5] && l[2][4] != null), maior = ok.reduce((a, l) => l[2][0] > a[2][0] ? l : a, ok[0]), menor = ok.reduce((a, l) => l[2][0] < a[2][0] ? l : a, ok[0]);
  let t = '<strong>Leitura.</strong> ' + it.rot + ': ' + v74Fmt(br[0], it) + ' no Brasil (IC95% ' + v74Fmt(br[1], it) + ' a ' + v74Fmt(br[2], it) + ').';
  if(maior && menor && maior !== menor){
    const sep = maior[2][1] > menor[2][2];
    t += ' Por ' + rc.rot.toLowerCase() + ', vai de ' + v74Fmt(menor[2][0], it) + ', em “' + menor[0] + '”, a ' + v74Fmt(maior[2][0], it) + ', em “' + maior[0] + '”' +
      (sep ? '; os intervalos de confiança desses dois grupos não se sobrepõem.' : '; os intervalos de confiança desses dois grupos se sobrepõem, e a diferença pode não ser real.');
  }
  if(mostra18){
    const comp = ok.filter(l => V74.uf2018[l[1]]?.[it.id] != null), sobe = comp.filter(l => l[2][0] > V74.uf2018[l[1]][it.id]).length;
    t += ' Em ' + sobe + ' de ' + comp.length + ' UFs o valor de 2024-2025 é maior que o de 2017-2018 (comparação descritiva: 2017-2018 sem intervalo de confiança).';
  }
  if(ok.length < 2) t += ' As estimativas por ' + rc.rot.toLowerCase() + ' são imprecisas (amostra pequena ou coeficiente de variação alto); compare os grupos com cautela.';
  document.getElementById('v74-' + b + '-leitura').innerHTML = t;
  // notas
  const n = [];
  n.push('<p><b>O que mede.</b> ' + it.desc + (it.universo ? ' Universo: só as famílias que recebem Bolsa Família.' : ' Universo: todas as famílias (unidades de consumo).') + '</p>');
  if(it.cautela) n.push('<p><b>Cautela.</b> ' + it.cautela + '</p>');
  if(rc.id === 'faixa_renda') n.push('<p>Rendimento per capita da POF, que inclui rendimentos não monetários e a variação patrimonial, em salários mínimos de R$ 1.518. As faixas não são comparáveis com as da PNAD Contínua usadas nas outras abas.</p>');
  if(rc.id === 'ocupacao') n.push('<p>Trabalho principal da pessoa de referência nos 12 meses da pesquisa. A POF não separa emprego com e sem carteira.</p>');
  if(rc.id === 'capital') n.push('<p>Na POF, “capital” é a área urbana do município da capital; a área rural da capital fica em “interior”.</p>');
  if(mostra18) n.push('<p>2017-2018: tabelas por UF dos Primeiros Resultados da POF 2017-2018 (mesmas definições), sem intervalo de confiança. Os valores em reais não entram na comparação.</p>');
  n.push('<p>Grupos com menos de 30 famílias na amostra não aparecem. † menos de 150 famílias ou coeficiente de variação acima de 15%: interpretar com cautela. Indicador complementar: não mede insegurança alimentar. Fonte: ' + V74_FONTE + '.</p>');
  document.getElementById('v74-' + b + '-nota').innerHTML = n.join('');
}
function v74Spec(id){
  const b = id.indexOf('acesso') >= 0 ? 'acesso' : 'engel', it = v74Ind(b), rc = v74Rec(b), L = v74Linhas(b), m18 = v74Tem18(b) && S.v74[b].c18;
  const cab = ['recorte', 'categoria', 'estimativa', 'ic95_inf', 'ic95_sup', 'n_familias_amostra', 'cv_pct', 'cautela', 'unidade'].concat(m18 ? ['pof_2017_2018'] : []);
  const br = it.dados.total.Brasil, cel = (r, c, x) => [r, c, v47n(x[0], it.nd), v47n(x[1], it.nd), v47n(x[2], it.nd), x[3], v47n(x[4]), x[5] ? 'sim' : 'não', it.unid];
  const linhas = [cel('Brasil', 'Brasil', br).concat(m18 ? [''] : [])].concat(L.map(l => cel(rc.rot, l[0], l[2]).concat(m18 ? [v47n(V74.uf2018[l[1]]?.[it.id], 2)] : [])));
  return {titulo: it.rot + ', por ' + rc.rot.toLowerCase() + ' (POF 2024-2025)', sub: it.desc + ' Barras: IC95%.', fonte: V74_FONTE + (m18 ? '; POF 2017-2018 (tabelas por UF)' : ''), cab: cab, linhas: linhas};
}
"""
JS = JS.replace('__DADOS__', json.dumps(V, ensure_ascii=False, separators=(',', ':')))
troca("function setEngelEd(ed){", JS + "\nfunction setEngelEd(ed){")

# exportacao: especificacao dos graficos novos
troca("function v49Spec(id){\n", "function v49Spec(id){\n  if(String(id).startsWith('div-v74-')) return v74Spec(id);\n")
# CSV da visao (rodape) na aba nova
troca("  if(modo === 'desig'){\n    const m = V41.marcadores",
      "  if(modo === 'acesso'){ const sp = v74Spec('div-v74-acesso-plot'); return {nome:'pof2024_2025_' + v74Ind('acesso').id + '_' + v74Rec('acesso').id, titulo:sp.titulo + ' (' + sp.fonte + ')', csv:v47tabela(sp.cab, sp.linhas)}; }\n"
      "  if(modo === 'desig'){\n    const m = V41.marcadores")

# ── navegacao: setModo, URL, listas de abas ───────────────────────────────────────────────
troca("['ebia','filtros','pof','nova4','engel','regressao','desig','lacunas','consumo'].forEach(m => {",
      "['ebia','filtros','pof','nova4','engel','regressao','desig','lacunas','consumo','acesso'].forEach(m => {")
troca("modo === 'engel' || modo === 'regressao' || modo === 'desig' || modo === 'lacunas' || modo === 'consumo'){",
      "modo === 'engel' || modo === 'regressao' || modo === 'desig' || modo === 'lacunas' || modo === 'consumo' || modo === 'acesso'){")
troca("    document.getElementById('panel-consumo').style.display = (modo === 'consumo') ? '' : 'none';",
      "    document.getElementById('panel-consumo').style.display = (modo === 'consumo') ? '' : 'none';\n"
      "    document.getElementById('panel-acesso').style.display = (modo === 'acesso') ? '' : 'none';")
troca("    if(modo === 'engel') buildEngelChart();",
      "    if(modo === 'engel'){ buildEngelChart(); v74Render('engel'); }\n    if(modo === 'acesso') v74Render('acesso');
    setTimeout(v74Encaixa, 0);")
troca("const modo = ['engel','desig','lacunas','consumo'].includes(S.modoAtual) ? S.modoAtual",
      "const modo = ['engel','desig','lacunas','consumo','acesso'].includes(S.modoAtual) ? S.modoAtual")
troca("  if(modo==='engel'){ p.set('ed',S.engelEd||'2025');",
      "  if(modo==='acesso'){ p.set('xi',S.v74.acesso.ind); p.set('xr',S.v74.acesso.rec); history.replaceState(null,'','#'+p.toString()); return; }\n"
      "  if(modo==='engel'){ p.set('xi',S.v74.engel.ind); p.set('xr',S.v74.engel.rec); p.set('ed',S.engelEd||'2025');")
troca("const modo=['ebia','filtros','pof','engel','desig','lacunas','consumo'].includes(modo0)?modo0:'ebia';",
      "const modo=['ebia','filtros','pof','engel','desig','lacunas','consumo','acesso'].includes(modo0)?modo0:'ebia';")
troca("  if(['engel','desig','lacunas','consumo'].includes(modo)){",
      "  if(['engel','desig','lacunas','consumo','acesso'].includes(modo)){\n"
      "    if(modo==='engel'||modo==='acesso'){ const bx=S.v74[modo]; if(p.get('xi') && V74.ind.some(i=>i.id===p.get('xi') && V74_BOX[modo].familias.includes(i.familia))) bx.ind=p.get('xi'); if(p.get('xr') && V74.recortes.some(r=>r.id===p.get('xr'))) bx.rec=p.get('xr'); }")
troca("const V71_ANALITICAS = ['engel', 'desig', 'lacunas', 'consumo', 'regressao'];",
      "const V71_ANALITICAS = ['engel', 'desig', 'lacunas', 'consumo', 'regressao', 'acesso'];")

# ── textos ───────────────────────────────────────────────────────────────────────────────────
troca("  engel:   '<strong>Orçamento familiar (Coeficiente de Engel):</strong>",
      "  acesso:  '<strong>Renda e acesso (POF 2024-2025):</strong> transferências de renda (Bolsa Família, BPC, auxílio-gás, vale-alimentação), alimentos obtidos sem compra (doação e produção própria) e composição do gasto com alimentação, por UF, Grande Região e características das famílias, com IC95%. Indicadores complementares: não medem insegurança alimentar.',\n"
      "  engel:   '<strong>Orçamento familiar (Coeficiente de Engel):</strong>")
troca("(POF 2017-2018 e POF 2024-2025, com comparação entre as edições). Quanto menor a renda",
      "(POF 2017-2018 e POF 2024-2025, com comparação entre as edições) e, abaixo, por UF e por características das famílias (POF 2024-2025). Quanto menor a renda")
troca("da POF 2024-2025, só o coeficiente de Engel, a partir dos Primeiros Resultados divulgados em 27/11/2026)",
      "da POF 2024-2025, o coeficiente de Engel e as informações complementares da aba Renda e acesso, calculadas a partir dos microdados divulgados em 27/11/2026)")
troca("const V47_VERSAO = 'v73';", "const V47_VERSAO = 'v74';")
troca('<strong id="citar-versao">v73</strong>', '<strong id="citar-versao">v74</strong>')
open(HTML, 'w', encoding='utf-8').write(s)
print('ok', len(s))
