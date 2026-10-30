# Painel de Insegurança Alimentar no Brasil

Produto técnico da dissertação de mestrado em Segurança Alimentar e Nutricional
(PPGSAN/UNIRIO) de Bernardo Castanho.

Painel interativo com cinco famílias de indicadores: experiência de acesso aos alimentos (EBIA),
fatores socioeconômicos e demográficos, aquisição domiciliar por grupos
alimentares (POF), orçamento familiar (coeficiente de Engel) e consumo individual
(Estudo 2). Descreve prevalências e metadados dos inquéritos do IBGE; não inclui a
regressão preliminar nem a participação de ultraprocessados na aquisição ou no consumo.

A aba **Consumo individual** traz o Estudo 2 da dissertação: a alimentação relatada por
cada morador (POF 2017-2018, módulo de consumo alimentar pessoal) segundo o nível de
insegurança alimentar do domicílio, em diferenças ajustadas com IC95% (plano registrado
em https://osf.io/m2gz6). São associações, não efeitos causais.

As desigualdades aparecem no botão **Filtros** do painel do estado (mapa por
UF com recortes) e na aba **Desigualdades no Brasil** (prevalência por marcador social com IC95%,
diferença absoluta e razão entre grupos, teste de mudança 2023-2024). A aba
**Lacunas e comparabilidade** mostra os anos com EBIA nos inquéritos, as
comparações sustentadas e os achados sobre a cadeia de informação. Para 2023 e
2024, as estimativas por UF trazem IC95% e a mudança entre os anos, com p
ajustado (Holm); em 2024, o mapa mostra também a variação desde 2023, colorida só
nas UFs em que a mudança é detectável após a correção de Holm.

Os recortes por fator podem ser cruzados dois a dois (55 pares de 11 fatores, por UF, Brasil e Grandes
Regiões; PNADC 2023 e 2024, com IC95% em cada célula, e PNAD 2004, 2009 e 2013, sem intervalo). A janela
de análise de cada cruzamento mostra a diferença entre dois grupos por UF (com IC95% da diferença), a
variação de 2023 para 2024 (com IC95%) e um mapa de calor numa UF, para a insegurança alimentar total ou
moderada ou grave. Os intervalos de diferença e de variação não têm correção para comparações múltiplas
nos marcadores (o resumo informa a de Bonferroni), e a PNAD tradicional não é comparável com a PNADC.

**Como citar:** Castanho, Bernardo. *Painel de Insegurança Alimentar no Brasil*.
Zenodo, 2026. https://doi.org/10.5281/zenodo.23405765 (todas as versões; a v70, atual,
é https://doi.org/10.5281/zenodo.23784335; a v58 é https://doi.org/10.5281/zenodo.23769033; a v50,
congelada anteriormente, é https://doi.org/10.5281/zenodo.23406463).

**Fontes:** PNAD 2004/2009/2013 · POF 2002/2008/2017-2018 · PNAD Contínua
2023/2024 (IBGE) · VIGISAN 2021 (Rede PENSSAN).

O arquivo `index.html` é autocontido: abre em qualquer navegador, inclusive sem
internet, sem instalar nada.

---

## Histórico

- v70 (29/10/2026): variação 2023→2024 por grupo e UF, com IC95% (o erro-padrão trata os dois anos como
  independentes, o que concorda com o bootstrap dos pesos replicados). Depositada no Zenodo
  (https://doi.org/10.5281/zenodo.23784335).
- v69 (29/10/2026): fator posição na ocupação da pessoa de referência (55 pares, 11 fatores).
- v68 (29/10/2026): IC95% da diferença entre dois grupos nos halteres.
- v67 (29/10/2026): insegurança alimentar moderada ou grave em todas as células.
- v66 (29/10/2026): recortes e cruzamentos nos anos da PNAD (2004, 2009 e 2013), sem IC.
- v65 (29/10/2026): IC95% nas células de recortes e cruzamentos de 2023 e 2024.
- v59 a v64 (29/10/2026): janela de análise de cruzamentos, ranking com busca, comparação de UF,
  visualização como tabela, matriz completa de pares (por UF, Brasil e Grandes Regiões), idade da pessoa
  de referência, download de todos os cruzamentos e link da análise.
- v58 (29/10/2026): total de IA exato nas nove séries simples por UF (578 de 1.847 células
  de 2023 e 2024, diferença de 0,1 p.p.; IA grave, segurança alimentar e n não mudam).
  Depositada no Zenodo (https://doi.org/10.5281/zenodo.23769033).
- v57 (29/10/2026): cinco cruzamentos de dois fatores por UF (capital ou interior × sexo,
  renda e instrução; idoso × instrução; criança menor de 5 anos × situação do domicílio),
  num total de 23 pares.
- v56 (22/10/2026): três cruzamentos novos (sexo × criança menor de 5 anos; cor ou raça ×
  idoso; renda × tamanho do domicílio) e correção do total de IA e do n dos 15 pares
  anteriores.
- v55 (15/10/2026): IA moderada ou grave com IC95% por UF e Brasil (2023 e 2024), no
  painel do estado e no CSV; painel do estado não passa mais por baixo da série histórica
  em telas altas.
- v54 (15/10/2026): botão "variação 2023→24" visível em todos os anos (leva a 2024);
  painel do estado e do Brasil com IA leve e moderada e barra da distribuição.
- v53 (15/10/2026): mapa e ranking da variação 2023→2024 por UF (cor só onde p de Holm
  < 0,05); título do mapa deixa de cobrir o título do painel entre 1181 e 1300 px.
- v52 (15/10/2026): aba Consumo individual (Estudo 2: Onda 1 e grupos alimentares,
  POF 2017-2018, conferida contra as Tabelas 5.21 a 5.24 da dissertação).
- v51 (15/10/2026): no menu, Aquisição domiciliar antes de Desigualdades no Brasil.
- v50 (15/10/2026): figuras e CSV exportados trazem o crédito pronto (Fonte: Castanho
  (2026) e referência ABNT). Versão congelada para a banca e depositada no Zenodo.
- v49 (15/10/2026): cada gráfico exporta PNG em alta resolução (com legenda,
  fonte, citação e metadados no arquivo) e CSV, conforme o recorte na tela.
- v48 (15/10/2026): layout para celular e telas estreitas; janela única "Sobre o
  painel"; guia rápido na primeira visita; siglas explicadas; ajustes na aquisição.
- v47 (15/10/2026): dados de cada visão em CSV; mapa em % ou em mil domicílios
  (2023 e 2024); IC na dica do mapa; Quadro 6.1.1 na aba Lacunas.
- v46 (15/10/2026): botão "Como citar" (ABNT e APA, com cópia automática).
- v45 (15/10/2026): fonte do coeficiente de Engel corrigida (POF 2017-2018);
  versão congelada para a banca.
- v44 (15/10/2026): gráfico do coeficiente de Engel redesenhado, com frase de
  leitura; recortes por UF só pelo botão Filtros (sai a aba Filtrar).
- v43 (15/10/2026): anos abaixo do menu; aba Desigualdades no Brasil
  redesenhada; frases de leitura na aquisição e nas desigualdades; nomes
  alinhados à dissertação (experiência de acesso; Filtrar).
- v42 (15/10/2026): IC95% e mudança 2023-2024 por UF; Rio de Janeiro por domínio
  amostral; domicílios em número absoluto; link guarda todas as abas; ajustes de
  contraste e leitura.
- v41 (15/10/2026): abas Desigualdades no Brasil e Lacunas e comparabilidade;
  IC95% nacionais.
- v40 (15/10/2026): texto alinhado à dissertação.
- v39 (12/10/2026): sem regressão preliminar nem participação de ultraprocessados.

---

Material acadêmico em elaboração. Os números são de uso restrito à banca até a
defesa.
