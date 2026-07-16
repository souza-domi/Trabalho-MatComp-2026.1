#Código para gerar splines de ax, ay, az, yaw e gz a partir dos dados lidos do arquivo CSV.

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

from leitura import t, gz
from referencialGlobal import ax_global, ay_global, az_global
from yaw_corrigido import yaw_corrigido


t = np.array(t, dtype=float)
gz = np.array(gz, dtype=float)

ax_global = np.array(ax_global, dtype=float)
ay_global = np.array(ay_global, dtype=float)
az_global = np.array(az_global, dtype=float)
yaw_corrigido = np.array(yaw_corrigido, dtype=float)


spline_ax = CubicSpline(t, ax_global)
spline_ay = CubicSpline(t, ay_global)
spline_az = CubicSpline(t, az_global)
spline_yaw = CubicSpline(t, yaw_corrigido)
spline_gz = CubicSpline(t, gz)


t_spline = np.linspace(t[0], t[-1], 100000)


ax_spline = spline_ax(t_spline)
ay_spline = spline_ay(t_spline)
az_spline = spline_az(t_spline)
yaw_spline = spline_yaw(t_spline)
gz_spline = spline_gz(t_spline)


def plot_splines():
    plt.figure()
    plt.plot(t, ax_global, ".", label="ax global original")
    plt.plot(t_spline, ax_spline, label="ax spline")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Aceleração X global (m/s²)")
    plt.legend()
    plt.grid()

    plt.figure()
    plt.plot(t, ay_global, ".", label="ay global original")
    plt.plot(t_spline, ay_spline, label="ay spline")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Aceleração Y global (m/s²)")
    plt.legend()
    plt.grid()

    plt.figure()
    plt.plot(t, np.rad2deg(yaw_corrigido), ".", label="yaw corrigido")
    plt.plot(t_spline, np.rad2deg(yaw_spline), label="yaw spline")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Yaw (graus)")
    plt.legend()
    plt.grid()

    plt.figure()
    plt.plot(t, gz, ".", label="gz original")
    plt.plot(t_spline, gz_spline, label="gz spline")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Giro Z (rad/s)")
    plt.legend()
    plt.grid()

    plt.show()


print("spline2.py executado.")
print("Variáveis prontas:")
print("t_spline")
print("ax_spline, ay_spline, az_spline")
print("yaw_spline")
print("gz_spline")