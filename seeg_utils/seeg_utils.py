# -*- coding: utf-8 -*-
import os
import tkinter as tk
from tkinter import filedialog

import numpy as np
import pandas as pd


def get_directory() -> str:
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory()
    root.destroy()
    return directory


def fix_trajectory(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    fn = os.path.join(os.path.dirname(file_name), 'trajectories',
                      'traj_'+os.path.basename(file_name))
    print(fn)
    traj_df = read_dat_file(fn)
    dx_traj = traj_df.x.iat[-1] - traj_df.x.iat[0]
    dy_traj = traj_df.y.iat[-1] - traj_df.y.iat[0]
    dz_traj = traj_df.z.iat[-1] - traj_df.z.iat[0]
    maxarg = np.argmax(np.abs([dx_traj, dy_traj, dz_traj]))
    if maxarg == 0:
        dtraj = dx_traj
        ddf = df.x.iat[-1] - df.x.iat[0]
    elif maxarg == 1:
        dtraj = dy_traj
        ddf = df.y.iat[-1] - df.y.iat[0]
    else:
        dtraj = dz_traj
        ddf = df.z.iat[-1] - df.z.iat[0]

    if (dtraj > 0 and ddf > 0) or (dtraj < 0 and ddf < 0):
        # contact 1 in trajectory file is on the surface while
        # contact 1 should be the deep contact in our convention
        df = df[::-1]

    return df


def read_dat_file(file_name: str) -> pd.DataFrame:
    df = pd.DataFrame(columns=['name', 'x', 'y', 'z'])
    name = _electrode_name(os.path.basename(file_name))
    with open(file_name) as f:
        line = f.readline()
        i = 1
        while ('info' not in line):
            if line != '\n':
                x, y, z = np.asarray(line.split(), dtype=float)
                df.loc[i, 'name'] = f'{name}{i}'
                df.loc[i, 'x'] = x
                df.loc[i, 'y'] = y
                df.loc[i, 'z'] = z
                i += 1

            line = f.readline()

    return df


def read_electrode_file(file_name: str,
                        check_trajectory: bool = False) -> pd.DataFrame:
    df = read_dat_file(file_name)
    if check_trajectory:
        df = fix_trajectory(df, file_name)

    return df


def combine_electrode_files(directory: str | None = None,
                            check_trajectory: bool = False) -> None:
    if directory is None:
        directory = get_directory()

    electrodes = pd.DataFrame(columns=['name', 'x', 'y', 'z'])
    with os.scandir(directory) as it:
        for entry in it:
            if entry.name.endswith('.dat') and entry.name != 'electrodes.dat':
                file_name = os.path.join(directory, entry.name)
                df = read_electrode_file(file_name, check_trajectory)
                electrodes = pd.concat([electrodes, df], ignore_index=True)

    file_name = os.path.join(directory, 'electrodes.dat')
    electrodes.to_csv(file_name, index=False, sep=' ', header=False)


def write_fcsv(file_name: str, electrodes: pd.DataFrame) -> None:
    header = '# Markups fiducial file version = 4.10\n'
    header += '# CoordinateSystem = 0\n'
    header += '# columns = id,x,y,z,ow,ox,oy,oz,vis,sel,lock,label,desc,associatedNodeID\n'                                     # noqa
    with open(file_name, 'w') as f:
        f.write(header)
        for i in range(1, electrodes.shape[0]+1):
            line = f"vtkMRMLMarkupsFiducialNode_0,{electrodes.loc[i, 'x']},{electrodes.loc[i, 'y']},{electrodes.loc[i, 'z']},"  # noqa
            line += f"0.000,0.000,0.000,1.000,1,1,0,{electrodes.loc[i, 'name']},,vtkMRMLScalarVolumeNode2\n"                    # noqa
            f.write(line)


def _electrode_name(name: str) -> str:
    for sym in ['^', '_', '-', '.']:
        if sym in name:
            return name.split(sym)[0]

    raise ValueError(f'unable to parse name: {name}')


def electrodes_to_fcsv(directory: str | None = None) -> None:

    if directory is None:
        directory = get_directory()

    with os.scandir(directory) as it:
        for entry in it:
            if entry.name.endswith('.dat') and entry.name != 'electrodes.dat':
                file_name = os.path.join(directory, entry.name)
                df = read_dat_file(file_name)
                file_name = os.path.join(directory,
                                         _electrode_name(entry.name)+'.fcsv')
                write_fcsv(file_name, df)
