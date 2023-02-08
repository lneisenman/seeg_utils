# -*- coding: utf-8 -*-

"""
test_edf
----------------------------------

Tests for `edf` module.
"""

import pytest


import mne
import seeg_utils as su


def test_read_edf_header():
    su.read_edf_header()
    assert 1 == 0

def test_read_nk():
    su.read_nk()
    assert 1 == 0
