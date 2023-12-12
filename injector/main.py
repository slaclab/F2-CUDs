import os, sys
from os import path
from sys import exit
from numpy import flip
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

from orbit import FacetOrbit, BPM
from orbit_view import OrbitView 

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)

from core import beam_refs

ORBIT_DRAW_RATE = 10
ORBIT_POS_SCALE = 1
ORBIT_TMIT_MAX = 1.4e10

PV_REF_UPDATE = 'SIOC:SYS1:ML03:AO976'

class F2_CUD_injector(Display):

    def __init__(self, parent=None, args=None):
        super(F2_CUD_injector, self).__init__(parent=parent, args=args)

        VCCF_image = InvertedImage(
            im_ch='CAMR:LT10:900:Image:ArrayData',
            w_ch='CAMR:LT10:900:Image:ArraySize0_RBV',
            parent=self.ui.frame_cameras
            )
        VCCF_image.readingOrder = 1
        VCCF_image.colorMap = 4
        VCCF_image.colorMapMin = 10.0
        VCCF_image.colorMapMax = 60.0
        VCCF_image.showAxes = True
        VCCF_image.maxRedrawRate = 10
        VCCF_image.setGeometry(15,85,360,300)
        VCCF_image.getView().getViewBox().setLimits(
            xMin=170, xMax=1340, yMin=110, yMax=1000
            )

        CATH_image = InvertedImage(
            im_ch='CTHD:IN10:111:Image:ArrayData',
            w_ch='CTHD:IN10:111:Image:ArraySize0_RBV',
            parent=self.ui.frame_cameras
            )
        CATH_image.readingOrder = 1
        CATH_image.colorMap = 1
        CATH_image.showAxes = True
        CATH_image.maxRedrawRate = 10
        CATH_image.normalizeData = True
        CATH_image.setGeometry(415,85,360,300)
        CATH_image.getView().getViewBox().setLimits(
            xMin=115, xMax=285, yMin=185, yMax=325
            )

        # setup IN10 - TD11 orbit
        self.draw_orbit = QTimer(self)

        inj_BPMs = [
            "BPMS:IN10:221", "BPMS:IN10:371", "BPMS:IN10:425", "BPMS:IN10:511",
            "BPMS:IN10:525", "BPMS:IN10:581", "BPMS:IN10:631", "BPMS:IN10:651",
            "BPMS:IN10:731", "BPMS:IN10:771", "BPMS:IN10:781", "BPMS:LI11:132",
            "BPMS:LI11:201", "BPMS:LI11:265", "BPMS:LI11:301", "BPMS:LI11:312",
            "BPMS:LI11:333", "BPMS:LI11:358", "BPMS:LI11:362", "BPMS:LI11:393"
            ]

        orbit = FacetOrbit(
            ignore_bad_bpms=True, rate_suffix='TH', scp_suffix='57',
            name='FACET-II IN10 - L1 orbit'
            )
        orbit.bpms = []
        for bpm_name in inj_BPMs:
            bpm = BPM(bpm_name, edef='TH')
            if bpm.name in FacetOrbit.energy_bpms(): bpm.is_energy_bpm = True
            orbit.append(bpm)
        orbit.connect()
        cud_orbit = partial(OrbitView,
            parent=self, draw_timer=self.draw_orbit.start(),
            units="mm",  ymin=-ORBIT_POS_SCALE, ymax=ORBIT_POS_SCALE, orbit=orbit
            )

        self.xOrbitView = cud_orbit(axis="x", name="X", label="X")
        self.yOrbitView = cud_orbit(axis="y", name="Y", label="Y")
        self.yOrbitView.setXLink(self.xOrbitView)
        self.yOrbitView.setYLink(self.xOrbitView)
        self.ui.cont_orbit.layout().addWidget(self.xOrbitView)
        self.ui.cont_orbit.layout().addWidget(self.yOrbitView)
        self.draw_orbit.start()

        self.setWindowTitle('FACET-II CUD: Injector')

        ref_update_flag = PyDMChannel(address=PV_REF_UPDATE, value_slot=self.update_beam_refs)
        ref_update_flag.connect()

        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')

    def update_beam_refs(self):
        ref_dict = beam_refs.read_current_refs()

        # (1) update orbit
        ref_fname_orbit = ref_dict['orbit_inj']
        self.ui.ts_ref_orbit.setText(beam_refs.ts_from_ref_fname(ref_fname_orbit))
        return


# subclass to flip iamge in X/Y - performance intensive :(
class InvertedImage(PyDMImageView):
    def __init__(self, im_ch, w_ch, parent=None, args=None):
        PyDMImageView.__init__(self, parent=parent, image_channel=im_ch, width_channel=w_ch)

    def process_image(self, image): return flip(image)
