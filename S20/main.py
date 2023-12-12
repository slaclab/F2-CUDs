import os, sys
from os import path
from sys import exit
import numpy as np
from functools import partial

import pydm
from pydm import Display
from pydm.widgets.label import PyDMLabel
from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel
from pydm.widgets.image import PyDMImageView

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QGridLayout, QWidget, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

from orbit import FacetOrbit, BPM, FacetSCPBPM
from orbit_view import OrbitView 

# ==== for later =====
# RESOLUTION 9.91
SYAG_CONVERSION = 'CAMR:LI20:100:RESOLUTION'


SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)

from core import beam_refs

ORBIT_DRAW_RATE = 10
ORBIT_POS_SCALE = 1
ORBIT_TMIT_MAX = 1.4e10

PV_REF_UPDATE = 'SIOC:SYS1:ML03:AO976'

class F2_CUD_S20(Display):

    def __init__(self, parent=None, args=None):
        super(F2_CUD_S20, self).__init__(parent=parent, args=args)

        SYAG_image = SYAGImg(
            im_ch='CAMR:LI20:100:Image:ArrayData',
            w_ch='CAMR:LI20:100:Image:ArraySize0_RBV',
            parent=self.ui.frame_SYAG
            )
        SYAG_image.readingOrder = 1
        SYAG_image.colorMap = 4
        SYAG_image.setGeometry(5, 5, 490, 240)

        # setup IN10 - TD11 orbit
        self.draw_orbit = QTimer(self)

        s20_BPMs_EPICS = [
            'BPMS:LI20:2050', 'BPMS:LI20:2147', 'BPMS:LI20:2160',
            'BPMS:LI20:2223', 'BPMS:LI20:2235', 'BPMS:LI20:2261', 'BPMS:LI20:2278', 'BPMS:LI20:2340',
            'BPMS:LI20:2360', 'BPMS:LI20:3013', 'BPMS:LI20:3036', 'BPMS:LI20:3101',
            'BPMS:LI20:3120', 'BPMS:LI20:3340'
            ]
        s20_BPMs_SCP = [
            "BPMS:LI20:2445", "BPMS:LI20:3156", "BPMS:LI20:3218",
            "BPMS:LI20:3265", "BPMS:LI20:3315"
            ]

        o = FacetOrbit(
            ignore_bad_bpms=True, rate_suffix='TH', scp_suffix='57',
            name='FACET-II BC20 - DUMP orbit'
            )
        o.bpms = []
        for bpm_name in s20_BPMs_EPICS:
            bpm = BPM(bpm_name, edef='TH')
            if bpm.name in FacetOrbit.energy_bpms(): bpm.is_energy_bpm = True
            o.append(bpm)
        for bpm_name in s20_BPMs_SCP:
            bpm = FacetSCPBPM(bpm_name, suffix='57')
            if bpm.name in FacetOrbit.energy_bpms():
                bpm.is_energy_bpm = True
            o.append(bpm)
        o.connect()
        cud_orbit = partial(OrbitView,
            parent=self, draw_timer=self.draw_orbit.start(),
            units="mm",  ymin=-ORBIT_POS_SCALE, ymax=ORBIT_POS_SCALE, orbit=o
            )

        self.xOrbitView = cud_orbit(axis="x", name="X", label="X")
        self.yOrbitView = cud_orbit(axis="y", name="Y", label="Y")
        self.yOrbitView.setXLink(self.xOrbitView)
        self.yOrbitView.setYLink(self.xOrbitView)
        self.ui.cont_orbit.layout().addWidget(self.xOrbitView)
        self.ui.cont_orbit.layout().addWidget(self.yOrbitView)
        self.draw_orbit.start()

        ref_update_flag = PyDMChannel(address=PV_REF_UPDATE, value_slot=self.update_beam_refs)
        ref_update_flag.connect()

        self.setWindowTitle('FACET-II CUD: Sector 20')
        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')

    def update_beam_refs(self):
        ref_dict = beam_refs.read_current_refs()

        # (1) update SYAG image
        ref_fname_SYAG = ref_dict['img_SYAG']
        self.ui.ts_ref_SYAG.setText(beam_refs.ts_from_ref_fname(ref_fname_SYAG))

        # (2) update DTOTR2 image
        ref_fname_DTOTR2 = ref_dict['img_DTOTR2']
        self.ui.ts_ref_DTOTR2.setText(beam_refs.ts_from_ref_fname(ref_fname_DTOTR2))

        # (3) update BC20-FDMP orbit
        ref_fname_orbit = ref_dict['orbit_s20']
        self.ui.ts_ref_orbit.setText(beam_refs.ts_from_ref_fname(ref_fname_orbit))


        return

# subclass to flip iamge in X/Y - performance intensive :(
class SYAGImg(PyDMImageView):
    def __init__(self, im_ch, w_ch, parent=None, args=None):
        PyDMImageView.__init__(self, parent=parent, image_channel=im_ch, width_channel=w_ch)

    def process_image(self, image): return np.flip(image)