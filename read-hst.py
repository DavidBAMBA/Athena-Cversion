import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



path_hitory = '/home/yo/Documents/Athena-Cversion/bin/id0/2Dks.hst'
path_csv = '/home/yo/Documents/Athena-Cversion/bin/id0/history.csv'

with open(path_hitory, 'r') as hst_file:
    lines = hst_file.readlines()

with open(path_csv, 'w') as csv_file:
    # Escribir el encabezado del CSV
    header = "time,dt,mass,total_E,x1_Mom,x2_Mom,x3_Mom,Gamma,x1_KE,x2_KE,x3_KE,Press,x0_ME,x1_ME,x2_ME,x3_ME,bsq,T00_EM,Gam,U_th,U_b\n"
    csv_file.write(header)
        
    for line in lines:
        if not line.startswith("#"):
            # Reemplazar múltiples espacios por una sola coma
            clean_line = ','.join(line.split())
            csv_file.write(clean_line + '\n')

df = pd.read_csv(path_csv)

c = 300000000
time = df['time'].to_numpy()
gamma = df['Gamma'].to_numpy()
U_th = df['Press'].to_numpy() *c
U_b = df['bsq'].to_numpy()* 4*np.pi*10e-7 * (4)

# Crear una figura y un conjunto de subgráficas
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

ax1.plot(time, gamma, linestyle='-', color='b')
ax1.set_ylabel('<Γ>')
ax1.set_yscale('log')

ax2.plot(time, U_b, linestyle='-', color='r')
ax2.set_ylabel('<U_b>')

ax3.plot(time, U_th, linestyle='-', color='g')
ax3.set_ylabel('<U_th>')
ax3.set_xlabel('Time')

plt.tight_layout()

plt.show()

