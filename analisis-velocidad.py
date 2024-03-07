import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import glob

# Reemplace esto con la ruta a su archivo VTK
vtk_file_path = '/home/yo/Documents/Athena-Cversion/results/results-ATHV2/output_combined_vz/combined_0001.vtk'  


# Leer el archivo VTK
mesh = pv.read(vtk_file_path)


# Extraer la velocidad en la dirección z (V3)
velocity_z = mesh['vz']
velocity_z_2d = velocity_z.reshape(1024, 512)
max_vel = np.max(velocity_z_2d, axis=1)
min_vel = np.min(velocity_z_2d, axis=1)

# Calcular la velocidad máxima y mínima en z
max_vz = np.max(velocity_z)
min_vz = np.min(velocity_z)
print(velocity_z.shape)
y = np.linspace(-0.1, 0.1, 1024)
# Crear una gráfica que muestre la velocidad máxima y mínima
plt.figure(figsize=(6, 6))
plt.plot(y,max_vel, label='MAX[vz]', color='r')
plt.plot(y,min_vel, label='MIN[Vv_z]', color='b')
#plt.axhline(y=max_vz, color='r', linestyle='-', label=f'Max [vz] = {max_vz:.2f}')
#plt.axhline(y=min_vz, color='b', linestyle='-', label=f'Min [vz] = {min_vz:.2f}')
plt.xlabel('z')
plt.ylabel('|Vz|')
plt.legend()
plt.show()
