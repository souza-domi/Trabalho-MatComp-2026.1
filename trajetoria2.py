# Trajetoria com orientação corrigida + restrição adaptativa

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d
from scipy.spatial import procrustes

from spline2 import t_spline, ax_spline, ay_spline, yaw_spline, gz_spline
from leitura import t_vi, cx, cy


t_vi = np.array(t_vi, dtype=float)
cx = np.array(cx, dtype=float)
cy = np.array(cy, dtype=float)

inicio =15
fim = 25


def aplicar_restricao_cinematica_adaptativa(
    vx_global,
    vy_global,
    yaw,
    gz,
    limiar=0.08
):
    vx_corr = np.zeros_like(vx_global)
    vy_corr = np.zeros_like(vy_global)

    for i in range(len(vx_global)):
        psi = yaw[i]

        # Global -> referencial do carrinho
        v_frente = (
            np.cos(psi) * vx_global[i]
            + np.sin(psi) * vy_global[i]
        )

        v_lateral = (
            -np.sin(psi) * vx_global[i]
            + np.cos(psi) * vy_global[i]
        )

        # Em reta: trava velocidade lateral
        # Em curva/derrapagem: deixa velocidade lateral existir
        if abs(gz[i]) < limiar:
            v_lateral = 0

        # Referencial do carrinho -> global
        vx_corr[i] = (
            np.cos(psi) * v_frente
            - np.sin(psi) * v_lateral
        )

        vy_corr[i] = (
            np.sin(psi) * v_frente
            + np.cos(psi) * v_lateral
        )

    return vx_corr, vy_corr


def plotar_trajetoria(inicio, fim, limiar=0.08):

    duracao = fim - inicio

    # -----------------------------
    # IMU
    # -----------------------------

    mascara_imu = (t_spline >= inicio) & (t_spline <= fim)

    t_janela = t_spline[mascara_imu]
    ax_janela = ax_spline[mascara_imu]
    ay_janela = ay_spline[mascara_imu]
    yaw_janela = yaw_spline[mascara_imu]
    gz_janela = gz_spline[mascara_imu]

    t_janela = t_janela - t_janela[0]

    # Remove bias da aceleração

    ax_janela = ax_janela - np.mean(ax_janela)
    ay_janela = ay_janela - np.mean(ay_janela)

    vx = cumulative_trapezoid(ax_janela, t_janela, initial=0)
    vy = cumulative_trapezoid(ay_janela, t_janela, initial=0)

    vx, vy = aplicar_restricao_cinematica_adaptativa(
    vx,
    vy,
    yaw_janela,
    gz_janela,
    limiar
)

    # Remove deriva linear da velocidade
    vx = vx - np.linspace(vx[0], vx[-1], len(vx))
    vy = vy - np.linspace(vy[0], vy[-1], len(vy))

    x = cumulative_trapezoid(vx, t_janela, initial=0)
    y = cumulative_trapezoid(vy, t_janela, initial=0)

    x = x - x[0]
    y = y - y[0]

    traj_imu = np.column_stack((x, y))

    # -----------------------------
    # VICON
    # -----------------------------

    mascara_vi = (t_vi >= inicio) & (t_vi <= fim)

    t_vi_janela = t_vi[mascara_vi]
    cx_janela = cx[mascara_vi]
    cy_janela = cy[mascara_vi]

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

    traj_vicon = np.column_stack((cx_interp, cy_interp))

    # -----------------------------
    # Procrustes
    # -----------------------------

    vicon_alinhada, imu_alinhada, disparidade = procrustes(
        traj_vicon,
        traj_imu
    )

    print("Disparidade Procrustes:", disparidade)

    # -----------------------------
    # Plot
    # -----------------------------

    plt.figure(figsize=(8, 6))

    vicon_plot = vicon_alinhada - vicon_alinhada[0]
    imu_plot = imu_alinhada - imu_alinhada[0]

    plt.plot(
        imu_plot[:, 0],
        imu_plot[:, 1],
        label="trajetória reconstruída"
    )

    plt.plot(
        vicon_plot[:, 0],
        vicon_plot[:, 1],
        label="trajetória original"
    )

    plt.scatter(0, 0, marker="o", label="início")

    plt.xlabel("X normalizado")
    plt.ylabel("Y normalizado")

    plt.title(
        f"Trajetória XY com restrição cinemática adaptativa\n"
        f"Janela: {inicio}s a {fim}s ({duracao}s) | "
        f"Disparidade: {disparidade:.4f}"
    )

    plt.legend()
    plt.grid()
    plt.axis("equal")

    return disparidade


if __name__ == "__main__":
    plotar_trajetoria(inicio, fim, limiar=0.08)
    plt.show()