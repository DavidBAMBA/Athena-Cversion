import pyvista as pv
import numpy as np
import glob
import matplotlib.pyplot as plt
from scipy.integrate import simps
import re  
import pandas as pd

# Path to the VTK files
directory1 = '/home/yo/Documents/Athena-Cversion/results/results-ATHV2/output_combined_Bsqr'
directory2 = '/home/yo/Documents/Athena-Cversion/results/results-ATHV3/output_combined_Bsqr'
directory3 = '/home/yo/Documents/Athena-Cversion/results/results-ATHV5/output_combined_Bsqr'
directory4 = '/home/yo/Documents/Athena-Cversion/results/results-ATHV5/output_combined_Bsqr'

vtk_files1 = glob.glob(directory1 + '/combined_*.vtk')
vtk_files2 = glob.glob(directory2 + '/combined_*.vtk')
vtk_files3 = glob.glob(directory3 + '/combined_*.vtk')
vtk_files4 = glob.glob(directory4 + '/combined_*.vtk')

# Function to extract the timestep from the filename
def filename_to_time(filename):
    match = re.search(r'combined_(\d+).vtk', filename)
    if match:
        # Convert the timestep number to an integer, then to real time
        time_step = 0.01
        return int(match.group(1)) * time_step
    else:
        return None

# Parameters
ny = 512
nz = 1024
Ly = 0.1
Lz = 0.2

# Lists to store time and integrated magnetic energy
total_magnetic_energy1 = []
total_magnetic_energy2 = []
total_magnetic_energy3 = []
total_magnetic_energy4 = []
times = []  

# Sort files by time and process each one
for vtk_file in sorted(vtk_files1, key=filename_to_time):
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
        total_magnetic_energy1.append(total_energy)
times = []  

for vtk_file in sorted(vtk_files2, key=filename_to_time):
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
        total_magnetic_energy2.append(total_energy)
times = []  

for vtk_file in sorted(vtk_files3, key=filename_to_time):
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
        total_magnetic_energy3.append(total_energy)
times = []  

for vtk_file in sorted(vtk_files4, key=filename_to_time):
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
        total_magnetic_energy4.append(total_energy)


# Calculate the temporal derivative of the dissipated magnetic energy
# Use forward finite difference for the derivative
energy_dissipation_rate1 = np.diff(total_magnetic_energy1) / np.diff(times) 
energy_dissipation_rate2 = np.diff(total_magnetic_energy2) / np.diff(times) 
energy_dissipation_rate3 = np.diff(total_magnetic_energy3) / np.diff(times) 
energy_dissipation_rate4 = np.diff(total_magnetic_energy4) / np.diff(times) 

# Plot the magnetic energy dissipation rate
plt.figure(figsize=(10, 5))
plt.plot(times[:-1], -energy_dissipation_rate1/10.0, label='V2')
plt.plot(times[:-1], -energy_dissipation_rate2/10.0, label='V3')
plt.plot(times[:-1], -energy_dissipation_rate3/10.0, label='V5')
plt.plot(times[:-1], -energy_dissipation_rate4/10.0, label='V6')
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