# Crítica da versão 1 e o que mudou na versão 2

Apresentação de qualificação "Para além da média nacional" (PPGSAN/UNIRIO), 25 minutos pelo Google Meet, com compartilhamento de uma aba do Chrome.

Legenda: **Severidade** Alta / Média / Baixa. **v2**: Corrigido / Parcial / Não corrigido.

## Resumo dos dez problemas mais sérios da v1

1. O resultado central (slide 11, "depende da escala") termina coberto por uma tabela sobre um véu translúcido: a figura que explica o achado desaparece no momento da conclusão, e o fundo "fantasma" fica sujo no Meet. (Alta, Corrigido)
2. A animação do slide central é decorativa: as linhas e os colchetes mostram a diferença absoluta, mas nada mostra visualmente por que a razão não muda. O achado mais importante da dissertação depende de a banca imaginar a escala relativa. (Alta, Corrigido: a mesma figura passa da escala aritmética para a logarítmica, as linhas ficam quase paralelas e os colchetes passam de "16,2 / 14,5 p.p." para "1,85× / 1,88×".)
3. Tempo irrealista: 2.716 palavras em exatamente 24:00 (113 palavras por minuto escritas), com slides cheios de números lidos em voz alta (o slide 10 lia 12 percentuais). Na prática, a fala estouraria os 25 minutos. (Alta, Corrigido: 2.092 palavras em 21:50.)
4. Abertura sem gancho pessoal nem "por quê": a capa e o slide 2 não dizem por que um nutricionista do IBGE fez este trabalho nem qual é o problema prático (a dissertação abre justamente com essa pergunta na seção 1.1). O fechamento ("Obrigado" e uma foto) não retoma a abertura. (Alta, Corrigido: pergunta prática no slide 2; mapa de luzes retorna no encerramento.)
5. O "so what" do mestrado profissional fica fraco: o painel aparece como um carrossel automático de quatro capturas, que gira sozinho a cada 6,5 s, sem relação com a fala e sem controle do apresentador. (Alta, Corrigido: visita guiada por cliques, aba por aba, com a fala sincronizada, e a contribuição declarada como metodológica, como na seção 3.1.)
6. Sinalização fraca: depois do slide 5, a banca não sabe em que camada está; o recurso das "três camadas" (bom) é apresentado uma vez e abandonado. (Média, Corrigido: navegador "1 Distribuição · 2 Alimentação · 3 Informação" no canto de todos os slides de resultados.)
7. Redundância: a mesma informação (EBIA em branco 2016-2019 e 2021) aparece três vezes (linha do tempo, grade de anos, faixa no gráfico), e "pergunta" e "camadas" repetem o mesmo agrupamento em dois slides. (Média, Corrigido: slides 4 e 5 fundidos; a situação dos arquivos fica só na linha do tempo dos métodos.)
8. Gráfico da trajetória enganoso: a faixa cinza "PNADC: EBIA em branco" cobre o ponto da POF 2017-2018, sugerindo que a POF está dentro da lacuna; os rótulos 2023 e 2024 ficavam espremidos como "2023-24". (Média, Corrigido.)
9. Defeitos de código: o waffle do slide 2 não se apagava ao voltar uma etapa; temporizadores de etapas antigas continuavam disparando depois de ida e volta rápida; clique para devolver o foco à aba avançava um slide sem querer (risco real no Meet); pop-up bloqueado falhava em silêncio; numeração "24 / 22 · reserva". (Média, Corrigido.)
10. Integridade: "CC BY 4.0" no slide do painel não tem fonte na dissertação nem no README; a nota do slide de composição dizia que o magnésio maior era "coerente com mais feijão", interpretação que não está no texto; travessões curtos (–) em intervalos das reservas violavam a regra de estilo do autor. (Alta, Corrigido: removidos; os intervalos usam "a".)

## (a) Narrativa e engajamento

| # | Problema | Sev. | v2 |
|---|---|---|---|
| A1 | Sem gancho: o 24,2% é apresentado e o "mas" fica só na fala. A banca não vê a média se partir. | Alta | Corrigido: no slide 2, o waffle de 24 quadrados se divide em dois (Norte 37,6% e Sul 13,6%, mesmo ano e mesma pesquisa). |
| A2 | Falta a motivação do autor (Nutrição e IBGE, seção 1.1), que é o que justifica um mestrado profissional. | Alta | Corrigido na fala do slide 2. |
| A3 | Encerramento sem retorno à abertura; foto de crianças sem relação com o argumento. | Média | Corrigido: o mapa de luzes da capa volta com a frase da justificativa (seção 3.1) e a fala retoma "quem está na média". |
| A4 | Arco de tensão: o resultado central chega no minuto 11, mas a pergunta "a desigualdade diminuiu?" não é antecipada. | Média | Parcial: a pergunta P2 já aparece como "Depende da escala?" no slide 4, e o slide 9 prepara a pergunta. |
| A5 | Transições faladas ausentes entre camadas ("passo à segunda camada" existia só para o Estudo 2). | Média | Corrigido: "Entro na primeira camada", "Passo à segunda camada", "A terceira camada é a informação". |
| A6 | Slide da síntese não diz qual é a entrega do mestrado profissional. | Média | Corrigido na fala ("a entrega é dupla: a análise e o painel"). |
| A7 | Duas frases-chave ("a média esconde"; "depende da escala") competem com muitas outras. | Baixa | Parcial: as duas frases agora fecham os slides 2 e 10. |

## (b) Desenho dos slides e visualização

| # | Problema | Sev. | v2 |
|---|---|---|---|
| B1 | Texto pequeno para o Meet: rodapés de 16 px, etiquetas de 13 a 15 px (status "pré-registrado", "fonte/processamento"), rótulos de UF de 15 px, legenda do mapa de 16 px. A compressão de vídeo apaga isso. | Alta | Corrigido: rodapés 18 px, etiquetas de status 17 a 18 px, rótulos e eixos 18 a 21 px. |
| B2 | Desfoque (filter: blur) em toda a troca de slide e em cada fragmento: pesado para a GPU e, no Meet, vira borrão de compressão. | Média | Corrigido: transições só com opacidade e deslocamento, com direção (avançar e voltar). |
| B3 | Prato do Estudo 2: o anel tracejado parecia um ícone de "carregando"; a legenda colidia com o rodapé. | Média | Corrigido: fatia vazia hachurada e legenda em duas linhas dentro da área. |
| B4 | Composição: o título "por 1.000 kcal" incluía fibra em g/dia; a etiqueta "secundário, Holm" contradizia "sem correção" ao lado. | Média | Corrigido. Também se declara que as barras dos níveis de IA são a média na segurança somada à diferença ajustada (cálculo da apresentação). |
| B5 | Slide 4 (pergunta) e síntese com cartões altos e vazios; renda com grande vazio entre o texto e os cartões. | Baixa | Corrigido. |
| B6 | Comparabilidade como tabela de cinco linhas: correta, mas pouco memorável. | Média | Corrigido: arcos sobre um eixo do tempo; acima do eixo, comparações com sustentação; abaixo, não sustentadas. |
| B7 | Foto de crianças sorrindo ao lado de "24,2% em insegurança alimentar": associa rostos ao dado. | Média | Corrigido: foto retirada. Restam fotos sem pessoas, com crédito em todos os slides que as usam (o slide dos três limites não tinha crédito). |
| B8 | Bases dos gráficos: barras começam em zero (correto); o gráfico de inclinação começa em 10% (aceitável para inclinação, eixo rotulado). | Baixa | Mantido, com eixo explícito nas duas escalas. |
| B9 | Linha de "fonte" do slide de marcadores encostava na frase de cautela. | Baixa | Corrigido. |

## (c) Animação

| # | Problema | Sev. | v2 |
|---|---|---|---|
| C1 | Animações decorativas onde deveriam explicar (planos 3D das camadas; carrossel automático). | Alta | Corrigido: animações agora carregam o argumento (waffle que se divide, arcos de comparabilidade, mudança de escala, visita guiada ao painel). |
| C2 | Inconsistência: alguns slides revelam por clique, outros por tempo (o carrossel girava sozinho enquanto o autor falava de outra coisa). | Média | Corrigido: tudo que importa avança por clique. |
| C3 | `prefers-reduced-motion` só desligava CSS; contagens, waffle e partículas continuavam animados por JavaScript. | Média | Corrigido: modo instantâneo também no JavaScript. |
| C4 | Velocidade: entradas com desfoque e 1 s de duração; no Meet, movimento rápido e fino vira ruído. | Baixa | Corrigido: movimentos médios (0,6 a 1,7 s), formas grossas (traços de 5 a 10 px). |

## (d) Código e robustez

| # | Problema | Sev. | v2 |
|---|---|---|---|
| D1 | Waffle: voltar da etapa 1 para 0 não apagava os quadrados. | Média | Corrigido. |
| D2 | `setTimeout` das etapas não eram cancelados: ida e volta rápida deixava quadrados acesos e barras crescendo fora de hora. | Média | Corrigido: temporizadores por slide (cancelados ao sair) e por elemento (cancelados a cada nova etapa). Testado com 60 avanços e 60 recuos em sequência. |
| D3 | Clique em qualquer lugar avança: o clique para devolver o foco à aba compartilhada pulava um slide. | Média | Corrigido: o clique que apenas devolve o foco é ignorado (400 ms). |
| D4 | Pop-up bloqueado falhava em silêncio; P de novo abria outra janela. | Média | Corrigido: aviso na tela e reaproveitamento da janela já aberta. |
| D5 | Janela do apresentador sem "número + Enter" (as reservas só pela lista). | Média | Corrigido. |
| D6 | Comandos podiam chegar duas vezes (postMessage e BroadcastChannel). | Baixa | Corrigido: identificador por comando. |
| D7 | Laço de partículas da capa não era cancelado ao sair e reentrar. | Baixa | Corrigido. |
| D8 | Barra de progresso passava de 100% nas reservas; página "24 / 22 · reserva". | Baixa | Corrigido: "Reserva A" a "Reserva F". |
| D9 | Ajuda e roteiro com "23 a 28" fixos; marcos de tempo do roteiro escritos à mão. | Baixa | Corrigido: numeração e marcos calculados a partir de `falas.py`. |
| D10 | A animação de entrada (`animation-fill-mode: both`) prendia opacidade e transformação, impedindo esconder o waffle depois. | Baixa | Corrigido (entrada num invólucro). |
| D11 | Ajuda (tecla ?) aparece para a banca na aba compartilhada. | Baixa | Não corrigido (é útil no ensaio); o roteiro orienta a não usá-la durante a apresentação. |

## (e) Notas de fala

| # | Problema | Sev. | v2 |
|---|---|---|---|
| E1 | Ritmo: 113 palavras escritas por minuto com muitos números lidos; vários slides acima de 120. | Alta | Corrigido: média de 96 palavras escritas por minuto (cerca de 104 contando os números lidos por extenso); números lidos só quando são o ponto do slide. |
| E2 | Slide de marcadores lia 12 percentuais em sequência: o ouvinte perde todos. | Média | Corrigido: lê só o contraste de renda e nomeia os outros grupos. |
| E3 | Nota do slide 2 de "Pergunta" e do slide de "Camadas" repetidas. | Média | Corrigido (slides fundidos). |
| E4 | Interpretação sem fonte ("magnésio maior, coerente com mais feijão"). | Alta | Corrigido (retirada). |
| E5 | A fala do painel não dizia para quem ele foi feito. | Média | Corrigido: "o público geral e os agentes públicos que monitoram a segurança alimentar" (seção 1.1). |

## (f) Guia de perguntas

| # | Problema | Sev. | v2 |
|---|---|---|---|
| F1 | Faltava a pergunta provável de um estatístico: como as interações ano × marcador foram estimadas e por que "planejada e não pré-registrada". | Alta | Corrigido (nova pergunta, seção 4.5). |
| F2 | Faltava defender a mudança de escala do slide central ("isso não manipula a figura?"). | Média | Corrigido. |
| F3 | Faltava como o painel trata células com pouca amostra (n mínimo 30; instável abaixo de 50; cautela de 50 a 149). | Média | Corrigido. |
| F4 | Faltava a categoria do produto técnico (Produto 01, software/aplicativo, seção 4.10). | Média | Corrigido. |
| F5 | "CC BY 4.0" afirmado no guia sem fonte. | Alta | Corrigido: retirado e incluído na lista "Antes da banca, confirme". |
| F6 | Postura com numeração fixa das reservas. | Baixa | Corrigido (calculada). |

## O que não foi possível resolver

- O IC95% de 2024 (23,8 a 24,5) vem do painel v70, não do texto da dissertação (exceção já aceita na v1).
- As capturas do painel são estáticas: uma demonstração ao vivo exigiria trocar de aba no Meet, o que é arriscado; o roteiro sugere deixar o painel aberto em outra aba só se a banca pedir.
- Não há avaliação de legibilidade num Meet real; a verificação foi feita por capturas a 1920 × 1080. Recomenda-se um ensaio numa chamada de teste.
