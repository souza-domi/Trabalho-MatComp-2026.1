import numpy as np
import matplotlib.pyplot as plt

from spline2 import t_spline, yaw_spline


# ==============================
# CONFIGURAÇÃO DA JANELA
# ==============================

inicio = 35
fim = 65


# ==============================
# DADOS
# ==============================

t = np.asarray(t_spline, dtype=float)
yaw = np.unwrap(np.asarray(yaw_spline, dtype=float))

mascara = (t >= inicio) & (t <= fim)

t_janela = t[mascara]
yaw_janela = yaw[mascara]

# Tempo relativo ao início da janela
t_relativo = t_janela - t_janela[0]

# Variação do yaw em relação ao início da janela
delta_yaw = yaw_janela - yaw_janela[0]

# Converte para graus
delta_yaw_graus = np.rad2deg(delta_yaw)

# Taxa de variação do yaw
taxa_yaw = np.gradient(
    delta_yaw_graus,
    t_relativo
)


# ==============================
# GRÁFICO
# ==============================

plt.figure(figsize=(11, 5))

plt.plot(
    t_relativo,
    taxa_yaw,
    linewidth=2
)

plt.axhline(
    0,
    linestyle="--",
    linewidth=1
)

plt.xlabel("Tempo (s)")
plt.ylabel("Taxa de variação do yaw (graus/s)")

plt.title(
    f"Taxa de variação do yaw\n"
    f"Janela {inicio}s - {fim}s"
)

plt.grid(True)
plt.tight_layout()
plt.show()