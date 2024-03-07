import pyvista as pv
import numpy as np
import glob
import matplotlib.pyplot as plt
from scipy.integrate import simps
import re  
import pandas as pd

# Path to the VTK files
directory = '/home/yo/Documents/Athena-Cversion/results/results-ATHV2/output_combined_Bsqr'
vtk_files = glob.glob(directory + '/combined_*.vtk')

# Function to extract the timestep from the filename
def filename_to_time(filename):
    match = re.search(r'combined_(\d+).vtk', filename)
    if match:
        # Convert the timestep number to an integer, then to real time
        time_step = 0.02
        return int(match.group(1)) * time_step
    else:
        return None

# Parameters
ny = 512
nz = 1024
Ly = 0.1
Lz = 0.2

# Lists to store time and integrated magnetic energy
times = []  
total_magnetic_energy = []

# Sort files by time and process each one
for vtk_file in sorted(vtk_files, key=filename_to_time):
    time = filename_to_time(vtk_file)
    if time is not None:
        times.append(time)

        # Read the mesh from the VTK file
        mesh = pv.read(vtk_file)
        #print(mesh.point_data.keys())

        U_b = mesh['Bsqr'] 
        U_b_2d = U_b.reshape(nz, ny)

        # Calculate the integral of b^2 over the domain
        bdoty = np.zeros(nz)
        dy = Ly / ny
        for ii in range(nz):
            bdoty[ii] = simps(U_b_2d[ii,:], dx=dy) / Ly
        dz = Lz / nz

        # Total magnetic energy for this timestep
        total_energy = simps(bdoty, dx=dz)
        total_magnetic_energy.append(total_energy)

# Calculate the temporal derivative of the dissipated magnetic energy
# Use forward finite difference for the derivative
energy_dissipation_rate = np.diff(total_magnetic_energy) / np.diff(times) 

# Plot the magnetic energy dissipation rate
plt.figure(figsize=(10, 5))
plt.plot(times[:-1], -energy_dissipation_rate/10.0, label='Magnetic Energy Dissipation Rate')
plt.xlabel('Time')
plt.yscale('log')
plt.ylabel('Magnetic Energy Dissipation Rate')
plt.legend()
plt.show()

""" # Optionally, create a DataFrame and save it to a CSV file
df = pd.DataFrame({
    'Time': times[:-1],
    'Dissipation Rate': -energy_dissipation_rate
})
df.to_csv('/home/yo/Documents/output_combined/magnetic_energy_dissipation_rate.csv', index=False)
 """