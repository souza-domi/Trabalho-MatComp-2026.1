
# Esse código encontra o melhor limiar de |gz| para cada intervalo de tempo, calculando a mediana dos 
#  limiares de cada janela de 10 segundos.


import numpy as np
import matplotlib.pyplot as plt

from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d
from scipy.spatial import procrustes

from spline2 import (
    t_spline,
    ax_spline,
    ay_spline,
    yaw_spline,
    gz_spline
)

from leitura import t_vi, cx, cy


# ============================================================
# CONFIGURAÇÕES
# Altere somente este bloco.
# ============================================================

INICIO_TOTAL = 5
FIM_TOTAL = 55
TAMANHO_JANELA = 10

LIMIAR_MIN = 0.00
LIMIAR_MAX = 0.30
PASSO_LIMIAR = 0.01

SALVAR_GRAFICOS = True


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

t_spline = np.asarray(t_spline, dtype=float)
ax_spline = np.asarray(ax_spline, dtype=float)
ay_spline = np.asarray(ay_spline, dtype=float)
yaw_spline = np.asarray(yaw_spline, dtype=float)
gz_spline = np.asarray(gz_spline, dtype=float)

t_vi = np.asarray(t_vi, dtype=float)
cx = np.asarray(cx, dtype=float)
cy = np.asarray(cy, dtype=float)


# ============================================================
# RESTRIÇÃO CINEMÁTICA
# ============================================================

def aplicar_restricao_cinematica_adaptativa(
    vx_global,
    vy_global,
    yaw,
    gz,
    limiar
):
    cos_yaw = np.cos(yaw)
    sin_yaw = np.sin(yaw)

    # Referencial global -> referencial do veículo
    v_frente = (
        cos_yaw * vx_global
        + sin_yaw * vy_global
    )

    v_lateral = (
        -sin_yaw * vx_global
        + cos_yaw * vy_global
    )

    # Em trechos considerados retilíneos,
    # a componente lateral é anulada.
    mascara_reta = np.abs(gz) < limiar

    v_lateral_corrigida = v_lateral.copy()
    v_lateral_corrigida[mascara_reta] = 0.0

    # Referencial do veículo -> referencial global
    vx_corrigida = (
        cos_yaw * v_frente
        - sin_yaw * v_lateral_corrigida
    )

    vy_corrigida = (
        sin_yaw * v_frente
        + cos_yaw * v_lateral_corrigida
    )

    return vx_corrigida, vy_corrigida


# ============================================================
# CÁLCULO DA DISPARIDADE PARA UMA JANELA E UM LIMIAR
# ============================================================

def calcular_disparidade(inicio, fim, limiar):
    # -----------------------------
    # IMU
    # -----------------------------
    mascara_imu = (
        (t_spline >= inicio)
        & (t_spline <= fim)
    )

    t_janela = t_spline[mascara_imu]
    ax_janela = ax_spline[mascara_imu]
    ay_janela = ay_spline[mascara_imu]
    yaw_janela = yaw_spline[mascara_imu]
    gz_janela = gz_spline[mascara_imu]

    if len(t_janela) < 5:
        return np.nan

    t_janela = t_janela - t_janela[0]

    # Remove o bias das acelerações.
    ax_janela = ax_janela - np.mean(ax_janela)
    ay_janela = ay_janela - np.mean(ay_janela)

    # Primeira integração: aceleração -> velocidade.
    vx = cumulative_trapezoid(
        ax_janela,
        t_janela,
        initial=0
    )

    vy = cumulative_trapezoid(
        ay_janela,
        t_janela,
        initial=0
    )

    # Aplica a restrição cinemática.
    vx, vy = aplicar_restricao_cinematica_adaptativa(
        vx,
        vy,
        yaw_janela,
        gz_janela,
        limiar
    )

    # Remove a deriva linear das velocidades.
    vx = vx - np.linspace(vx[0], vx[-1], len(vx))
    vy = vy - np.linspace(vy[0], vy[-1], len(vy))

    # Segunda integração: velocidade -> posição.
    x = cumulative_trapezoid(
        vx,
        t_janela,
        initial=0
    )

    y = cumulative_trapezoid(
        vy,
        t_janela,
        initial=0
    )

    x = x - x[0]
    y = y - y[0]

    traj_imu = np.column_stack((x, y))

    # -----------------------------
    # VICON
    # -----------------------------
    mascara_vicon = (
        (t_vi >= inicio)
        & (t_vi <= fim)
    )

    t_vi_janela = t_vi[mascara_vicon]
    cx_janela = cx[mascara_vicon]
    cy_janela = cy[mascara_vicon]

    if len(t_vi_janela) < 5:
        return np.nan

    t_vi_janela = t_vi_janela - t_vi_janela[0]
    cx_janela = cx_janela - cx_janela[0]
    cy_janela = cy_janela - cy_janela[0]

    interp_cx = interp1d(
        t_vi_janela,
        cx_janela,
        kind="linear",
        fill_value="extrapolate"
    )

    interp_cy = interp1d(
        t_vi_janela,
        cy_janela,
        kind="linear",
        fill_value="extrapolate"
    )

    cx_interp = interp_cx(t_janela)
    cy_interp = interp_cy(t_janela)

    traj_vicon = np.column_stack(
        (cx_interp, cy_interp)
    )

    try:
        _, _, disparidade = procrustes(
            traj_vicon,
            traj_imu
        )
    except ValueError:
        return np.nan

    if not np.isfinite(disparidade):
        return np.nan

    return float(disparidade)


# ============================================================
# GERAÇÃO DAS JANELAS
# ============================================================

def gerar_janelas():
    janelas = []

    inicio = INICIO_TOTAL

    while inicio + TAMANHO_JANELA <= FIM_TOTAL:
        fim = inicio + TAMANHO_JANELA
        janelas.append((float(inicio), float(fim)))
        inicio += TAMANHO_JANELA

    return janelas


# ============================================================
# TESTE DOS LIMIARES EM TODAS AS JANELAS
# ============================================================

def testar_limiares_por_janela():
    limiares = np.round(
        np.arange(
            LIMIAR_MIN,
            LIMIAR_MAX + PASSO_LIMIAR / 2,
            PASSO_LIMIAR
        ),
        6
    )

    janelas = gerar_janelas()

    resultados = []
    matriz_disparidades = np.full(
        (len(janelas), len(limiares)),
        np.nan
    )

    print("\n==========================================")
    print("TESTE DOS LIMIARES POR JANELA")
    print("==========================================")
    print(
        f"Intervalo total: {INICIO_TOTAL} s a "
        f"{FIM_TOTAL} s"
    )
    print(
        f"Tamanho das janelas: "
        f"{TAMANHO_JANELA} s"
    )
    print(
        f"Quantidade de janelas: "
        f"{len(janelas)}"
    )

    for i, (inicio, fim) in enumerate(janelas):
        print(
            f"\nAnalisando janela "
            f"{inicio:.0f}-{fim:.0f} s..."
        )

        for j, limiar in enumerate(limiares):
            matriz_disparidades[i, j] = calcular_disparidade(
                inicio,
                fim,
                float(limiar)
            )

        disparidades_janela = matriz_disparidades[i]

        if np.all(np.isnan(disparidades_janela)):
            print(
                "Nenhum resultado válido nessa janela."
            )
            continue

        indice_melhor = np.nanargmin(
            disparidades_janela
        )

        melhor_limiar = float(
            limiares[indice_melhor]
        )

        menor_disparidade = float(
            disparidades_janela[indice_melhor]
        )

        resultados.append({
            "inicio": inicio,
            "fim": fim,
            "melhor_limiar": melhor_limiar,
            "menor_disparidade": menor_disparidade
        })

        print(
            f"Melhor limiar = "
            f"{melhor_limiar:.3f} rad/s | "
            f"Disparidade = "
            f"{menor_disparidade:.6f}"
        )

    return (
        limiares,
        janelas,
        resultados,
        matriz_disparidades
    )


# ============================================================
# CÁLCULO DA MEDIANA
# ============================================================

def calcular_limiar_final(resultados):
    melhores_limiares = np.asarray(
        [
            resultado["melhor_limiar"]
            for resultado in resultados
        ],
        dtype=float
    )

    limiar_mediano = float(
        np.median(melhores_limiares)
    )

    return melhores_limiares, limiar_mediano


# ============================================================
# DISPARIDADE MÉDIA E MEDIANA PARA CADA LIMIAR
# ============================================================

def calcular_estatisticas_disparidade(
    matriz_disparidades
):
    disparidade_media = np.nanmean(
        matriz_disparidades,
        axis=0
    )

    disparidade_mediana = np.nanmedian(
        matriz_disparidades,
        axis=0
    )

    desvio_padrao = np.nanstd(
        matriz_disparidades,
        axis=0
    )

    return (
        disparidade_media,
        disparidade_mediana,
        desvio_padrao
    )


# ============================================================
# GRÁFICO 1 — MELHOR LIMIAR EM CADA JANELA
# ============================================================

def plotar_limiar_por_janela(
    resultados,
    limiar_mediano
):
    centros_janelas = [
        (
            resultado["inicio"]
            + resultado["fim"]
        ) / 2
        for resultado in resultados
    ]

    melhores_limiares = [
        resultado["melhor_limiar"]
        for resultado in resultados
    ]

    plt.figure(figsize=(11, 6))

    plt.plot(
        centros_janelas,
        melhores_limiares,
        marker="o",
        linewidth=1.2,
        label="Melhor limiar por janela"
    )

    plt.axhline(
        limiar_mediano,
        linestyle="--",
        linewidth=2,
        label=(
            f"Mediana = "
            f"{limiar_mediano:.3f} rad/s"
        )
    )

    plt.xlabel("Tempo central da janela (s)")
    plt.ylabel("Melhor limiar (rad/s)")

    plt.title(
        "Melhor limiar obtido em cada janela"
    )

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    if SALVAR_GRAFICOS:
        plt.savefig(
            "melhor_limiar_por_janela.png",
            dpi=300,
            bbox_inches="tight"
        )


# ============================================================
# GRÁFICO 2 — HISTOGRAMA DOS MELHORES LIMIARES
# ============================================================

def plotar_histograma(
    melhores_limiares,
    limiar_mediano
):
    bordas = np.arange(
        LIMIAR_MIN - PASSO_LIMIAR / 2,
        LIMIAR_MAX
        + PASSO_LIMIAR
        + PASSO_LIMIAR / 2,
        PASSO_LIMIAR
    )

    plt.figure(figsize=(10, 6))

    plt.hist(
        melhores_limiares,
        bins=bordas,
        edgecolor="black"
    )

    plt.axvline(
        limiar_mediano,
        linestyle="--",
        linewidth=2,
        label=(
            f"Mediana = "
            f"{limiar_mediano:.3f} rad/s"
        )
    )

    plt.xlabel(
        "Melhor limiar de cada janela (rad/s)"
    )
    plt.ylabel("Frequência")

    plt.title(
        "Distribuição dos melhores limiares"
    )

    plt.grid(axis="y")
    plt.legend()
    plt.tight_layout()

    if SALVAR_GRAFICOS:
        plt.savefig(
            "histograma_melhores_limiares.png",
            dpi=300,
            bbox_inches="tight"
        )


# ============================================================
# GRÁFICO 3 — DISPARIDADE × LIMIAR
# ============================================================

def plotar_disparidade_por_limiar(
    limiares,
    disparidade_media,
    disparidade_mediana,
    desvio_padrao,
    limiar_mediano
):
    plt.figure(figsize=(11, 6))

    plt.plot(
        limiares,
        disparidade_media,
        marker="o",
        markersize=4,
        linewidth=1.3,
        label="Disparidade média"
    )

    plt.plot(
        limiares,
        disparidade_mediana,
        linestyle="--",
        linewidth=1.5,
        label="Disparidade mediana"
    )

    plt.fill_between(
        limiares,
        disparidade_media - desvio_padrao,
        disparidade_media + desvio_padrao,
        alpha=0.2,
        label="Desvio padrão"
    )

    plt.axvline(
        limiar_mediano,
        linestyle=":",
        linewidth=2,
        label=(
            f"Limiar final = "
            f"{limiar_mediano:.3f} rad/s"
        )
    )

    plt.xlabel("Limiar de $|g_z|$ (rad/s)")
    plt.ylabel("Disparidade de Procrustes")

    plt.title(
        "Disparidade em função do limiar"
    )

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    if SALVAR_GRAFICOS:
        plt.savefig(
            "disparidade_vs_limiar_janelas.png",
            dpi=300,
            bbox_inches="tight"
        )


# ============================================================
# RESULTADO NO TERMINAL
# ============================================================

def imprimir_resultados(
    resultados,
    melhores_limiares,
    limiar_mediano
):
    print("\n==========================================")
    print("RESULTADO FINAL")
    print("==========================================")

    print(
        f"Janelas válidas analisadas: "
        f"{len(resultados)}"
    )

    print("\nMelhor limiar de cada janela:")

    for resultado in resultados:
        print(
            f"{resultado['inicio']:.0f}-"
            f"{resultado['fim']:.0f} s | "
            f"{resultado['melhor_limiar']:.3f} "
            f"rad/s | "
            f"disparidade = "
            f"{resultado['menor_disparidade']:.6f}"
        )

    print("\nLista dos melhores limiares:")
    print(melhores_limiares.tolist())

    print(
        f"\nLimiar final pela mediana: "
        f"{limiar_mediano:.3f} rad/s"
    )

    if np.isclose(
        limiar_mediano,
        LIMIAR_MIN
    ):
        print(
            "\nATENÇÃO: a mediana ficou no "
            "limite inferior da faixa testada."
        )

    if np.isclose(
        limiar_mediano,
        LIMIAR_MAX
    ):
        print(
            "\nATENÇÃO: a mediana ficou no "
            "limite superior da faixa testada."
        )


# ============================================================
# EXECUÇÃO
# ============================================================

def main():
    (
        limiares,
        janelas,
        resultados,
        matriz_disparidades
    ) = testar_limiares_por_janela()

    if len(resultados) == 0:
        print(
            "\nNenhuma janela válida foi analisada."
        )
        return

    (
        melhores_limiares,
        limiar_mediano
    ) = calcular_limiar_final(
        resultados
    )

    (
        disparidade_media,
        disparidade_mediana,
        desvio_padrao
    ) = calcular_estatisticas_disparidade(
        matriz_disparidades
    )

    imprimir_resultados(
        resultados,
        melhores_limiares,
        limiar_mediano
    )

    plotar_limiar_por_janela(
        resultados,
        limiar_mediano
    )

    plotar_histograma(
        melhores_limiares,
        limiar_mediano
    )

    plotar_disparidade_por_limiar(
        limiares,
        disparidade_media,
        disparidade_mediana,
        desvio_padrao,
        limiar_mediano
    )

    plt.show()


if __name__ == "__main__":
    main()
