# -*- coding: utf-8 -*-

"""
test_seeg_utils
----------------------------------

Tests for `seeg_utils` module.
"""

import pytest


import seeg_utils as su


def test_combine_electrode_files():
    su.combine_electrode_files()


def test_check_trajectories():
    su.combine_electrode_files(check_trajectory=True)


def test_electrodes_to_fcsv():
    su.electrodes_to_fcsv()
