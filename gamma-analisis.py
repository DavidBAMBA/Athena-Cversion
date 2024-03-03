import pyvista as pv
import numpy as np
import glob
import matplotlib.pyplot as plt
from scipy.integrate import simps
import re  

# Path to the VTK files
directory = '/home/yo/Documents/Athena-Cversion/bin'
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

# Lists to store time and total energy for each timestep
times = []  
total_energy_per_timestep = []

# Process each file
for vtk_file in sorted(vtk_files, key=filename_to_time):
    time = filename_to_time(vtk_file)
    if time is not None:
        times.append(time)

        # Read the mesh from the VTK file
        mesh = pv.read(vtk_file)
        U_b = mesh['G']  # Assuming 'G' is the quantity you want to integrate
        U_b_2d = U_b.reshape(nz, ny)

        # Integrate b^2 over the domain
        dy = Ly / ny
        dz = Lz / nz
        total_energy = np.trapz([np.trapz(U_b_2d[ii, :], dx=dy) for ii in range(nz)], dx=dz)
        total_energy_per_timestep.append(total_energy)

# Calculate the average energy over all timesteps
average_energy = np.mean(total_energy_per_timestep)

# Plotting the result
plt.figure(figsize=(10, 6))
plt.plot(times, total_energy_per_timestep, label='Energy per Timestep')
plt.hlines(average_energy, xmin=min(times), xmax=max(times), colors='r', linestyles='dashed', label='Average Energy')
plt.xlabel('Time')
plt.ylabel('Total Magnetic Energy')
plt.title('Total Magnetic Energy Over Time')
plt.legend()
plt.show()
