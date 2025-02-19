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
from PyQt5.QtWidgets import QGridLayout, QWidget, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

# import orbit
from orbit import FacetOrbit, DiffOrbit, BaseOrbit, BPM, FacetSCPBPM
from orbit_view import OrbitView 

from epics import caget, get_pv
from scipy.signal import find_peaks
from skimage.measure import regionprops
from skimage.filters import threshold_mean

# ==== for later =====
# RESOLUTION 9.91
SYAG_CONVERSION = 'CAMR:LI20:100:RESOLUTION'


SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)

from core import beam_refs

ORBIT_DRAW_RATE = 10
ORBIT_POS_SCALE = 1.1
ORBIT_TMIT_MAX = 1.4e10

PV_REF_UPDATE = 'SIOC:SYS1:ML03:AO976'

PV_DTOTR = 'CAMR:LI20:107'
PV_DTOTR_IMG = f'{PV_DTOTR}:Image:ArrayData'
IMG_W = caget(f'{PV_DTOTR}:Image:ArraySize0_RBV')
IMG_H = caget(f'{PV_DTOTR}:Image:ArraySize1_RBV')
MASK = np.ones((IMG_W,IMG_H),dtype=int)

def calc_dtotr_centroid():
    """ get the image centroid from DTOTR2 & determine CUD image ROI """
    IMG_W = get_pv(f'{PV_DTOTR}:Image:ArraySize0_RBV').get()
    IMG_H = get_pv(f'{PV_DTOTR}:Image:ArraySize1_RBV').get()
    image = np.reshape(caget(PV_DTOTR_IMG), (IMG_W,IMG_H), order='F')
    image = image - min(image.flatten())
    mask = (image > threshold_mean(image)).astype(int)
    cy,cx = regionprops(mask, image)[0].centroid
    return cx,cy

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
        SYAG_image.getView().getViewBox().setLimits(
            xMin=0, xMax=caget('CAMR:LI20:100:Image:ArraySize0_RBV')+100,
            yMin=0, yMax=caget('CAMR:LI20:100:Image:ArraySize1_RBV')/2.0
            )

        self.track_dtotr = QTimer(self)
        self.track_dtotr.start()
        self.track_dtotr.setInterval(200)
        self.track_dtotr.timeout.connect(self.set_DTOTR2_ROI)

        # setup S20 orbit
        self.draw_orbit = QTimer(self)
        self.live_orbit = FacetOrbit(
            ignore_bad_bpms=True, rate_suffix='TH', scp_suffix='57',
            name='FACET-II BC20 - DUMP orbit'
            )
        self.live_orbit.bpms = self.S20_BPMs()
        self.live_orbit.connect()        

        cud_orbit = partial(OrbitView,
            parent=self, draw_timer=self.draw_orbit,
            units="mm",  ymin=-ORBIT_POS_SCALE, ymax=ORBIT_POS_SCALE, orbit=self.live_orbit
            )
        self.xOrbitView = cud_orbit(axis="x", name="X", label="X")
        self.yOrbitView = cud_orbit(axis="y", name="Y", label="Y")
        self.yOrbitView.setXLink(self.xOrbitView)
        self.yOrbitView.setYLink(self.xOrbitView)
        self.ui.cont_orbit.layout().addWidget(self.xOrbitView)
        self.ui.cont_orbit.layout().addWidget(self.yOrbitView)
        self.draw_orbit.start()

        self.reference_orbit = None
        self.difference_orbit = None
        ref_update_flag = PyDMChannel(address=PV_REF_UPDATE, value_slot=self.udpate_ref_orbit)
        ref_update_flag.connect()

        self.setWindowTitle('FACET-II CUD: Sector 20')
        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')

    def udpate_ref_orbit(self):
        ref_dict = beam_refs.read_current_refs()
        orbit_fpath, ftype = ref_dict['orbit_s20'], 'Absolute'
        if orbit_fpath != 'NOTSET':
            try:
                self.reference_orbit = BaseOrbit.from_MATLAB_file(orbit_fpath)
                fname = path.split(orbit_fpath)[-1]
                ftype = 'Diff'
                self.difference_orbit = DiffOrbit(self.live_orbit, self.reference_orbit)
                print(f"Reference orbit loaded from file {orbit_fpath}")
            except Exception as e:
                print("Couldn't load orbit from MATLAB file.")
                print("Only MATLAB files created by Orbit Display are supported\n")
                raise(e)
        self.ui.ref_orbit_name.setText(path.split(orbit_fpath)[-1])
        self.ui.label_orbit_type.setText(ftype)

        orbit = self.live_orbit
        if ftype == 'Diff': orbit = DiffOrbit(self.live_orbit, self.reference_orbit)
        self.xOrbitView.set_orbit(orbit)
        self.yOrbitView.set_orbit(orbit)
        return

    def S20_BPMs(self):
        s20_BPMs_SCP = [
            'BPMS:LI20:2050', 'BPMS:LI20:2147', 'BPMS:LI20:2160', 'BPMS:LI20:2223',
            'BPMS:LI20:2235', 'BPMS:LI20:2245', 'BPMS:LI20:2261', 'BPMS:LI20:2278', 
            'BPMS:LI20:2340', 'BPMS:LI20:2360', 'BPMS:LI20:3013', 'BPMS:LI20:3036', 
            'BPMS:LI20:3101', 'BPMS:LI20:3120', 'BPMS:LI20:3340',
            ]
        s20_BPMs_EPICS = [
            "BPMS:LI20:2445", "BPMS:LI20:3156", "BPMS:LI20:3218", "BPMS:LI20:3265",
            "BPMS:LI20:3315"
            ]
        bpms = []
        for bpm_name in s20_BPMs_EPICS:
            bpm = BPM(bpm_name, edef='TH')
            if bpm.name in FacetOrbit.energy_bpms(): bpm.is_energy_bpm = True
            bpms.append(bpm)
        for bpm_name in s20_BPMs_SCP:
            bpm = FacetSCPBPM(bpm_name, suffix='57')
            if bpm.name in FacetOrbit.energy_bpms(): bpm.is_energy_bpm = True
            bpms.append(bpm)
        return bpms

    def set_DTOTR2_ROI(self):
        cx,cy = calc_dtotr_centroid()
        self.ui.live_DTOTR2.getView().getViewBox().setLimits(
            xMin=cx-200, xMax=cx+200, yMin=cy-200, yMax=cy+200
            )
        return

# subclass to flip iamge in X/Y - performance intensive :(
class SYAGImg(PyDMImageView):
    def __init__(self, im_ch, w_ch, parent=None, args=None):
        PyDMImageView.__init__(self, parent=parent, image_channel=im_ch, width_channel=w_ch)

    def process_image(self, image): return np.flip(image)