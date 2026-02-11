#!/usr/bin/env python3
"""
Plot density evolution from Athena MPI VTK output and create a video.
Usage: python plot_density.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import os
import glob
import re
import struct


def read_vtk_athena(filename):
    """Read Athena VTK structured points binary file."""
    with open(filename, 'rb') as f:
        # Header
        f.readline()  # vtk DataFile Version
        desc = f.readline().decode('ascii')
        f.readline()  # BINARY
        f.readline()  # DATASET STRUCTURED_POINTS

        # Parse time
        time_match = re.search(r'time=\s*([\d.eE+-]+)', desc)
        time = float(time_match.group(1)) if time_match else 0.0

        # DIMENSIONS (nodes = cells + 1)
        dims = list(map(int, f.readline().decode('ascii').split()[1:4]))

        # ORIGIN
        origin = list(map(float, f.readline().decode('ascii').split()[1:4]))

        # SPACING
        spacing = list(map(float, f.readline().decode('ascii').split()[1:4]))

        # CELL_DATA N
        ncells = int(f.readline().decode('ascii').split()[1])

        # SCALARS ... / LOOKUP_TABLE
        f.readline()
        f.readline()

        # Binary data (big-endian float32)
        data = np.frombuffer(f.read(ncells * 4), dtype='>f4')

        nx = max(dims[0] - 1, 1)
        ny = max(dims[1] - 1, 1)
        data = data.reshape((ny, nx))

    return data, origin, spacing, time


def join_vtk_step(run_dir, step, id_dirs):
    """Join VTK files from all MPI processes for a given timestep."""
    pieces = []
    for id_dir in id_dirs:
        id_num = int(re.search(r'id(\d+)', os.path.basename(id_dir)).group(1))
        if id_num == 0:
            fname = os.path.join(id_dir, f'2Dks.{step:04d}.d.vtk')
        else:
            fname = os.path.join(id_dir, f'2Dks-id{id_num}.{step:04d}.d.vtk')

        if not os.path.exists(fname):
            continue

        data, origin, spacing, time = read_vtk_athena(fname)
        pieces.append({
            'data': data,
            'origin': origin,
            'spacing': spacing,
            'time': time,
        })

    if not pieces:
        return None, None, None

    sp = pieces[0]['spacing']
    time = pieces[0]['time']

    # Global domain extents
    x_min = min(p['origin'][0] for p in pieces)
    y_min = min(p['origin'][1] for p in pieces)
    x_max = max(p['origin'][0] + p['data'].shape[1] * p['spacing'][0] for p in pieces)
    y_max = max(p['origin'][1] + p['data'].shape[0] * p['spacing'][1] for p in pieces)

    nx_global = int(round((x_max - x_min) / sp[0]))
    ny_global = int(round((y_max - y_min) / sp[1]))

    global_data = np.zeros((ny_global, nx_global))

    for p in pieces:
        ix = int(round((p['origin'][0] - x_min) / sp[0]))
        iy = int(round((p['origin'][1] - y_min) / sp[1]))
        ny_loc, nx_loc = p['data'].shape
        global_data[iy:iy + ny_loc, ix:ix + nx_loc] = p['data']

    extent = [x_min, x_max, y_min, y_max]
    return global_data, extent, time


def main():
    run_dir = os.path.dirname(os.path.abspath(__file__))
    output_video = os.path.join(run_dir, 'density_evolution.mp4')

    # Find id directories
    id_dirs = sorted(
        glob.glob(os.path.join(run_dir, 'id*')),
        key=lambda x: int(re.search(r'id(\d+)', x).group(1))
    )
    print(f'Found {len(id_dirs)} MPI processes')

    # Count timesteps
    vtk_files = sorted(glob.glob(os.path.join(run_dir, 'id0', '2Dks.*.d.vtk')))
    n_steps = len(vtk_files)
    print(f'Found {n_steps} timesteps')

    # Read first frame
    data0, extent0, t0 = join_vtk_step(run_dir, 0, id_dirs)
    print(f'Global grid: {data0.shape[1]} x {data0.shape[0]} cells')

    # Setup figure
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(
        np.log10(data0),
        origin='lower',
        extent=extent0,
        aspect='equal',
        cmap='inferno',
    )
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, label=r'$\log_{10}(\rho)$')
    ax.set_xlabel('X1')
    ax.set_ylabel('X2')
    title = ax.set_title(f't = {t0:.4f}')
    ax.set_ylim(-0.025, 0.025)
    plt.tight_layout()

    def update(step):
        data, extent, time = join_vtk_step(run_dir, step, id_dirs)
        if data is not None:
            log_data = np.log10(np.clip(data, 1e-10, None))
            im.set_data(log_data)
            im.set_clim(log_data.min(), log_data.max())
            title.set_text(f't = {time:.4f}')
        print(f'  Frame {step}/{n_steps - 1}', end='\r')
        return [im, title]

    # Snapshot at t=2
    target_time = 2.0
    snap_step = None
    for s in range(n_steps):
        _, _, t_s = join_vtk_step(run_dir, s, id_dirs)
        if t_s is not None and t_s >= target_time:
            snap_step = s
            break
    if snap_step is None:
        snap_step = n_steps - 1
    data_last, extent_last, t_last = join_vtk_step(run_dir, snap_step, id_dirs)
    fig_snap, ax_snap = plt.subplots(figsize=(10, 5))
    log_last = np.log10(np.clip(data_last, 1e-10, None))
    im_snap = ax_snap.imshow(
        log_last,
        origin='lower',
        extent=extent_last,
        aspect='equal',
        cmap='inferno',
    )
    fig_snap.colorbar(im_snap, ax=ax_snap, shrink=0.8, label=r'$\log_{10}(\rho)$')
    ax_snap.set_ylim(-0.025, 0.025)
    ax_snap.set_xlabel('X1')
    ax_snap.set_ylabel('X2')
    ax_snap.set_title(f't = {t_last:.4f}')
    plt.tight_layout()
    snapshot_path = os.path.join(run_dir, f'density_t{t_last:.2f}.png')
    fig_snap.savefig(snapshot_path, dpi=200, bbox_inches='tight')
    print(f'Snapshot saved: {snapshot_path}')
    plt.close(fig_snap)

    # Video
    print('Creating video...')
    anim = FuncAnimation(fig, update, frames=range(n_steps), blit=True)
    writer = FFMpegWriter(fps=15, bitrate=3000)
    anim.save(output_video, writer=writer, dpi=150)
    print(f'\nVideo saved: {output_video}')
    plt.close()


if __name__ == '__main__':
    main()
