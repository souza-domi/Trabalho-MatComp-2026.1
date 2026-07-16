
#Código que lê os dados do IMU e do VICON, e organiza as variáveis para análise.

import pandas as pd

# -----------------------------
# IMU
# -----------------------------

imu = pd.read_csv(
    "C:/Users/Domi/Desktop/matcomp/imu1.csv",
    header=None
)



# ordenar pelo tempo
imu = imu.sort_values(by=0)

# remover tempos repetidos
imu = imu.drop_duplicates(subset=0, keep="first")

# reorganizar índices
imu = imu.reset_index(drop=True)

# tempo da IMU
t = imu[0]
t = t - t.iloc[0]

# velocidade angular / giroscópio
gx = imu[4]
gy = imu[5]
gz = imu[6]

# orientação do sensor
roll = imu[1]
pitch = imu[2]
yaw = imu[3]

# aceleração no referencial do sensor
ax = imu[10]
ay = imu[11]
az = imu[12]

# -----------------------------
# VI / VICON - Trajetória Real
# -----------------------------

vi = pd.read_csv(
    "C:/Users/Domi/Desktop/matcomp/vi1.csv",
    header=None
)

# ordenar pelo tempo
vi = vi.sort_values(by=0)
vi = vi.reset_index(drop=True)

# tempo do VI está em nanossegundos
t_vi = vi[0]
t_vi = t_vi - t_vi.iloc[0]
t_vi = t_vi / 1e9

# coordenadas da trajetória real
cx = vi[2]
cy = vi[3]

