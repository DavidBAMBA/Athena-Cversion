import pyvista as pv
import numpy as np
import glob
import matplotlib.pyplot as plt
from scipy.integrate import simps
import re  
import pandas as pd

# Path del los archivos vtk
directory = '/home/yo/Documents/Athena-Cversion/bin/output_combined'
vtk_files = glob.glob(directory + '/combined_*.vtk')

def filename_to_time(filename):
    #lee el numero del archivo
    match = re.search(r'combined_(\d+).vtk', filename)
    if match:
        # Convierte el número a un entero y luego a tiempo real
        time_step = 0.02
        return int(match.group(1)) * time_step
    else:
        return None


# Parameters
lamda = 0.1
k = 2*np.pi / lamda 
g = 0.1
delta = 0.01
ny = 512  
nz = 1024 
Ly = 0.1
Lz = 0.2
size_dz = 0.1 #delta z 
n_size_dz = 512
m = 1  #int(Ly/lamda)
f1_values = np.zeros(ny, dtype=complex)
f_t_g  = []  
f_t_b  = []  
f_t_r  = []  
times = []  

for vtk_file in sorted(vtk_files, key=filename_to_time):
    time = filename_to_time(vtk_file)
    if time is not None:
        times.append(time)

    # read vtk files
    mesh = pv.read(vtk_file)

    density = mesh['d'] 
    # 2D mesh of density
    density_2d = density.reshape(nz, ny)
   # Calculate of fourier amplitude of density perturbations
    # Mean Density
    rho_mean = np.zeros(ny)
    dy = Ly / ny
    for ii in range(ny):
        rho_mean[ii] = simps(density_2d[:,ii], dx=dy) / Ly
    
    f_m = np.zeros(nz, dtype=complex)

    # Fourier amplitude
    for ii in range(nz):
        delta_rho = density_2d[ii,:]/rho_mean - 1.0
        y_positions = np.linspace(-0.05, 0.05, ny)
        f_m[ii] = 1/Ly * simps(delta_rho * np.exp(-2j * np.pi * m * y_positions / Ly), dx=dy)
        
    # Mean Fourier amplitude
    dz= Lz / nz
    f_m_mean_green = (1/(0.1))  * simps(np.abs(f_m[256:769]), dx=dz) #delta z = 0.1
    f_m_mean_blue  = (1/(0.05)) * simps(np.abs(f_m[384:641]), dx=dz) #delta z = 0.05
    f_m_mean_red   = (1/(0.02)) * simps(np.abs(f_m[460:564]), dx=dz) #delta z = 0.02

    f_t_g.append(f_m_mean_green)  
    f_t_b.append(f_m_mean_blue)
    f_t_r.append(f_m_mean_red)

data = {'time:': times, 'f_m_mean_g': f_t_g, 'f_m_mean_b': f_t_b, 'f_m_mean_r': f_t_r }
df = pd.DataFrame(data)

csv_filename = 'f_t_values.csv'
df.to_csv(csv_filename, index=False)
print('finished')