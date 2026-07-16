
#esse aqui

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d
from scipy.spatial import procrustes

from leitura import t, t_vi, cx, cy
from referencialGlobal import ax_global, ay_global

# -----------------------------
# CONVERTER PARA ARRAY
# -----------------------------

t = np.array(t)
t_vi = np.array(t_vi)

cx = np.array(cx)
cy = np.array(cy)

ax_global = np.array(ax_global)
ay_global = np.array(ay_global)

# -----------------------------
# FUNÇÃO PARA PLOTAR TRAJETÓRIA SEM SPLINE
# -----------------------------
inicio = 80
fim = 90
def plotar_trajetoria(inicio, fim):

    duracao = fim - inicio

    # -----------------------------
    # CORTAR IMU NA JANELA
    # -----------------------------

    mascara_imu = (t >= inicio) & (t <= fim)

    t_janela = t[mascara_imu]
    ax_janela = ax_global[mascara_imu]
    ay_janela = ay_global[mascara_imu]

    t_janela = t_janela - t_janela[0]

    # remover offset da aceleração na janela
    ax_janela = ax_janela - np.mean(ax_janela)
    ay_janela = ay_janela - np.mean(ay_janela)

    # -----------------------------
    # INTEGRAÇÃO POR TRAPÉZIOS
    # -----------------------------

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
    # CORTAR VICON NA MESMA JANELA
    # -----------------------------

    mascara_vi = (t_vi >= inicio) & (t_vi <= fim)

    t_vi_janela = t_vi[mascara_vi]
    cx_janela = cx[mascara_vi]
    cy_janela = cy[mascara_vi]

    t_vi_janela = t_vi_janela - t_vi_janela[0]

    cx_janela = cx_janela - cx_janela[0]
    cy_janela = cy_janela - cy_janela[0]

    # -----------------------------
    # INTERPOLAR VICON NOS TEMPOS DA IMU
    # -----------------------------

    interp_cx = interp1d(
        t_vi_janela,
        cx_janela,
        fill_value="extrapolate"
    )

    interp_cy = interp1d(
        t_vi_janela,
        cy_janela,
        fill_value="extrapolate"
    )

    cx_interp = interp_cx(t_janela)
    cy_interp = interp_cy(t_janela)

    traj_vicon = np.column_stack((cx_interp, cy_interp))

    # -----------------------------
    # PROCRUSTES
    # -----------------------------

    vicon_alinhada, imu_alinhada, disparidade = procrustes(
        traj_vicon,
        traj_imu
    )

    print("Disparidade Procrustes sem spline:", disparidade)

    # -----------------------------
    # GRÁFICO
    # -----------------------------

    plt.figure(figsize=(8, 6))

    plt.plot(
        imu_alinhada[:, 0],
        imu_alinhada[:, 1],
        label="trajetória reconstruída"
    )

    plt.plot(
        vicon_alinhada[:, 0],
        vicon_alinhada[:, 1],
        label="trajetória original"
    )

    plt.xlabel("X normalizado")
    plt.ylabel("Y normalizado")

    plt.title(
        f"Trajetória XY sem spline\n"
        f"Janela: {inicio}s a {fim}s ({duracao}s) | "
        f"Disparidade: {disparidade:.4f}"
    )

    plt.legend()
    plt.grid()
    plt.axis("equal")

    return disparidade

# -----------------------------
# RODAR SOZINHO
# -----------------------------

if __name__ == "__main__":
    plotar_trajetoria(inicio, fim)
    plt.show()