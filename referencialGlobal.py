
# Projeção 3D da aceleração do sensor para o referencial global

import numpy as np

from leitura import roll, pitch, ax, ay, az
from yaw_corrigido import yaw_corrigido


# -----------------------------
# Converter para arrays
# -----------------------------

roll = np.array(roll, dtype=float)
pitch = np.array(pitch, dtype=float)
yaw = np.array(yaw_corrigido, dtype=float)

ax = np.array(ax, dtype=float)
ay = np.array(ay, dtype=float)
az = np.array(az, dtype=float)


# -----------------------------
# Converter aceleração de G para m/s²
# -----------------------------

g = 9.80665

ax = ax * g
ay = ay * g
az = az * g


# -----------------------------
# Listas para aceleração global
# -----------------------------

ax_global = []
ay_global = []
az_global = []


# -----------------------------
# Rotação sensor -> global
# -----------------------------

for r, p, y, ax_s, ay_s, az_s in zip(
    roll, pitch, yaw, ax, ay, az
):

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(r), -np.sin(r)],
        [0, np.sin(r),  np.cos(r)]
    ])

    Ry = np.array([
        [np.cos(p), 0, np.sin(p)],
        [0, 1, 0],
        [-np.sin(p), 0, np.cos(p)]
    ])

    Rz = np.array([
        [np.cos(y), -np.sin(y), 0],
        [np.sin(y),  np.cos(y), 0],
        [0, 0, 1]
    ])

    R = Rz @ Ry @ Rx

    a_sensor = np.array([ax_s, ay_s, az_s])

    a_global = R @ a_sensor

    ax_global.append(a_global[0])
    ay_global.append(a_global[1])
    az_global.append(a_global[2])


ax_global = np.array(ax_global)
ay_global = np.array(ay_global)
az_global = np.array(az_global)


print("referencialGlobal.py executado.")
print("Variáveis prontas: ax_global, ay_global, az_global")