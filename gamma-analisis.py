import pyvista as pv
import numpy as np
import glob
import matplotlib.pyplot as plt
from scipy.integrate import simps
import re  

# Path to the VTK files
directory = '/home/yo/Documents/Athena-Cversion/results/results-ATHV3/output_combined_G'
vtk_files = glob.glob(directory + '/combined_*.vtk')

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

# Lists to store time and total energy for each timestep
times = []  
Gamma_timestep = []

# Process each file
for vtk_file in sorted(vtk_files, key=filename_to_time):
    time = filename_to_time(vtk_file)
    if time is not None:
        times.append(time)

        # Read the mesh from the VTK file
        mesh = pv.read(vtk_file)
        G = mesh['G']  # Assuming 'G' is the quantity you want to integrate
        G_2d = G.reshape(nz, ny)

        # Integrate b^2 over the domain
        dy = Ly / ny
        dz = Lz / nz
        Gamma = np.trapz([np.trapz(G_2d[ii, :], dx=dy) for ii in range(nz)], dx=dz)
        Gamma_timestep.append(Gamma)

# Calculate the average energy over all timesteps
average_energy = np.mean(Gamma_timestep) 

# Plotting the result
plt.figure(figsize=(10, 6))
plt.plot(times, Gamma_timestep)
plt.hlines(average_energy, xmin=min(times), xmax=max(times), colors='r', linestyles='dashed', label='Average Energy')
plt.xlabel('Time')
plt.ylabel('Gamma')
plt.yscale('log')
plt.show()
