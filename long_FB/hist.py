"""
================================================================================
FACET-II long. feedback history plots
@author: Zack Buschmann <zack@slac.stanford.edu>
================================================================================
"""


import os, sys
from os import path
from sys import exit
import time
import numpy as np

from epics import caget

import pydm
from pydm import Display
from pydm.widgets.channel import PyDMChannel

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)


# ==============================================================================
# MAIN PANEL
# ==============================================================================

class F2longHist(Display):

    def __init__(self, parent=None, args=None):
        super(F2longHist, self).__init__(parent=parent, args=args)

        self.ui.L0_energy.getAxis('Axis 1').linkedView().setYRange(-1,1, 1.1)
        self.ui.L0_energy.getAxis('Axis 2').linkedView().setYRange(28, 40)

        self.ui.L1_energy.getAxis('Axis 1').linkedView().setYRange(-2.2, 2.2)
        self.ui.L1_energy.getAxis('Axis 2').linkedView().setYRange(130, 160)

        self.ui.L1_blen.getAxis('Axis 1').linkedView().setYRange(0, 8000)
        self.ui.L1_blen.getAxis('Axis 2').linkedView().setYRange(-32,2)

        self.ui.L2_energy.getAxis('Axis 1').linkedView().setYRange(-4.4, 4.4)
        self.ui.L2_energy.getAxis('Axis 2').linkedView().setYRange(-180, 180)

        self.ui.L2_blen.getAxis('Axis 1').linkedView().setYRange(0, 11000)
        self.ui.L2_blen.getAxis('Axis 2').linkedView().setYRange(-60, -20)

        self.ui.L3_energy.getAxis('Axis 1').linkedView().setYRange(-4.4, 4.4)
        self.ui.L3_energy.getAxis('Axis 2').linkedView().setYRange(-180, 180)

        self.ui.L3_blen.getAxis('Axis 1').linkedView().setYRange(0, 300)

        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'history.ui')
