# -*- coding: utf-8 -*-
import os
import tkinter as tk
from tkinter import filedialog

import numpy as np
import pandas as pd


def get_directory():
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory()
    root.destroy()
    return directory


def read_dat_file(file_name):
    df = pd.DataFrame(columns=['name', 'x', 'y', 'z'])
    name = _electrode_name(os.path.basename(file_name))
    with open(file_name) as f:
        line = f.readline()
        i = 1
        while('info' not in line):
            if line != '\n':
                x, y, z = np.asarray(line.split(), dtype=float)
                df.loc[i, 'name'] = f'{name}{i}'
                df.loc[i, 'x'] = x
                df.loc[i, 'y'] = y
                df.loc[i, 'z'] = z
                i += 1

            line = f.readline()

    return df


def combine_electrode_files(directory=None):
    if directory is None:
        directory = get_directory()

    electrodes = pd.DataFrame(columns=['name', 'x', 'y', 'z'])
    with os.scandir(directory) as it:
        for entry in it:
            if entry.name.endswith('.dat') and entry.name != 'electrodes.dat':
                file_name = os.path.join(directory, entry.name)
                df = read_dat_file(file_name)
                electrodes = electrodes.append(df, ignore_index=True)

    file_name = os.path.join(directory, 'electrodes.dat')
    electrodes.to_csv(file_name, index=False, sep=' ', header=False)


def write_fcsv(file_name, electrodes):
    header = '# Markups fiducial file version = 4.10\n'
    header += '# CoordinateSystem = 0\n'
    header += '# columns = id,x,y,z,ow,ox,oy,oz,vis,sel,lock,label,desc,associatedNodeID\n'
    with open(file_name, 'w') as f:
        f.write(header)
        for i in range(1, electrodes.shape[0]+1):
            line = f"vtkMRMLMarkupsFiducialNode_0,{electrodes.loc[i, 'x']},{electrodes.loc[i, 'y']},{electrodes.loc[i, 'z']},"
            line += f"0.000,0.000,0.000,1.000,1,1,0,{electrodes.loc[i, 'name']},,vtkMRMLScalarVolumeNode2\n"
            f.write(line)


def _electrode_name(name):
    for sym in ['^', '_', '-', '.']:
        if sym in name:
            return name.split(sym)[0]

    raise ValueError(f'unable to parse name: {name}')


def electrodes_to_fcsv(directory=None):

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
