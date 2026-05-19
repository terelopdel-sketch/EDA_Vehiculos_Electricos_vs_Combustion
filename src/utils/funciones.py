"""
utils.py
========
Funciones auxiliares reutilizables para el EDA:
Vehículos Eléctricos (EV) vs Combustión (ICE) — 2015/2026

Fuente del dataset: fueleconomy.gov (EPA — U.S. Department of Energy)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


# ──────────────────────────────────────────────
# 1. DETECCIÓN DE OUTLIERS
# ──────────────────────────────────────────────

def calcular_outliers(df, columna):
    """
    Calcula los outliers de una columna usando el método IQR.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataset sobre el que calcular los outliers.
    columna : str
        Nombre de la columna a analizar.

    Retorna
    -------
    outliers_izq : pd.DataFrame
        Filas con valores por debajo del límite inferior.
    outliers_der : pd.DataFrame
        Filas con valores por encima del límite superior.

    Ejemplo
    -------
    >>> out_izq, out_der = calcular_outliers(df, 'CO2_Emissions_g_per_mile')
    """
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    lim_inf = Q1 - 1.5 * IQR
    lim_sup = Q3 + 1.5 * IQR

    outliers_izq = df[df[columna] < lim_inf]
    outliers_der = df[df[columna] > lim_sup]

    print(f"=== {columna} ===")
    print(f"Q1: {Q1:.1f} | Q3: {Q3:.1f} | IQR: {IQR:.1f}")
    print(f"Límite inferior: {lim_inf:.1f} | Límite superior: {lim_sup:.1f}")
    print(f"Outliers izquierda: {len(outliers_izq)}")
    print(f"Outliers derecha:   {len(outliers_der)}")

    return outliers_izq, outliers_der


# ──────────────────────────────────────────────
# 2. MEJORA RELATIVA ENTRE DOS VALORES
# ──────────────────────────────────────────────

def mejora_relativa(valor_inicial, valor_final, nombre="", unidad=""):
    """
    Calcula la mejora absoluta y relativa entre dos valores.

    Parámetros
    ----------
    valor_inicial : float
        Valor de partida.
    valor_final : float
        Valor final.
    nombre : str, opcional
        Nombre descriptivo del indicador.
    unidad : str, opcional
        Unidad de medida (ej. 'millas', 'g/milla').

    Retorna
    -------
    mejora_abs : float
        Diferencia absoluta entre valor final e inicial.
    mejora_rel : float
        Diferencia relativa en porcentaje.

    Ejemplo
    -------
    >>> mejora_relativa(157.4, 292.0, "Autonomía EV", "millas")
    """
    mejora_abs = valor_final - valor_inicial
    mejora_rel = ((valor_final / valor_inicial) - 1) * 100

    print(f"=== {nombre} ===")
    print(f"Valor inicial:   {valor_inicial:.1f} {unidad}")
    print(f"Valor final:     {valor_final:.1f} {unidad}")
    print(f"Mejora absoluta: +{mejora_abs:.1f} {unidad}")
    print(f"Mejora relativa: +{mejora_rel:.1f}%")

    return mejora_abs, mejora_rel


# ──────────────────────────────────────────────
# 3. TEST MANN-WHITNEY U ENTRE CATEGORÍAS
# ──────────────────────────────────────────────

def mann_whitney_categorias(df, variable, categoria_col="Vehicle_Category"):
    """
    Aplica el test de Mann-Whitney U entre todos los pares
    de categorías de una variable dada.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataset a analizar.
    variable : str
        Variable numérica a comparar entre grupos.
    categoria_col : str
        Nombre de la columna categórica que define los grupos.
        Por defecto 'Vehicle_Category'.

    Ejemplo
    -------
    >>> mann_whitney_categorias(df, 'CO2_Emissions_g_per_mile')
    """
    categorias = df[categoria_col].unique()
    grupos = {cat: df[df[categoria_col] == cat][variable]
              for cat in categorias}

    print(f"=== Mann-Whitney U — {variable} ===\n")
    cats = list(grupos.items())
    for i, (nombre1, g1) in enumerate(cats):
        for nombre2, g2 in cats[i+1:]:
            stat, p = stats.mannwhitneyu(g1, g2, alternative='two-sided')
            sig = 'Significativa ✅' if p < 0.05 else 'No significativa ❌'
            print(f"  {nombre1} vs {nombre2}:")
            print(f"    U={stat:.0f} | p={p:.6f} → {sig}")
    print()


# ──────────────────────────────────────────────
# 4. HISTOGRAMA + BOXPLOT
# ──────────────────────────────────────────────

def plot_distribucion(df, columna, xlabel, color='r', bins=100, titulo=None, save_path=None):
    """
    Genera un histograma con KDE y un boxplot para una variable numérica.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataset a visualizar.
    columna : str
        Nombre de la columna a graficar.
    xlabel : str
        Etiqueta del eje X del histograma.
    color : str, opcional
        Color de las gráficas. Por defecto 'r' (rojo).
    bins : int, opcional
        Número de bins del histograma. Por defecto 100.
    titulo : str, opcional
        Título del gráfico. Si no se indica, se usa el nombre de la columna.
    save_path : str, opcional
        Ruta donde guardar la imagen.

    """
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    fig.suptitle(titulo if titulo else f"Distribución de {columna}",
                 fontweight='bold')

    sns.histplot(df[columna], kde=True, color=color, bins=bins, ax=axs[0])
    axs[0].set_xlabel(xlabel)
    axs[0].set_ylabel("Número de vehículos")

    sns.boxplot(x=columna, data=df, ax=axs[1])
    axs[1].set_xlabel(xlabel)

    sns.despine()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        
    plt.show()


# ──────────────────────────────────────────────
# 5. RESUMEN ESTADÍSTICO POR CATEGORÍA
# ──────────────────────────────────────────────

def resumen_por_categoria(df, variable, categoria_col="Vehicle_Category"):
    """
    Genera un resumen estadístico de una variable numérica
    agrupado por categoría de vehículo.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataset a analizar.
    variable : str
        Variable numérica a resumir.
    categoria_col : str
        Columna categórica para agrupar. Por defecto 'Vehicle_Category'.

    Retorna
    -------
    resumen : pd.DataFrame
        Tabla con media, mediana, mínimo, máximo y desviación típica.

    Ejemplo
    -------
    >>> resumen_por_categoria(df, 'CO2_Emissions_g_per_mile')
    """
    resumen = df.groupby(categoria_col)[variable].agg(
        media="mean",
        mediana="median",
        minimo="min",
        maximo="max",
        std="std"
    ).round(2)

    print(f"=== Resumen de {variable} por {categoria_col} ===\n")
    print(resumen)

    return resumen
