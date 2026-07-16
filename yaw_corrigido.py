import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

from leitura import t, yaw


# ==========================================
# 1. Dados
# ==========================================

t = np.array(t, dtype=float)
yaw_original = np.array(yaw, dtype=float)

# ==========================================
# 2. Garantir yaw em radianos
# ==========================================

if np.nanmax(np.abs(yaw_original)) > 2 * np.pi:
    yaw_original = np.deg2rad(yaw_original)

# ==========================================
# 3. Remover saltos de -pi/pi
# ==========================================

yaw_unwrap = np.unwrap(yaw_original)

# ==========================================
# 4. Filtrar yaw
# ==========================================

janela = 301

if janela >= len(yaw_unwrap):
    janela = len(yaw_unwrap) - 1

if janela % 2 == 0:
    janela -= 1

yaw_corrigido = savgol_filter(
    yaw_unwrap,
    window_length=janela,
    polyorder=3
)

# ==========================================
# 5. Função de plot
# ==========================================

def plot_yaw_corrigido():
    plt.figure(figsize=(10, 5))
    plt.plot(t, np.rad2deg(yaw_unwrap), label="yaw original")
    plt.plot(t, np.rad2deg(yaw_corrigido), label="yaw corrigido")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Yaw (graus)")
    plt.title("Yaw original vs yaw corrigido")
    plt.legend()
    plt.grid(True)
    plt.show()


print("yaw_corrigido.py executado.")
print("Variável pronta: yaw_corrigido")