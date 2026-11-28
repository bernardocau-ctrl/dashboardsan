// Gera docs/registro_POF_2024_2025.docx (registro das inclusoes da POF 2024-2025 no painel).
// Uso: node gerar_registro.js <engel_tabelas.json> <engel_microdados.json> <saida.docx>
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  HeadingLevel, LevelFormat, BorderStyle, Footer, PageNumber, TableOfContents } = require('docx');

const [TAB, MIC, OUT, EXP, PV] = process.argv.slice(2);
const P = JSON.parse(fs.readFileSync(PV, 'utf8'));
const X = JSON.parse(fs.readFileSync(EXP, 'utf8'));
const g = (L, nome) => L.find(d => d.grupo === nome);
const ic = d => br(d.est) + '% (IC95% ' + br(d.ic95[0]) + ' a ' + br(d.ic95[1]) + ')';
const T = JSON.parse(fs.readFileSync(TAB, 'utf8'));
const M = JSON.parse(fs.readFileSync(MIC, 'utf8'));

const FONT = 'Arial';
const W = 9026; // A4 com margens de 1440
const br = (v, d = 1) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
const rs = v => br(v, 2);

const p = (text, opt = {}) => new Paragraph({ spacing: { after: 120, line: 300 }, ...opt,
  children: (Array.isArray(text) ? text : [text]).map(t => typeof t === 'string' ? new TextRun({ text: t, font: FONT, size: 22 }) : t) });
const b = t => new TextRun({ text: t, font: FONT, size: 22, bold: true });
const i = t => new TextRun({ text: t, font: FONT, size: 22, italics: true });
const h1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })] });
const h2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })] });
const item = (text, nivel = 0) => new Paragraph({ numbering: { reference: 'marcadores', level: nivel }, spacing: { after: 80, line: 290 },
  children: (Array.isArray(text) ? text : [text]).map(t => typeof t === 'string' ? new TextRun({ text: t, font: FONT, size: 22 }) : t) });
const num = text => new Paragraph({ numbering: { reference: 'numeros', level: 0 }, spacing: { after: 80, line: 290 },
  children: (Array.isArray(text) ? text : [text]).map(t => typeof t === 'string' ? new TextRun({ text: t, font: FONT, size: 22 }) : t) });

const borda = { style: BorderStyle.SINGLE, size: 4, color: 'BFC7D1' };
const bordas = { top: borda, bottom: borda, left: borda, right: borda };
function tabela(cab, linhas, larg, opt = {}) {
  const soma = larg.reduce((a, c) => a + c, 0);
  const cel = (txt, j, head) => new TableCell({
    borders: bordas, width: { size: larg[j], type: WidthType.DXA },
    shading: head ? { fill: 'E3EAF2', type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: { top: 60, bottom: 60, left: opt.fs ? 60 : 100, right: opt.fs ? 60 : 100 },
    children: [new Paragraph({ alignment: (!head && j > 0 && opt.numericas !== false && /^[−+\-]?[\d.,]+%?( p\.p\.)?$/.test(String(txt))) ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: [new TextRun({ text: String(txt), font: FONT, size: opt.fs || 18, bold: !!head })] })],
  });
  return new Table({ width: { size: soma, type: WidthType.DXA }, columnWidths: larg,
    rows: [new TableRow({ tableHeader: true, children: cab.map((c, j) => cel(c, j, true)) })]
      .concat(linhas.map(l => new TableRow({ children: l.map((c, j) => cel(c, j, false)) }))) });
}
const legenda = t => new Paragraph({ spacing: { before: 60, after: 200 }, children: [new TextRun({ text: t, font: FONT, size: 18, italics: true, color: '4E5968' })] });
const titTab = t => new Paragraph({ spacing: { before: 200, after: 80 }, keepNext: true, children: [new TextRun({ text: t, font: FONT, size: 20, bold: true })] });

const FX25 = ['Até R$ 3.036', 'R$ 3.036 a 4.554', 'R$ 4.554 a 9.108', 'R$ 9.108 a 15.180', 'R$ 15.180 a 22.770', 'R$ 22.770 a 37.950', 'Mais de R$ 37.950'];
const FX18 = ['Até R$ 1.908', 'R$ 1.908 a 2.862', 'R$ 2.862 a 5.724', 'R$ 5.724 a 9.540', 'R$ 9.540 a 14.310', 'R$ 14.310 a 23.850', 'Mais de R$ 23.850'];
const SM = ['Até 2', '2 a 3', '3 a 6', '6 a 10', '10 a 15', '15 a 25', 'Mais de 25'];

function tabEngel(chave, mic) {
  return tabela(['Faixa', 'Alim. no domicílio', 'Alim. fora', 'Alim. total', 'Despesa corrente', 'Rendimento', '% desp.', '% renda', '% fora', 'n'],
    T[chave].classes.map((c, k) => [FX25[k], rs(c.alim_dom), rs(c.alim_fora), rs(c.alim_total), rs(c.despesa), rs(c.renda), br(c.engel_desp), br(c.engel_renda), br(c.pct_fora), mic[k].n_amostra.toLocaleString('pt-BR')]),
    [1250, 900, 860, 900, 1020, 1020, 600, 600, 560, 680], { fs: 16 });
}
const dif = (a, b) => { const d = Math.round((b - a) * 10) / 10; return d === 0 ? '0,0' : (d > 0 ? '+' : '−') + br(Math.abs(d)); };
function tabComp(loc) {
  const A = T['2018_' + loc].classes, B = T['2025_' + loc].classes;
  return tabela(['Faixa (salários mínimos)', '2017-2018, % despesa', '2024-2025, % despesa', 'Diferença (p.p.)', '2017-2018, % fora', '2024-2025, % fora', 'Diferença (p.p.)'],
    SM.map((f, k) => [f, br(A[k].engel_desp), br(B[k].engel_desp), dif(A[k].engel_desp, B[k].engel_desp), br(A[k].pct_fora), br(B[k].pct_fora), dif(A[k].pct_fora, B[k].pct_fora)]),
    [1826, 1200, 1200, 1200, 1200, 1200, 1200]);
}

const hoje = '27 de novembro de 2026';
const FTP = 'https://ftp.ibge.gov.br/Orcamentos_Familiares/Pesquisa_de_Orcamentos_Familiares_2024_2025/';
const filhos = [
  new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: 'Registro das inclusões da POF 2024-2025', font: FONT })] }),
  p([new TextRun({ text: 'Painel de Insegurança Alimentar no Brasil (produto técnico da dissertação, PPGSAN/UNIRIO)', font: FONT, size: 24, color: '4E5968' })]),
  p([b('Versão do painel: '), 'v75 (inclui a v73 e a v74). ', b('Data: '), hoje + '. ', b('Situação: '), 'versão de trabalho, ainda sem depósito no Zenodo e sem DOI próprio.']),
  p([b('Finalidade deste documento: '), 'registrar, de forma rastreável, tudo o que entrar no painel a partir da Pesquisa de Orçamentos Familiares (POF) 2024-2025 do IBGE: o que foi incluído, de quais tabelas e arquivos, com quais definições, como foi conferido e com quais cautelas. Novas inclusões devem ser acrescentadas como novas seções da parte 9 (Histórico de inclusões), sem apagar as anteriores.']),

  h1('1. Resumo'),
  item([b('Incluído na v73: '), 'o coeficiente de Engel da POF 2024-2025 (parte do orçamento familiar gasta com alimentação, por faixa de rendimento), para o Brasil e o Rio de Janeiro, com as mesmas definições usadas para a POF 2017-2018, e uma visão de comparação entre as duas edições.']),
  item([b('Não incluído: '), 'nada que dependa da Escala Brasileira de Insegurança Alimentar (EBIA), de cor ou raça, de instrução, das quantidades adquiridas em kg ou do consumo alimentar pessoal. Essas informações foram coletadas na POF 2024-2025, mas ainda não foram liberadas pelo IBGE.']),
  item([b('Conferência: '), 'as definições foram validadas reproduzindo exatamente os 42 valores de 2017-2018 que o painel já mostrava. Os valores de 2024-2025 vêm das tabelas oficiais e o gasto com alimentação foi recalculado a partir dos microdados, com resultado idêntico ao centavo nas 28 células e no número de famílias.']),
  item([b('Outras abas: '), 'nenhuma mudança de dados. Os textos que citavam a POF 2017-2018 como única fonte do Engel foram atualizados.']),

  h1('2. A divulgação do IBGE em 27/11/2026'),
  p('O IBGE divulgou os Primeiros Resultados da POF 2024-2025, com tabelas de despesas e rendimentos das famílias (Brasil, situação do domicílio, Grandes Regiões e Unidades da Federação), e, no mesmo dia, os microdados correspondentes. Ambos estão no servidor de downloads do IBGE:'),
  item(FTP + 'Primeiros_Resultados/ (tabelas em xlsx e ods)'),
  item(FTP + 'Microdados/ (dados, documentação, questionários, programas de leitura em R e SAS, memória de cálculo, cadastro de produtos e tradutores das tabelas)'),
  p('Segundo o arquivo "Leiame" dos microdados, esta liberação contém as variáveis da publicação de Primeiros Resultados (despesas e rendimentos) e algumas características dos moradores, e os demais temas serão divulgados segundo um cronograma de trabalho. Não foi encontrada data anunciada para os próximos temas.'),
  titTab('Tabela 1. Informações de interesse do painel na POF 2024-2025'),
  tabela(['Informação', 'Coletada?', 'Liberada em 27/11/2026?'], [
    ['EBIA (segurança alimentar)', 'Sim (questionário POF 6, pessoa de referência)', 'Não'],
    ['Cor ou raça; instrução', 'Sim (questionário POF 1)', 'Não'],
    ['Quantidade adquirida de alimentos (kg)', 'Sim (caderneta, questionário POF 3)', 'Não (a caderneta traz só o valor em reais)'],
    ['Consumo alimentar pessoal', 'Sim (questionário POF 7)', 'Não'],
    ['Sexo, idade, condição na unidade de consumo, situação do domicílio, estrato, pesos e pesos de replicação', 'Sim', 'Sim'],
    ['Despesas (inclusive alimentação) e rendimentos', 'Sim', 'Sim'],
  ], [3600, 3026, 2400], { numericas: false }),
  legenda('Fonte: dicionário de variáveis e questionários dos microdados da POF 2024-2025 (IBGE, 2026), conferidos em 27/11/2026.'),

  h1('3. O que cada aba do painel pode receber'),
  titTab('Tabela 2. Situação de cada aba em relação à POF 2024-2025'),
  tabela(['Aba', 'Situação', 'Motivo'], [
    ['Insegurança alimentar (EBIA)', 'Aguarda', 'EBIA não liberada.'],
    ['Fatores socioeconômicos (11 fatores, 55 cruzamentos)', 'Aguarda', 'As células são prevalência de insegurança alimentar. Com os dados de hoje já é possível montar 9 dos 11 fatores; cor ou raça e instrução não foram liberadas (19 dos 55 cruzamentos dependem delas).'],
    ['Aquisição domiciliar (kg por pessoa ao ano, 17 grupos)', 'Aguarda', 'Quantidades em kg não liberadas. O gasto em reais por grupo é outra medida e não deve ser misturado à série em kg.'],
    ['Orçamento familiar (coeficiente de Engel)', 'Incluído na v73', 'Despesas e rendimentos por faixa de rendimento estão publicados para o Brasil e para todas as UFs.'],
    ['Desigualdades no Brasil', 'Aguarda', 'Baseada na EBIA.'],
    ['Consumo individual (Estudo 2)', 'Aguarda', 'Depende do consumo alimentar pessoal e da EBIA.'],
    ['Lacunas e comparabilidade', 'A decidir', 'Pode registrar a POF 2024-2025 (EBIA coletada e não liberada) e a liberação em etapas; o texto espelha a dissertação e deve ser validado pelo autor.'],
  ], [2700, 1500, 4826], { numericas: false }),

  h1('4. Coeficiente de Engel: definições'),
  p('Foram mantidas, sem alteração, as definições da POF 2017-2018 usadas desde a v45 do painel. Elas foram confirmadas reproduzindo exatamente os valores do painel a partir das tabelas oficiais de 2017-2018 (ver parte 6).'),
  item([b('Gasto com alimentação: '), 'despesa monetária e não monetária média mensal familiar com alimentação, total, no domicílio e fora do domicílio (Tabela 1.1.7 para o Brasil; 1.3.33.3 para o Rio de Janeiro).']),
  item([b('Denominador "despesa": '), 'despesas correntes (Tabela 1.1.1; Rio de Janeiro, 1.3.33.1). Não é a despesa total nem a despesa de consumo.']),
  item([b('Denominador "renda": '), 'rendimento total médio mensal familiar, sem a variação patrimonial (Tabela 2.1.1; Rio de Janeiro, 2.3.33.1).']),
  item([b('Indicadores: '), 'Engel sobre a despesa = alimentação total ÷ despesas correntes; Engel sobre a renda = alimentação total ÷ rendimento total; % fora = alimentação fora do domicílio ÷ alimentação total. Valores em %, com uma casa decimal.']),
  item([b('Faixas: '), 'classes de rendimento total e variação patrimonial mensal familiar definidas pelo IBGE, em múltiplos do salário mínimo vigente: até 2, 2 a 3, 3 a 6, 6 a 10, 10 a 15, 15 a 25 e mais de 25 salários mínimos. Em 2024-2025 o salário mínimo de referência é R$ 1.518 (até R$ 3.036, ..., mais de R$ 37.950); em 2017-2018 era R$ 954 (até R$ 1.908, ..., mais de R$ 23.850). A primeira faixa inclui as famílias sem rendimento.']),
  item([b('Unidade: '), 'a "família" das tabelas é a unidade de consumo da POF.']),

  h1('5. Coeficiente de Engel: valores incluídos'),
  titTab('Tabela 3. Coeficiente de Engel por faixa de rendimento, Brasil, POF 2024-2025'),
  tabEngel('2025_BR', M.BR),
  legenda('Fonte: IBGE, POF 2024-2025, Primeiros Resultados, Tabelas 1.1.1, 1.1.7 e 2.1.1; valores em reais, médias mensais por família; % desp. e % renda = coeficiente de Engel sobre a despesa corrente e sobre o rendimento; n = famílias (unidades de consumo) na amostra, calculado a partir dos microdados.'),
  titTab('Tabela 4. Coeficiente de Engel por faixa de rendimento, Rio de Janeiro, POF 2024-2025'),
  tabEngel('2025_RJ', M.RJ),
  legenda('Fonte: IBGE, POF 2024-2025, Primeiros Resultados, Tabelas 1.3.33.1, 1.3.33.3 e 2.3.33.1. A faixa de mais de R$ 37.950 tem 139 famílias na amostra, abaixo do limite de 150 que o painel usa para indicar "interpretar com cautela".'),
  p([b('Totais (todas as faixas). '), 'Brasil: alimentação R$ ' + rs(T['2025_BR'].total.alim_total) + ' por mês, ' + br(T['2025_BR'].total.engel_desp) + '% da despesa corrente, ' + br(T['2025_BR'].total.engel_renda) + '% do rendimento, ' + br(T['2025_BR'].total.pct_fora) + '% fora do domicílio. Rio de Janeiro: R$ ' + rs(T['2025_RJ'].total.alim_total) + ', ' + br(T['2025_RJ'].total.engel_desp) + '%, ' + br(T['2025_RJ'].total.engel_renda) + '% e ' + br(T['2025_RJ'].total.pct_fora) + '%. Os totais não aparecem no gráfico do painel, que mostra só as faixas.']),
  h2('5.1 Comparação entre as edições'),
  p('A visão "Comparar" do painel põe lado a lado as duas edições, por faixa em salários mínimos, para o Brasil ou para o Rio de Janeiro. As tabelas abaixo registram os valores mostrados.'),
  titTab('Tabela 5. Coeficiente de Engel (% da despesa corrente) e % fora do domicílio, Brasil, POF 2017-2018 e 2024-2025'),
  tabComp('BR'),
  legenda('Fontes: IBGE, POF 2017-2018 e POF 2024-2025 (tabelas citadas na parte 4). Diferenças em pontos percentuais, sem intervalo de confiança e sem teste estatístico.'),
  titTab('Tabela 6. Coeficiente de Engel (% da despesa corrente) e % fora do domicílio, Rio de Janeiro, POF 2017-2018 e 2024-2025'),
  tabComp('RJ'),
  legenda('Fontes: as mesmas da Tabela 5. Na POF 2024-2025, a faixa de mais de 25 salários mínimos tem 139 famílias na amostra do Rio de Janeiro.'),

  h1('6. Como os valores foram conferidos'),
  num([b('Definições (2017-2018). '), 'Com as tabelas oficiais da POF 2017-2018 (servidor de downloads do IBGE, pasta Primeiros_resultados), o script engel_tabelas.py recalculou os três indicadores do Brasil e do Rio de Janeiro. Os 42 valores (7 faixas × 3 indicadores × 2 locais) coincidem com os que o painel mostrava desde a v45. Dos 35 valores em reais do Brasil, 33 coincidem; 2 diferem em R$ 0,01 (gasto total com alimentação nas faixas de R$ 2.862 a 5.724 e de mais de R$ 23.850), porque o painel antigo obteve o total somando o gasto no domicílio e fora dele, em vez de usar o total da tabela. Os percentuais não mudam. Na v73, os valores de 2017-2018 foram mantidos como estavam, e os de 2024-2025 usam o total da tabela oficial. Isso confirma que o painel usa despesas correntes e rendimento total sem variação patrimonial.']),
  num([b('Extração (2024-2025). '), 'O mesmo script extraiu, das tabelas 1.1.1, 1.1.7 e 2.1.1 (Brasil) e 1.3.33.1, 1.3.33.3 e 2.3.33.1 (Rio de Janeiro), os valores das Tabelas 3 e 4.']),
  num([b('Microdados (2024-2025). '), 'O script engel_microdados.py refez, a partir dos arquivos MORADOR, CADERNETA_COLETIVA e DESPESA_INDIVIDUAL, o cálculo da memória de cálculo do IBGE para a tabela de alimentação (valor deflacionado × fator de anualização ÷ 12; tradutor de alimentação; média por unidade de consumo ponderada pelo PESO_FINAL), com as famílias classificadas pelo RENDA_TOTAL nas mesmas faixas. O gasto no domicílio e fora dele coincidiu ao centavo com as tabelas publicadas nas 28 células (7 faixas × 2 componentes × 2 locais), assim como o número estimado de famílias em cada faixa. Amostra: 77.292 unidades de consumo no Brasil e 5.193 no Rio de Janeiro.']),
  num([b('Painel. '), 'O painel foi aberto num navegador automatizado (Chromium), em tela de computador (1366 px) e de celular (390 px): as três edições, os dois locais da comparação, as três medidas, o arquivo CSV e o link com o estado da aba foram testados, sem erros no console e sem rolagem horizontal no celular.']),
  p([i('Limite da conferência: '), 'as despesas correntes e o rendimento total de 2024-2025 foram lidos das tabelas oficiais e não foram recalculados a partir dos microdados.']),

  h1('7. Cautelas de interpretação'),
  item('O coeficiente de Engel é indicador complementar do orçamento familiar; não mede insegurança alimentar nem consumo alimentar.'),
  item('São estimativas pontuais, sem intervalo de confiança. As diferenças entre edições e entre o Brasil e o Rio de Janeiro são descritivas; diferenças pequenas podem não ser reais. Os microdados trazem pesos de replicação (bootstrap) que permitiriam calcular intervalos de confiança em versão futura.'),
  item('As faixas são em salários mínimos da época. Como o salário mínimo teve ganho real entre 2018 e 2025, a mesma faixa não corresponde exatamente ao mesmo poder de compra nas duas edições.'),
  item('Os percentuais podem ser comparados entre as edições; os valores em reais não, porque cada edição está em reais da sua própria data de referência e o painel não os corrige pela inflação entre edições.'),
  item('Na faixa de menor rendimento, a despesa corrente média é maior que o rendimento declarado nas duas edições (em 2024-2025, R$ 2.405,68 contra R$ 1.984,89 no Brasil). O painel descreve o fato e não testa explicações.'),
  item('No Rio de Janeiro, a faixa de mais de 25 salários mínimos tem 139 famílias na amostra de 2024-2025; o painel exibe aviso de cautela.'),
  item('Os números são dos Primeiros Resultados. Se o IBGE revisar tabelas ou microdados, os valores precisam ser conferidos de novo.'),

  h1('8. Alterações técnicas no painel (v73)'),
  item('index.html: novos conjuntos de dados ENGEL_BR_2025 e ENGEL_RJ_2025 (com os valores das Tabelas 3 e 4 e o n da amostra) e o objeto ENGEL_ED, que reúne as duas edições e suas fontes. Os dados de 2017-2018 (ENGEL_BR e ENGEL_RJ) não mudaram.'),
  item('Aba Orçamento familiar: botões de edição (2017-2018, 2024-2025, que é a opção inicial, e Comparar) e, na comparação, de local (Brasil ou Rio de Janeiro). Frase de leitura, eixo, nota de fonte e avisos de cautela passam a ser gerados a partir dos dados da edição escolhida.'),
  item('Exportações: o CSV da aba passa a ter as colunas edição, faixa em salários mínimos e n da amostra; a figura PNG e seu CSV citam a fonte da edição exibida.'),
  item('Link: o endereço guarda a edição e o local (por exemplo, #m=engel&ed=comp&el=rj).'),
  item('Textos: dica da aba, introdução, cartão da família Orçamento familiar e nota "De onde vêm os dados" passam a citar a POF 2024-2025. Versão exibida em "Como citar": v73.'),
  item('README.md: fontes e histórico da v73.'),
  item('docs/v73/: scripts e resultados da conferência (engel_tabelas.py, engel_microdados.py, os respectivos arquivos .json e patch_v73.py, que aplicou a maior parte das mudanças; dois ajustes posteriores, um título sem travessão e o aviso de cautela na comparação, foram feitos diretamente no index.html).'),

  h1('9. Histórico de inclusões'),
  titTab('Tabela 7. Inclusões da POF 2024-2025 no painel'),
  tabela(['Data', 'Versão', 'O que entrou', 'Fonte'], [
    ['27/11/2026', 'v73', 'Coeficiente de Engel, Brasil e Rio de Janeiro, 7 faixas; comparação com 2017-2018', 'Primeiros Resultados (tabelas 1.1.1, 1.1.7, 2.1.1, 1.3.33.1, 1.3.33.3, 2.3.33.1); microdados de 27/11/2026'],
    ['27/11/2026', 'v75', 'Composição do gasto em 57 subgrupos (arroz, feijão, carnes, refrigerantes e outros); despesa com alimentação escolar (R$) e com cesta básica (R$, média de todas as famílias); desconto de cesta básica no salário', 'Microdados de 27/11/2026; conferência com a Tabela 1.1.7'],
    ['27/11/2026', 'v74', '33 indicadores por UF, Grande Região e 9 fatores, com IC95%: Engel, % fora, gasto por pessoa e gás (aba Orçamento familiar); transferências de renda, forma de aquisição e composição do gasto (aba nova Renda e acesso); Engel e % fora por UF em 2017-2018', 'Microdados de 27/11/2026; tabelas por UF da POF 2017-2018'],
  ], [1200, 900, 3426, 3500], { numericas: false }),

  h1('10. Pendências e próximos passos'),
  item([b('Decisão do autor: '), 'depositar a v73 no Zenodo (novo DOI) e decidir se o texto da dissertação passa a citá-la; hoje a dissertação descreve a v58.']),
  item([b('Possível ampliação, com os dados já liberados: '), 'Engel para as 27 UFs e por situação do domicílio; intervalos de confiança com os pesos de replicação.']),
  item([b('Quando o IBGE liberar a EBIA: '), 'ponto de 2024-2025 na série nacional e por UF, recortes e cruzamentos. A base com 9 dos 11 fatores já está pronta (parte 11); falta só juntar a EBIA pela chave da família e calcular.']),
  item([b('Decisão do autor: '), 'quais das informações novas da parte 12 entram no painel, e em qual aba.']),
  item([b('Quando liberar cor ou raça e instrução: '), 'os 19 cruzamentos restantes.']),
  item([b('Quando liberar as quantidades: '), 'aquisição domiciliar em kg por pessoa ao ano, com a mesma classificação em 17 grupos.']),
  item([b('Quando liberar o consumo alimentar pessoal: '), 'avaliar a atualização do Estudo 2, que depende também da EBIA.']),

  h1('11. Preparação da base de microdados (27/11/2026)'),
  p('Para que a atualização seja rápida quando a EBIA for liberada, a leitura dos microdados e a construção dos fatores do painel ficaram prontas na pasta pof2025/ do repositório (leitura.py, base_familias.py, estimativas.py, explorar.py e README.md). A base tem uma linha por família (unidade de consumo), que é também a unidade em que a EBIA é perguntada (questionário POF 6, pessoa de referência da unidade de consumo); a EBIA entrará pela chave COD_UPA + NUM_DOM + NUM_UC. Só 0,13% das famílias dividem o domicílio com outra unidade de consumo, de modo que família e domicílio praticamente coincidem.'),
  titTab('Tabela 8. Conferência da base com as tabelas publicadas, Brasil, POF 2024-2025'),
  tabela(['Indicador', 'Base', 'Publicado pelo IBGE'], [
    ['Número de famílias', '79.561.637', '79.561.637'], ['Tamanho médio da família (pessoas)', '2,67', '2,67'],
    ['Rendimento total e variação patrimonial médio (R$)', '9.240,04', '9.240,04'], ['Despesa com alimentação média (R$)', '1.113,00', '1.113,00'],
    ['Despesa corrente média (R$)', '7.331,88', '7.331,88'], ['Programas sociais federais, média por família (R$)', '200,14', '200,14'],
    ['Coeficiente de Engel nas 27 UFs', 'igual em todas', 'Tabelas 1.3.UF.1 e 1.3.UF.3'],
  ], [4626, 2200, 2200]),
  legenda('Fonte: microdados e Tabelas 1.1.1, 1.1.7 e 2.1.1 da POF 2024-2025 (IBGE, 2026).'),
  p([b('Achado sobre a tabela publicada. '), 'O tradutor oficial de despesa geral repete em duas linhas idênticas 10 códigos de deduções de rendimentos (507001 a 507010, quadro 7 de outros rendimentos: pensão alimentícia, mesada e doação de não morador, entre outros). Como o programa do IBGE junta os registros ao tradutor pelo código, essas deduções entram duas vezes na despesa corrente publicada: R$ 2,99 a mais na média do Brasil (0,04%). O efeito no coeficiente de Engel é desprezível (15,2% nas duas versões). A base guarda a despesa corrente igual à publicada e a versão sem a repetição. O achado se soma aos registrados na aba Lacunas sobre a cadeia de informação e pode ser comunicado ao IBGE.']),
  titTab('Tabela 9. Fatores do painel na POF 2024-2025 (dados de 27/11/2026)'),
  tabela(['Fator', 'Situação', 'Diferença em relação à PNADC usada no painel'], [
    ['Sexo, idade da pessoa de referência, criança <5, idoso ≥60, urbano ou rural', 'Pronto', 'Nenhuma relevante (o sexo é o de nascimento).'],
    ['Tamanho do domicílio', 'Pronto', 'Conta os moradores da unidade de consumo, exceto pensionista, empregado doméstico e parente dele.'],
    ['Capital ou interior', 'Pronto, com diferença', 'Na POF, "capital" é a área urbana do município da capital (estrato); a área rural da capital fica no interior.'],
    ['Faixa de renda (per capita, em salários mínimos)', 'Pronto, com diferença', 'O rendimento da POF inclui rendimentos não monetários (como o aluguel estimado de imóvel próprio) e a variação patrimonial. As faixas baixas ficam muito menores (1,4% das famílias até 1/4 SM) e "sem rendimento" quase não existe (4 famílias na amostra). As faixas não devem ser comparadas com as da PNADC.'],
    ['Posição na ocupação', 'Parcial', 'A POF não separa emprego com e sem carteira, e o período é de 12 meses. Ficam 6 categorias: privado (com ou sem carteira), doméstico, público (com militar), empregador, conta própria e outros (sem trabalho no período, 30,4% das pessoas de referência, ou não remunerado).'],
    ['Cor ou raça; instrução', 'Não liberado', 'Coletados (questionário POF 1), ainda não disponíveis.'],
  ], [2900, 1500, 4626], { numericas: false }),

  h1('12. Informações novas que os dados liberados já permitem'),
  p('Sem a EBIA, nenhuma informação nova mede insegurança alimentar. Os dados liberados permitem, porém, indicadores complementares de acesso aos alimentos pela via do orçamento, da renda e da forma de aquisição, todos com intervalo de confiança pelos pesos de replicação. Os resultados abaixo são do Brasil (exceto quando indicado), calculados com a base da parte 11; nenhum deles está no painel.'),
  h2('12.1 Coeficiente de Engel pelos fatores do painel'),
  p('Hoje o painel mostra o Engel só por faixa de rendimento familiar. Com a base, ele pode ser cruzado com os 9 fatores. Exemplos: famílias até 1/4 SM per capita, ' + ic(g(X.A_engel_por_fator.faixa_renda, 'Até 1/4 SM')) + ' da despesa corrente; mais de 5 SM, ' + ic(g(X.A_engel_por_fator.faixa_renda, 'Mais de 5 SM')) + '; pessoa de referência trabalhadora doméstica, ' + ic(g(X.A_engel_por_fator.ocupacao, 'Trabalhador doméstico')) + '; setor público, ' + ic(g(X.A_engel_por_fator.ocupacao, 'Setor público (inclui militar)')) + '. A parcela da alimentação feita fora de casa vai de ' + br(g(X.A_fora_por_fator.faixa_renda, '1/4 a 1/2 SM').est) + '% (1/4 a 1/2 SM) a ' + br(g(X.A_fora_por_fator.faixa_renda, 'Mais de 5 SM').est) + '% (mais de 5 SM).'),
  h2('12.2 Coeficiente de Engel por UF e por Grande Região'),
  p('Os valores conferem com as tabelas estaduais publicadas. O Engel vai de ' + br(g(X.D_engel_por_uf, 'DF').est) + '% (Distrito Federal) a ' + br(g(X.D_engel_por_uf, 'AM').est) + '% (Amazonas); por região, de ' + br(g(X.D_engel_por_regiao, 'CO').est) + '% (Centro-Oeste) a ' + br(g(X.D_engel_por_regiao, 'N').est) + '% (Norte). Isso permitiria um mapa do Engel por UF, como o mapa da EBIA, e a comparação com a POF 2017-2018 por UF (as tabelas estaduais de 2017-2018 também estão publicadas).'),
  h2('12.3 Programas de transferência de renda'),
  p('O cadastro de produtos identifica Bolsa Família (com Auxílio Brasil), BPC, auxílio-gás e outros programas; a soma confere com a linha "Programas sociais federais" da tabela publicada. Famílias que declararam receber Bolsa Família: ' + ic(g(X.B_bolsa_familia_por_fator.faixa_renda, 'Total')) + '; ' + br(g(X.B_bolsa_familia_por_fator.sexo, 'Mulher').est) + '% com pessoa de referência mulher e ' + br(g(X.B_bolsa_familia_por_fator.sexo, 'Homem').est) + '% com homem; ' + br(g(X.B_bolsa_familia_por_fator.crianca5, 'Com criança <5').est) + '% das famílias com criança menor de 5 anos; ' + br(g(X.B_bolsa_familia_por_fator.sit_dom, 'Rural').est) + '% no rural. Nas famílias que recebem, o benefício é ' + br(X.B_bf_parcela_da_renda.est) + '% do rendimento total, e o Engel é ' + br(g(X.B_engel_bf, 'Recebe Bolsa Família').est) + '%, contra ' + br(g(X.B_engel_bf, 'Não recebe').est) + '% nas que não recebem (diferença de ' + br(X.B_engel_bf_dif.dif) + ' p.p., IC95% ' + br(X.B_engel_bf_dif.ic95[0]) + ' a ' + br(X.B_engel_bf_dif.ic95[1]) + '). A diferença descreve perfis de renda distintos e não é efeito do programa. Cautela: o recebimento é declarado e pode estar subdeclarado; antes de publicar, convém comparar com os registros administrativos do programa no mesmo período.'),
  h2('12.4 Forma de aquisição dos alimentos para o domicílio'),
  p('Cada aquisição tem a forma registrada: monetária, doada pelo governo, doada por outros, produção própria, troca, retirada do negócio ou outra. Do valor da alimentação no domicílio, ' + ic(g(X.C_nao_monet_por_situacao, 'Total')) + ' foi não monetário no Brasil, ' + br(g(X.C_nao_monet_por_situacao, 'Urbano').est) + '% no urbano e ' + br(g(X.C_nao_monet_por_situacao, 'Rural').est) + '% no rural, onde a produção própria responde por ' + br(g(X.C_prod_propria_por_situacao, 'Rural').est) + '% do valor e está presente em ' + br(g(X.C_familias_prod_propria_por_situacao, 'Rural').est) + '% das famílias. Receberam algum alimento doado ' + ic(g(X.C_familias_com_doacao_por_renda, 'Total')) + ' das famílias, com maior frequência nas faixas de 1/4 a 1 SM per capita (cerca de 6%). A doação pelo governo é rara na caderneta (' + br(g(X.C_doacao_gov_por_renda, 'Total').est) + '% do valor) e tem coeficiente de variação alto; não deve ser detalhada por recorte.'),
  h2('12.5 Gasto mensal per capita com alimentação'),
  p('Gasto com alimentação por pessoa por mês: R$ ' + rs(g(X.E_alim_pc_por_renda, 'Até 1/4 SM').est) + ' nas famílias até 1/4 SM per capita e R$ ' + rs(g(X.E_alim_pc_por_renda, 'Mais de 5 SM').est) + ' nas de mais de 5 SM (média do Brasil, R$ ' + rs(g(X.E_alim_pc_por_renda, 'Total').est) + '). O valor descreve gasto, não quantidade nem qualidade da alimentação.'),
  h2('12.6 Outras possibilidades identificadas, ainda não calculadas'),
  item('Auxílio-alimentação recebido do trabalho (vale ou cartão): declarado por 24,4% das famílias.'),
  item('Despesa com alimentação escolar e com cesta básica, e desconto de cesta básica no salário.'),
  item('Auxílio-gás (3,3% das famílias) e gasto com gás de cozinha, relacionado ao preparo de alimentos.'),
  item('Composição do gasto alimentar no domicílio pelos grupos da tabela do IBGE (arroz, feijão, carnes, frutas, refrigerantes e outros), por faixa de renda.'),
  h2('12.7 Avaliação'),
  p('As informações de 12.1 a 12.4 têm boa precisão (coeficientes de variação em geral abaixo de 5% no Brasil) e ligação direta com o acesso aos alimentos. As mais próximas do objeto da dissertação são o Engel por fator e por UF (que ampliam uma aba existente sem criar nova família de indicadores) e a aquisição não monetária, que mostra a importância da produção própria no rural. Os programas de transferência são o contexto mais relevante para a leitura da EBIA quando ela sair, mas pedem cuidado com a subdeclaração. Todas são indicadores complementares e precisam da mesma ressalva do painel: não medem insegurança alimentar.'),

  h1('13. Inclusões da v74: todas as informações novas'),
  p('A v74 leva ao painel as informações da parte 12. Na aba Orçamento familiar, abaixo do gráfico por faixa de rendimento, um bloco novo mostra o Engel e indicadores do orçamento por UF (mapa e ranking), Grande Região e pelos 9 fatores. Uma aba nova, Renda e acesso, reúne as transferências de renda, a forma de aquisição dos alimentos e a composição do gasto com alimentação, com os mesmos recortes. Os dados vêm de pof2025/gerar_painel.py (arquivo pof2025/resultados/painel_v74.json).'),
  titTab('Tabela 10. Indicadores incluídos na v74, com o valor do Brasil (POF 2024-2025)'),
  tabela(['Aba e seção', 'Indicador', 'Brasil (IC95%)'],
    P.ind.filter(it => it.familia !== 'composicao_sub' && !['val_escolar', 'val_cesta', 'fam_desc_cesta'].includes(it.id)).map(it => { const c = it.dados.total.Brasil, f = v => it.unid === 'R$' ? 'R$ ' + rs(v) : br(v, it.nd) + '%';
      return [(it.familia === 'engel' ? 'Orçamento familiar' : 'Renda e acesso') + ': ' + it.secao, it.rot, f(c[0]) + ' (' + f(c[1]) + ' a ' + f(c[2]) + ')']; }),
    [2400, 4426, 2200], { numericas: false }),
  legenda('Fonte: IBGE, microdados da POF 2024-2025 (27/11/2026); elaboração própria. Cada indicador está disponível por UF (27), Grande Região (5) e pelas categorias dos 9 fatores da parte 11.'),
  h2('13.1 Regras de exibição'),
  item('Estimativa pontual com PESO_FINAL; IC95% pelos 200 pesos de replicação (bootstrap), com o erro-padrão descrito no README de pof2025.'),
  item('Grupos com menos de 30 famílias na amostra não aparecem (caso, por exemplo, de "sem rendimento", com 4 famílias). Grupos com menos de 150 famílias ou coeficiente de variação acima de 15% aparecem mais claros e com o sinal †, para interpretação com cautela.'),
  item('A frase de leitura compara o maior e o menor valor só entre os grupos sem aviso de cautela e diz se os intervalos de confiança deles se sobrepõem. Quando quase todos os grupos são imprecisos (cesta básica por UF, por exemplo), a frase avisa isso em vez de apontar extremos.'),
  item('Na aba Orçamento familiar, o Engel e o % fora do domicílio por UF podem ser comparados com 2017-2018 (losangos laranja), calculados com as mesmas definições a partir das tabelas por UF daquela edição, sem intervalo de confiança. A comparação é descritiva; em ' + (() => { const it = P.ind.find(i => i.id === 'engel_desp'); const u = Object.keys(P.uf2018); return u.filter(k => it.dados.uf[k] && it.dados.uf[k][0] > P.uf2018[k].engel_desp).length + ' de ' + u.length; })() + ' UFs o Engel de 2024-2025 é maior que o de 2017-2018.'),
  item('Os gráficos exportam PNG (com título, fonte e citação), CSV (com IC, n e coeficiente de variação) e tabela, como os demais; o endereço guarda indicador e recorte.'),
  h2('13.2 Conferências'),
  item('Engel por UF: igual às 27 tabelas estaduais publicadas (parte 11).'),
  item('Engel e % fora por UF em 2017-2018: o valor do Rio de Janeiro (13,6% e 30,7%) coincide com o que a aba já mostrava a partir das tabelas daquela edição.'),
  item('Composição do gasto: os 15 grupos com nome próprio coincidem com a Tabela 1.1.7 (participação de cada grupo na alimentação no domicílio) até a segunda casa decimal; os 16 grupos somam 100%.'),
  item('Programas sociais: a soma dos códigos do tradutor reproduz a linha "Programas sociais federais" (R$ 200,14).'),
  item('Gasto por pessoa: R$ 416,36 por mês, igual à despesa média com alimentação (R$ 1.113,00) dividida pelo tamanho médio da família (2,67), a menos do arredondamento.'),
  h2('13.3 Cautelas próprias desta versão'),
  item('Nenhum indicador novo mede insegurança alimentar; todos descrevem orçamento, renda ou forma de aquisição.'),
  item('Transferências: recebimento declarado, sujeito a subdeclaração. O Engel das famílias que recebem Bolsa Família descreve o perfil de quem recebe e não é efeito do programa.'),
  item('Doação, produção própria e cesta básica vêm da caderneta de 7 dias e captam mal aquisições esporádicas ou sazonais. A cesta básica é rara na amostra (0,16% das famílias, coeficiente de variação de 17%) e fica imprecisa por recorte.'),
  item('Faixa de rendimento per capita da POF e posição na ocupação seguem as diferenças da Tabela 9: não comparar com as categorias da PNADC das outras abas.'),
  item('Composição do gasto: participação no valor gasto, não na quantidade adquirida nem no consumo.'),

  h1('14. Inclusões da v75: subgrupos, alimentação escolar e cesta básica'),
  p('A v75 completa a aba Renda e acesso com três itens que a v74 tinha deixado parciais.'),
  item([b('Composição do gasto em subgrupos. '), 'Além dos 16 grupos, o seletor passa a ter os 57 subgrupos da tabela de alimentação do IBGE, como arroz, feijão, carne de boi de primeira e de segunda, frango, ovo, leite de vaca, pão francês, biscoito, café moído, refrigerantes e cervejas, com os mesmos recortes e IC95%. Os 73 itens (grupos e subgrupos) foram conferidos contra a Tabela 1.1.7: a maior diferença é de 0,005 p.p., de arredondamento.']),
  item([b('Alimentação escolar paga. '), 'Além do % de famílias com essa despesa, o valor mensal médio nas famílias que a têm.']),
  item([b('Cesta básica. '), 'Além do % de famílias que adquiriram, o valor mensal médio por família, calculado sobre todas as famílias. A caderneta cobre 7 dias, e o IBGE converte o valor da semana em mensal (cerca de 4,3 vezes); essa conversão é válida para a média de todas as famílias, mas inflaria a média só de quem comprou na semana (R$ 1.352,56 por mês, valor que não representa o gasto real e por isso não foi usado).']),
  item([b('Desconto de cesta básica no salário. '), 'Percentual de famílias. É muito raro na amostra e fica com estimativa imprecisa, sinalizada no painel.']),
  item([b('Intervalos de confiança. '), 'O limite inferior passa a ser cortado em zero, porque o intervalo aproximado podia ficar negativo em proporções muito pequenas.']),
  item([b('Correção da v74. '), 'As introduções das abas Orçamento familiar e Renda e acesso tinham ficado longas demais para o cartão de contexto, que as escondia e mostrava só o botão Sobre o painel. Os textos foram encurtados e voltaram a aparecer.']),
  titTab('Tabela 11. Indicadores novos da v75, Brasil (POF 2024-2025)'),
  tabela(['Indicador', 'Brasil (IC95%)', 'n'],
    P.ind.filter(it => ['val_escolar', 'val_cesta', 'fam_desc_cesta', 's1011', 's1012', 's1071', 's1072', 's1081', 's1091', 's1101', 's1102', 's1121', 's1122', 's1124'].includes(it.id)).map(it => {
      const c = it.dados.total.Brasil, f = v => it.unid === 'R$' ? 'R$ ' + rs(v) : br(v, it.nd) + '%';
      return [it.rot, f(c[0]) + ' (' + f(c[1]) + ' a ' + f(c[2]) + ')' + (c[5] ? ' †' : ''), c[3].toLocaleString('pt-BR')]; }),
    [5126, 2700, 1200], { numericas: false }),
  legenda('Fonte: IBGE, microdados da POF 2024-2025 (27/11/2026); elaboração própria. Subgrupos selecionados; todos os 57 estão no painel e em pof2025/resultados/painel_v75.json. n = famílias na amostra (no valor da alimentação escolar, só as que têm a despesa). † interpretar com cautela.'),

  h1('15. Reportagem "Cem moedas" no Retrato'),
  p('Uma quinta página foi acrescentada ao Retrato (retrato/moedas.html), no estilo de "O prato": texto em cartões e uma animação em canvas que muda conforme a leitura. A metáfora é a de cem moedas, R$ 1 de cada R$ 100 de despesa da família; no fim, as moedas viram casas, uma por família. A página funciona sem internet e respeita a preferência por movimento reduzido.'),
  item('Cenas: R$ 15 de cada R$ 100 para a comida (15,2%, contra 15,3% em 2017-2018); as sete faixas de rendimento (de 21,8% a 9,2%); a mesma escada em reais (de R$ 525 a R$ 3.294 por mês); dentro e fora de casa (de 19,9% a 50,0% fora); mapa de quadrados das UFs (de 11,7% no DF a 24,0% no AM), com as mudanças desde 2017-2018 (queda nas nove UFs do Nordeste, maior alta no Amazonas); a sacola em 16 grupos; arroz e feijão nas duas pontas da renda per capita; a comida obtida sem compra no urbano e no rural; o Bolsa Família em três recortes e por UF; e um fecho sobre o que ainda falta (a EBIA da POF 2024-2025).'),
  item('Os números vêm dos mesmos arquivos conferidos do painel (Engel por faixa das tabelas publicadas; demais indicadores de painel_v75.json). O gerador pof2025/gerar_retrato.py injeta os dados no modelo pof2025/moedas_modelo.html e confere 16 números escritos no texto contra os dados.'),
  item('Cautelas escritas na própria página: comparação com 2017-2018 descritiva (sem intervalo de confiança naquela edição); participação no gasto não é quantidade nem consumo; caderneta de 7 dias capta mal doações e produção sazonal; recebimento do Bolsa Família declarado; nenhum número da página mede insegurança alimentar.'),
  item('Desenho das peças (28/11/2026): moedas realistas desenhadas por código em alta resolução, com mipmaps, como os grãos de O prato: metal com brilho escovado, borda elevada, serrilha na espessura, algarismo, espiga e ano em relevo, marcas de uso e sombra suave; latão para o total, cobre para a comida, níquel para a comida fora de casa, estanho fosco para o restante e esmalte colorido para os grupos de alimentos. A moeda é genérica e não reproduz o desenho de nenhuma moeda em circulação. As casas ganharam parede pintada, telhado de telha, porta e janela. A tela só é redesenhada durante a rolagem.'),
  item('As moedas arredondam: com poucas moedas por coluna ou quadrado, o desenho aproxima o valor, e o texto e as tabelas ao fim da página trazem os números exatos.'),

  h1('Referências'),
  p('IBGE. Pesquisa de Orçamentos Familiares 2024-2025: primeiros resultados. Tabelas e microdados. Rio de Janeiro: IBGE, 2026. Disponível em: ' + FTP + '. Acesso em: 27 nov. 2026.'),
  p('IBGE. Pesquisa de Orçamentos Familiares 2017-2018: primeiros resultados. Tabelas de despesas, rendimentos e Unidades da Federação. Rio de Janeiro: IBGE, 2019. Disponível em: https://ftp.ibge.gov.br/Orcamentos_Familiares/Pesquisa_de_Orcamentos_Familiares_2017_2018/Primeiros_resultados/. Acesso em: 27 nov. 2026.'),
  p('CASTANHO, Bernardo. Painel de Insegurança Alimentar no Brasil. [S. l.]: Zenodo, 2026. DOI: 10.5281/zenodo.23405765.'),
];

const doc = new Document({
  creator: 'Bernardo Castanho', title: 'Registro das inclusões da POF 2024-2025', description: 'Painel de Insegurança Alimentar no Brasil, v73',
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal', run: { font: FONT, size: 36, bold: true, color: '1B2A38' }, paragraph: { spacing: { before: 0, after: 120 }, keepNext: true } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 28, bold: true, color: '1F4E79' }, paragraph: { spacing: { before: 320, after: 120 }, keepNext: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 24, bold: true, color: '1F4E79' }, paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: 'marcadores', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: 'numeros', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] },
  ] },
  features: { updateFields: true },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      new TextRun({ text: 'Registro POF 2024-2025 · Painel v75 · página ', font: FONT, size: 16, color: '6B7682' }),
      new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: '6B7682' })] })] }) },
    children: filhos,
  }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log('ok', OUT, buf.length); });
