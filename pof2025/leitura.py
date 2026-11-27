"""Leitura dos microdados da POF 2024-2025 (IBGE, liberacao de 27/11/2026).

Os layouts (larguras e nomes das colunas) sao os do programa oficial "Leitura dos Microdados - R.R"
distribuido pelo IBGE em Programas_de_Leitura_20261127.zip. Os arquivos .txt tem largura fixa e trazem o
ponto decimal escrito, entao os numeros sao lidos como estao.

Uso como modulo:
    from leitura import ler
    mor = ler('MORADOR', zip_dados='.../Dados_20261127.zip', cache='.../cache')
A primeira leitura de cada arquivo grava um .pkl em `cache`; as seguintes leem o .pkl.
"""
import os
import zipfile

import pandas as pd

CHAVE_UC = ['COD_UPA', 'NUM_DOM', 'NUM_UC']
_ID = ['UF', 'ESTRATO_POF', 'TIPO_SITUACAO_REG', 'COD_UPA', 'NUM_DOM', 'NUM_UC']
_FIM = ['PESO', 'PESO_FINAL', 'RENDA_TOTAL']

LAYOUT = {
    'MORADOR': ([2, 4, 1, 9, 2, 1, 2, 2, 1, 3, 1, 14, 14, 10],
                _ID + ['COD_INFORMANTE', 'V010106', 'V010301', 'V010303', 'V010304'] + _FIM),
    'ALUGUEL_ESTIMADO': ([2, 4, 1, 9, 2, 1, 2, 8, 2, 10, 2, 2, 12, 10, 1, 2, 14, 14, 10],
                         _ID + ['QUADRO', 'V9001', 'V9002', 'V8000', 'V9010', 'V9011', 'DEFLATOR', 'V8000_DEFLA',
                                'COD_IMPUT_VALOR', 'FATOR_ANUALIZACAO'] + _FIM),
    'DESPESA_COLETIVA': ([2, 4, 1, 9, 2, 1, 2, 2, 8, 2, 10, 2, 2, 10, 12, 10, 10, 1, 2, 14, 14, 10, 1],
                         _ID + ['QUADRO', 'SEQ', 'V9001', 'V9002', 'V8000', 'V9010', 'V9011', 'V020904', 'DEFLATOR',
                                'V8000_DEFLA', 'V020904_DEFLA', 'COD_IMPUT_VALOR', 'FATOR_ANUALIZACAO'] + _FIM + ['V9012']),
    'CADERNETA_COLETIVA': ([2, 4, 1, 9, 2, 1, 2, 3, 2, 8, 2, 10, 12, 10, 1, 2, 14, 14, 10],
                           _ID + ['QUADRO', 'SEQ', 'SEQ_PAI', 'V9001', 'V9002', 'V8000', 'DEFLATOR', 'V8000_DEFLA',
                                  'COD_IMPUT_VALOR', 'FATOR_ANUALIZACAO'] + _FIM),
    'DESPESA_INDIVIDUAL': ([2, 4, 1, 9, 2, 1, 2, 2, 2, 8, 2, 10, 2, 2, 12, 10, 1, 2, 14, 14, 10, 1],
                           _ID + ['COD_INFORMANTE', 'QUADRO', 'SEQ', 'V9001', 'V9002', 'V8000', 'V9010', 'V9011',
                                  'DEFLATOR', 'V8000_DEFLA', 'COD_IMPUT_VALOR', 'FATOR_ANUALIZACAO'] + _FIM + ['V9012']),
    'RENDIMENTO_TRABALHO': ([2, 4, 1, 9, 2, 1, 2, 2, 1, 2, 8, 1, 1, 10, 10, 10, 10, 2, 2, 12, 10, 10, 10, 10, 1, 2, 14, 14, 10],
                            _ID + ['COD_INFORMANTE', 'QUADRO', 'SUB_QUADRO', 'SEQ', 'V9001', 'V050203', 'V0502031',
                                   'V8500', 'V05021212', 'V05021222', 'V05021232', 'V9010', 'V9011', 'DEFLATOR',
                                   'V8500_DEFLA', 'V05021212_DEFLA', 'V05021222_DEFLA', 'V05021232_DEFLA',
                                   'COD_IMPUT_VALOR', 'FATOR_ANUALIZACAO'] + _FIM),
    'OUTROS_RENDIMENTOS': ([2, 4, 1, 9, 2, 1, 2, 2, 2, 8, 10, 10, 2, 2, 12, 10, 10, 1, 2, 14, 14, 10],
                           _ID + ['COD_INFORMANTE', 'QUADRO', 'SEQ', 'V9001', 'V8500', 'V8501', 'V9010', 'V9011',
                                  'DEFLATOR', 'V8500_DEFLA', 'V8501_DEFLA', 'COD_IMPUT_VALOR', 'FATOR_ANUALIZACAO'] + _FIM),
    'PESOS_REPLICACAO': ([9, 2] + [15] * 200, ['COD_UPA', 'NUM_DOM'] + [f'REP_POF_{i}' for i in range(1, 201)]),
}

# colunas de texto (codigos); as demais viram numero
_TEXTO = {'SUB_QUADRO'}


def ler(nome, zip_dados, cache=None, colunas=None):
    """Le um arquivo de dados da POF 2024-2025 e devolve um DataFrame com os tipos ajustados."""
    nome = nome.upper()
    if nome not in LAYOUT:
        raise KeyError(f'arquivo desconhecido: {nome}; opcoes: {sorted(LAYOUT)}')
    pkl = os.path.join(cache, nome + '.pkl') if cache else None
    if pkl and os.path.exists(pkl):
        df = pd.read_pickle(pkl)
    else:
        larg, nomes = LAYOUT[nome]
        with zipfile.ZipFile(zip_dados) as z:
            df = pd.read_fwf(z.open(nome + '.txt'), widths=larg, names=nomes, header=None, dtype=str)
        for c in df.columns:
            if c not in _TEXTO:
                df[c] = pd.to_numeric(df[c].str.strip(), errors='coerce')
        if pkl:
            os.makedirs(cache, exist_ok=True)
            df.to_pickle(pkl)
    return df[colunas] if colunas else df


def valor_mensal(df, arquivo):
    """Valor mensal deflacionado de cada registro, como na memoria de calculo do IBGE."""
    a = arquivo.upper()
    if a == 'CADERNETA_COLETIVA':
        return df['V8000_DEFLA'] * df['FATOR_ANUALIZACAO'] / 12
    if a == 'DESPESA_INDIVIDUAL':
        m = df['QUADRO'].isin([23, 25, 28, 29, 30, 31, 33])
        return (df['V8000_DEFLA'] * df['FATOR_ANUALIZACAO'] * df['V9011'].where(m, 1)) / 12
    if a == 'DESPESA_COLETIVA':
        m = df['QUADRO'].isin([7, 9])
        return (df['V8000_DEFLA'] * df['FATOR_ANUALIZACAO'] * df['V9011'].where(m, 1)) / 12
    if a == 'RENDIMENTO_TRABALHO':
        return df['V8500_DEFLA'] * df['V9011'] * df['FATOR_ANUALIZACAO'] / 12
    if a == 'OUTROS_RENDIMENTOS':
        m = df['QUADRO'].isin([3, 5, 6, 7])
        return (df['V8500_DEFLA'] * df['FATOR_ANUALIZACAO'] * df['V9011'].where(m, 1)) / 12
    raise KeyError(a)
