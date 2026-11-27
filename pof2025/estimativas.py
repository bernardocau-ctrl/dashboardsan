"""Estimativas ponderadas com intervalo de confianca pelos pesos de replicacao (bootstrap) da POF 2024-2025.

O IBGE distribui 200 vetores de pesos bootstrap (REP_POF_1 a REP_POF_200, arquivo PESOS_REPLICACAO). A estimativa
pontual usa PESO_FINAL; o erro-padrao e o desvio-padrao das 200 estimativas replicadas em torno da estimativa pontual,
sqrt(sum((t_r - t)^2) / R). O dicionario remete a uma nota tecnica que nao veio na documentacao liberada; se ela
indicar outro fator (por exemplo, R - 1 no denominador), basta mudar DIVISOR. A diferenca entre R e R - 1 com
R = 200 altera o erro-padrao em 0,25%.

Tipos de estimativa:
  razao(num, den): sum(w*num) / sum(w*den), em %  (ex.: coeficiente de Engel = alimentacao / despesa corrente)
  prop(ind):       sum(w*ind) / sum(w), em %       (ex.: % de familias que recebem Bolsa Familia)
  media(x):        sum(w*x) / sum(w)               (ex.: gasto mensal medio com alimentacao, em R$)
"""
import numpy as np
import pandas as pd

R = 200
DIVISOR = R
REPS = [f'REP_POF_{i}' for i in range(1, R + 1)]


def _theta(df, pesos, tipo, a, b):
    W = df[pesos].to_numpy(dtype=float)                          # n x k
    if tipo == 'razao':
        return 100 * (df[a].to_numpy()[:, None] * W).sum(0) / (df[b].to_numpy()[:, None] * W).sum(0)
    if tipo == 'prop':
        return 100 * (df[a].to_numpy()[:, None] * W).sum(0) / W.sum(0)
    if tipo == 'media':
        return (df[a].to_numpy()[:, None] * W).sum(0) / W.sum(0)
    raise ValueError(tipo)


def estimar(df, tipo, a, b=None):
    """Devolve estimativa, erro-padrao, IC95% (normal) e n da amostra para o subconjunto `df`."""
    t = _theta(df, ['PESO_FINAL'], tipo, a, b)[0]
    tr = _theta(df, REPS, tipo, a, b)
    ep = float(np.sqrt(((tr - t) ** 2).sum() / DIVISOR))
    if not np.isfinite(ep):   # grupo pequeno demais: algum peso replicado zera o denominador
        return {'est': float(t), 'ep': None, 'ic95': [None, None], 'cv': None, 'n': int(len(df))}
    return {'est': float(t), 'ep': ep, 'ic95': [float(t - 1.96 * ep), float(t + 1.96 * ep)], 'cv': float(100 * ep / t) if t else None,
            'n': int(len(df))}


def por_grupo(df, grupo, tipo, a, b=None, total=True):
    """Estimativa por categoria de `grupo` (e o total), como lista de dicionarios."""
    out = []
    if total:
        out.append({'grupo': 'Total', **estimar(df, tipo, a, b)})
    cats = df[grupo].cat.categories if hasattr(df[grupo], 'cat') else sorted(df[grupo].dropna().unique())
    for c in cats:
        sub = df[df[grupo] == c]
        if len(sub):
            out.append({'grupo': str(c), **estimar(sub, tipo, a, b)})
    return out


def diferenca(df, grupo, c1, c2, tipo, a, b=None):
    """Diferenca (c2 - c1) com IC95% pelo bootstrap (as mesmas replicas nas duas estimativas)."""
    s1, s2 = df[df[grupo] == c1], df[df[grupo] == c2]
    t = _theta(s2, ['PESO_FINAL'], tipo, a, b)[0] - _theta(s1, ['PESO_FINAL'], tipo, a, b)[0]
    tr = _theta(s2, REPS, tipo, a, b) - _theta(s1, REPS, tipo, a, b)
    ep = float(np.sqrt(((tr - t) ** 2).sum() / DIVISOR))
    return {'dif': float(t), 'ep': ep, 'ic95': [float(t - 1.96 * ep), float(t + 1.96 * ep)]}
