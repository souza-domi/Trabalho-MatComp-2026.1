import matplotlib.pyplot as plt
import numpy as np

from leitura import t_vi, cx, cy

# -----------------------------
# ESCOLHA DA JANELA
# -----------------------------
inicio = 35
fim = 65

# -----------------------------
# MÁSCARA DA JANELA
# -----------------------------
t_vi = np.array(t_vi)
cx = np.array(cx)
cy = np.array(cy)

mascara = (t_vi >= inicio) & (t_vi <= fim)

# -----------------------------
# TRAJETÓRIA DA JANELA
# -----------------------------
plt.figure(figsize=(7,7))

plt.plot(cx[mascara], cy[mascara], label=f"Trajetória real ({inicio}s - {fim}s)")

plt.scatter(cx[mascara][0], cy[mascara][0],
            color='red', s=60, label="Início")

plt.title(f"Trajetória real\nJanela {inicio}s - {fim}s")

plt.xlabel("x")
plt.ylabel("y")

plt.axis("equal")
plt.grid(True)
plt.legend()

plt.show()