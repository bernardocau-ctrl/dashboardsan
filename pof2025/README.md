# POF 2024-2025: leitura dos microdados e fatores do painel

Preparação para incluir a POF 2024-2025 no Painel de Insegurança Alimentar no Brasil assim que o IBGE liberar a EBIA.
Nada desta pasta aparece no painel por enquanto; o painel (v73) só usa da POF 2024-2025 o coeficiente de Engel.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `leitura.py` | Lê qualquer um dos 8 arquivos de dados (layouts do programa oficial do IBGE) e calcula o valor mensal de cada registro como na memória de cálculo do IBGE. Guarda cópia em `.pkl` para as leituras seguintes. |
| `base_familias.py` | Monta a base com uma linha por família (unidade de consumo, UC), os 9 fatores do painel que já podem ser construídos, gasto com alimentação, despesa corrente, programas sociais e os 200 pesos de replicação; confere com as tabelas publicadas. |
| `estimativas.py` | Estimativas ponderadas (razão, proporção e média) com IC95% pelos pesos de replicação (bootstrap), por grupo, e diferença entre dois grupos. |
| `explorar.py` | Triagem das informações novas que os dados liberados já permitem (Engel por fator e UF, Bolsa Família, aquisição não monetária de alimentos, gasto per capita). |
| `resultados/triagem_2026-11-27.json` | Saída de `explorar.py` com os microdados de 27/11/2026. |

## Como rodar

Precisa de Python 3 com pandas, numpy e xlrd (para os tradutores `.xls`).

```
python3 -I base_familias.py <Dados_20261127.zip> <Tradutor_Alimentação.xls> <Tradutor_Despesa_Geral.xls> <pasta_cache>
python3 -I explorar.py <pasta_cache>/base_uc.pkl <saida.json>
```

Os dados e tradutores estão em
https://ftp.ibge.gov.br/Orcamentos_Familiares/Pesquisa_de_Orcamentos_Familiares_2024_2025/Microdados/
(o zip de dados tem 138 MB e não fica neste repositório). A base leva cerca de 2 minutos para ser montada.

## Conferência com as tabelas publicadas (Brasil)

| Indicador | Base | IBGE |
|---|---|---|
| Número de famílias | 79.561.637 | 79.561.637 |
| Tamanho médio da família | 2,67 | 2,67 |
| Rendimento total e variação patrimonial médio (R$) | 9.240,04 | 9.240,04 |
| Despesa com alimentação média (R$) | 1.113,00 | 1.113,00 |
| Despesa corrente média (R$) | 7.331,88 | 7.331,88 |
| Programas sociais federais, média por família (R$) | 200,14 | 200,14 |
| Coeficiente de Engel por UF (27 UFs) | igual em todas | Tabelas 1.3.UF.1 e 1.3.UF.3 |

Achado sobre a tabela publicada: o tradutor oficial de despesa geral repete em duas linhas idênticas 10 códigos de
deduções (507001 a 507010, quadro 7 de outros rendimentos). Como o programa do IBGE junta pelo código, essas deduções
entram duas vezes na despesa corrente publicada (R$ 2,99 a mais na média do Brasil, 0,04%). A base guarda as duas
versões: `despesa_corrente` (igual à tabela) e `despesa_corrente_sem_dupl`.

## Os fatores do painel na POF 2024-2025

| Fator | Situação | Como foi construído | Diferença em relação à PNADC do painel |
|---|---|---|---|
| Sexo | pronto | sexo de nascimento da pessoa de referência da UC | nenhuma relevante |
| Idade da pessoa de referência | pronto | até 29, 30 a 44, 45 a 59, 60 ou mais | nenhuma |
| Criança menor de 5 anos | pronto | algum morador da UC | nenhuma |
| Idoso de 60 anos ou mais | pronto | algum morador da UC | nenhuma |
| Tamanho do domicílio | pronto | moradores da UC: 1, 2 a 3, 4 a 5, 6 ou mais | conta a UC (só 0,13% das UCs dividem domicílio) |
| Urbano ou rural | pronto | situação do domicílio | nenhuma |
| Capital ou interior | pronto, com diferença | estrato "Município da Capital" | na POF é só a área urbana da capital; a área rural da capital fica no interior |
| Faixa de renda | pronto, com diferença | rendimento total da UC ÷ moradores, em salários mínimos de R$ 1.518 | o rendimento da POF inclui rendimentos não monetários (como o aluguel estimado de quem mora em imóvel próprio) e a variação patrimonial; por isso as faixas baixas ficam bem menores (1,4% até 1/4 SM) e "sem rendimento" quase não existe (4 famílias). Não comparar as faixas com as da PNADC. |
| Posição na ocupação | parcial | trabalho principal da pessoa de referência nos 12 meses (o de mais meses) | a POF não separa emprego com e sem carteira; as categorias viram 6 (privado com ou sem carteira, doméstico, público com militar, empregador, conta própria, outros); o período é de 12 meses, não a semana de referência; 30,4% das pessoas de referência não tiveram trabalho no período |
| Cor ou raça | não liberado | coletado no POF 1 | |
| Instrução | não liberado | coletado no POF 1 | |

Moradores contados: todos os da UC, exceto pensionista, empregado doméstico e parente do empregado doméstico.

Quando a EBIA for liberada, ela deve entrar pela chave `COD_UPA + NUM_DOM + NUM_UC` (o questionário POF 6 pergunta a
EBIA à pessoa de referência de cada UC).

## Erro-padrão

`estimativas.py` usa os 200 pesos bootstrap (`REP_POF_1` a `REP_POF_200`) com erro-padrão
`sqrt(soma((t_r - t)^2) / 200)`. O dicionário remete a uma nota técnica que não veio na documentação liberada; se ela
indicar outro divisor, basta mudar `DIVISOR` (a troca de 200 por 199 altera o erro-padrão em 0,25%).
