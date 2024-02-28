import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import glob

# Reemplace esto con la ruta a su archivo VTK
vtk_file_path = '/home/yo/Documents/Athena-Cversion/bin/output_combined/combined_0200.vtk'

# Leer el archivo VTK
mesh = pv.read(vtk_file_path)

print("Point Data Keys:")
print(mesh.point_data.keys())

# Imprimir las keys de los datos de celdas
print("\nCell Data Keys:")
print(mesh.cell_data.keys())

# Extraer la velocidad en la dirección z (V3)
velocity_z = mesh.point_data['v3']

# Calcular la velocidad máxima y mínima en z
max_vz = np.max(velocity_z)
min_vz = np.min(velocity_z)

# Crear una gráfica que muestre la velocidad máxima y mínima
plt.figure(figsize=(8, 6))
plt.plot(velocity_z, label='Vz')
plt.axhline(y=max_vz, color='r', linestyle='-', label=f'Max [vz] = {max_vz:.2f}')
plt.axhline(y=min_vz, color='b', linestyle='-', label=f'Min [vz] = {min_vz:.2f}')
plt.xlabel('Index')
plt.ylabel('Velocity in z-direction')
plt.title('Maximum and Minimum Velocity in z-direction')
plt.legend()
plt.grid(True)
plt.show()
