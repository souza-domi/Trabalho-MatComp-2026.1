# Plota a trajetoria apenas com yaw corrigido


import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d
from scipy.spatial import procrustes

from spline2 import t_spline, ax_spline, ay_spline
from leitura import t_vi, cx, cy


inicio = 10
fim = 20

remover_bias = True
alinhar_inicio_plot = True


t_spline = np.array(t_spline, dtype=float)
ax_spline = np.array(ax_spline, dtype=float)
ay_spline = np.array(ay_spline, dtype=float)

t_vi = np.array(t_vi, dtype=float)
cx = np.array(cx, dtype=float)
cy = np.array(cy, dtype=float)


def plotar_trajetoria(inicio, fim):
    duracao = fim - inicio

    # IMU
    mascara_imu = (t_spline >= inicio) & (t_spline <= fim)

    t_janela = t_spline[mascara_imu]
    ax_janela = ax_spline[mascara_imu]
    ay_janela = ay_spline[mascara_imu]

    if remover_bias:
        ax_janela = ax_janela - np.mean(ax_janela)
        ay_janela = ay_janela - np.mean(ay_janela)

    vx = cumulative_trapezoid(ax_janela, t_janela, initial=0)
    vy = cumulative_trapezoid(ay_janela, t_janela, initial=0)

    x = cumulative_trapezoid(vx, t_janela, initial=0)
    y = cumulative_trapezoid(vy, t_janela, initial=0)

    x = x - x[0]
    y = y - y[0]

    traj_imu = np.column_stack((x, y))

    # VICON
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

    # PROCRUSTES
    vicon_alinhada, imu_alinhada, disparidade = procrustes(
        traj_vicon,
        traj_imu
    )

    if alinhar_inicio_plot:
        vicon_plot = vicon_alinhada - vicon_alinhada[0]
        imu_plot = imu_alinhada - imu_alinhada[0]
    else:
        vicon_plot = vicon_alinhada
        imu_plot = imu_alinhada

    print("Remover bias:", remover_bias)
    print("Disparidade Procrustes:", disparidade)

    plt.figure(figsize=(8, 6))

    plt.plot(imu_plot[:, 0], imu_plot[:, 1], label="trajetória reconstruída")
    plt.plot(vicon_plot[:, 0], vicon_plot[:, 1], label="trajetória original (VICON)")

    if alinhar_inicio_plot:
        plt.scatter(0, 0, marker="o", label="início")

    titulo_bias = "com remoção de bias" if remover_bias else "sem remoção de bias"

    plt.xlabel("X normalizado")
    plt.ylabel("Y normalizado")
    plt.title(
        f"Trajetória XY com yaw corrigido + spline ({titulo_bias})\n"
        f"Janela: {inicio}s a {fim}s ({duracao}s) | "
        f"Disparidade: {disparidade:.4f}"
    )

    plt.legend()
    plt.grid(True)
    plt.axis("equal")

    return disparidade


if __name__ == "__main__":
    plotar_trajetoria(inicio, fim)
    plt.show()