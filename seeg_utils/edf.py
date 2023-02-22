# -*- coding: utf-8 -*-
'''EDF file utilities'''

import os
import tkinter as tk
from tkinter import filedialog

import mne
import pyedflib


def get_file_name() -> str:
    root = tk.Tk()
    root.withdraw()
    file_name = filedialog.askopenfilename()
    root.destroy()
    return file_name


def read_edf_header(file_name: str | None = None) -> None:
    if file_name is None:
        fn = get_file_name()
    else:
        fn = file_name

    header = pyedflib.highlevel.read_edf_header(fn)
    print(header.keys())
    print(header['Duration'])
    print(header['SignalHeaders'][0])
    print(header['channels'][0])


def read_nk(file_name: str | None = None) -> None:
    if file_name is None:
        fn = get_file_name()
    else:
        fn = file_name

    raw = mne.io.read_raw_nihon(fn)
    print(raw.info['sfreq'])
