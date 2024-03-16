import os, sys
from os import path
import numpy as np
from sys import exit
from functools import partial
from epics import caput, PV
from datetime import datetime as dt

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

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)

from klys_indicator import sbstIndicator, klysIndicator
from core.common import bitStatusLabel

SELF_PATH = os.path.dirname(os.path.abspath(__file__))


# TIMESTAMP PVs
# SIOC:SYS1:ML03:CA951 - CA954

# emit/msmt PVs
# SIOC:SYS1:ML03:AO951 - AO971

PV_L0_MSMT     = 'PROF:IN10:571:EMITN_X'
PV_L2_MSMT     = 'WIRE:LI11:614:XRMS'
# PV_L2_TS       = 'SIOC:SYS1:ML03:CA951'
PV_L3_MSMT     = 'WIRE:LI19:144:XRMS'
# PV_L3_TS       = 'SIOC:SYS1:ML03:CA952'
PV_IPWS1_MSMT  = 'WIRE:LI20:3179:XRMS'
# PV_IPWS1_TS    = 'SIOC:SYS1:ML03:CA953'
PV_IPBlen_MSMT = 'CAMR:LI20:107:BLEN'
# PV_IPBlen_TS   = 'SIOC:SYS1:ML03:CA954'

SELF_PATH = os.path.dirname(os.path.abspath(__file__))

# L2: S11-S14, L3: S15-S19, 8x klys per sector
L2 = [str(i) for i in range(11,15)]
L3 = [str(i) for i in range(15,20)]
SECTORS = L2 + L3
KLYSTRONS = [str(i) for i in range(1,9)]

# stations that don't exist
NONEXISTANT_RFS = ['11-3', '14-7', '15-2', '19-7', '19-8']

PV_FB_ENABLE = 'SIOC:SYS1:ML00:AO856'

STYLE_GREEN = """
PyDMLabel {
  border-radius: 2px;
}
PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="0"] {
  background-color: rgb(0,0,10);
  color: rgb(0,255,0);
}
"""

STYLE_YELLOW = """
PyDMLabel {
  border-radius: 2px;
}
PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="0"] {
  background-color: rgb(0,0,10);
  color: rgb(255,255,0);
}
"""


class F2_WFH(Display):

    def __init__(self, parent=None, args=None):
        super(F2_WFH, self).__init__(parent=parent, args=args)

        self.setWindowTitle('FACET-II work-from-home CUD')

        self.SYAG_image = InvertedImage(
            im_ch='CAMR:LI20:100:Image:ArrayData',
            w_ch='CAMR:LI20:100:Image:ArraySize0_RBV',
            parent=self.ui.frame_SYAG
            )
        self.SYAG_image.readingOrder = 1
        self.SYAG_image.colorMap = 4
        # SYAG_image.setGeometry(0,0, 340, 170)

        self.VCCF_image = InvertedImage(
            im_ch='CAMR:LT10:900:Image:ArrayData',
            w_ch='CAMR:LT10:900:Image:ArraySize0_RBV',
            parent=self.ui.frame_vcc
            )
        self.VCCF_image.readingOrder = 1
        self.VCCF_image.colorMap = 4
        self.VCCF_image.colorMapMin = 10.0
        self.VCCF_image.colorMapMax = 60.0
        self.VCCF_image.showAxes = True
        self.VCCF_image.maxRedrawRate = 10
        # VCCF_image.setGeometry(15,85,360,300)
        # VCCF_image.getView().getViewBox().setLimits(
        #     xMin=170, xMax=1340, yMin=110, yMax=1000
        #     )

        DL10E_enable = bitStatusLabel(
            PV_FB_ENABLE, word_length=6, bit=0, parent=self.ui.ind_dl10e)

        BC11E_enable = bitStatusLabel(
            PV_FB_ENABLE, word_length=6, bit=2, parent=self.ui.ind_bc11e)
        BC11BL_enable = bitStatusLabel(
            PV_FB_ENABLE, word_length=6, bit=3, parent=self.ui.ind_bc11bl)

        BC14E_enable = bitStatusLabel(
            PV_FB_ENABLE, word_length=6, bit=1, parent=self.ui.ind_bc14e)
        BC14BL_enable = bitStatusLabel(
            PV_FB_ENABLE, word_length=6, bit=5, parent=self.ui.ind_bc14bl)

        BC20E_enable = bitStatusLabel(
            PV_FB_ENABLE, word_length=6, bit=4, parent=self.ui.ind_bc20e)

        for ind in [
            DL10E_enable,
            BC11E_enable,
            BC11BL_enable,
            BC14E_enable,
            BC14BL_enable,
            BC20E_enable,
            ]:
            ind.setGeometry(0,0,114,27)
            ind.onstyle = STYLE_GREEN
            ind.offstyle = STYLE_YELLOW

        self.L0_msmt     = PyDMChannel(address=PV_L0_MSMT, value_slot=self.msmt_ts_L0)
        self.L2_msmt     = PyDMChannel(address=PV_L2_MSMT, value_slot=self.msmt_ts_L2)
        self.L3_msmt     = PyDMChannel(address=PV_L3_MSMT, value_slot=self.msmt_ts_L3)
        self.IPWS1_msmt  = PyDMChannel(address=PV_IPWS1_MSMT, value_slot=self.msmt_ts_IPWS1)
        self.IPBlen_msmt = PyDMChannel(address=PV_IPBlen_MSMT, value_slot=self.msmt_ts_IPBlen)
        for ch in [self.L0_msmt, self.L2_msmt, self.L3_msmt, self.IPWS1_msmt, self.IPBlen_msmt]:
            ch.connect()

        self.L0_msmt_PV     = PV(PV_L0_MSMT)
        self.L2_msmt_PV     = PV(PV_L2_MSMT)
        self.L3_msmt_PV     = PV(PV_L3_MSMT)
        self.IPWS1_msmt_PV  = PV(PV_IPWS1_MSMT)
        self.IPBlen_msmt_PV = PV(PV_IPBlen_MSMT)

        self.setup_injector()
        self.setup_L1()
        self.setup_L2_L3()

        self.ui.fps_VCC.currentTextChanged.connect(self.update_camera_FPS)
        self.ui.fps_SYAG.currentTextChanged.connect(self.update_camera_FPS)
        self.ui.fps_DTOTR2.currentTextChanged.connect(self.update_camera_FPS)
        self.ui.fps_VCC.setCurrentText('1')
        self.ui.fps_SYAG.setCurrentText('10')
        self.ui.fps_DTOTR2.setCurrentText('10')
        self.update_camera_FPS()

        # ind_XTCAVF = klysIndicator('20-4', parent=self.ui.cont_XTCAVF)
        # ind_XTCAVF.setGeometry(0,0,100,80)

        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')

    def update_camera_FPS(self):
        self.VCCF_image.maxRedrawRate = int(self.ui.fps_VCC.currentText())
        self.SYAG_image.maxRedrawRate = int(self.ui.fps_SYAG.currentText())
        self.ui.live_DTOTR2.maxRedrawRate = int(self.ui.fps_DTOTR2.currentText())
        return

    def msmt_ts_L0(self, value=None, char_value=None):
        self.msmt_ts(self.L0_msmt_PV, self.ui.ts_L0, value=value, char_value=char_value)

    def msmt_ts_L2(self, value=None, char_value=None):
        self.msmt_ts(self.L2_msmt_PV, self.ui.ts_L2, value=value, char_value=char_value)
        
    def msmt_ts_L3(self, value=None, char_value=None, **kw):
        self.msmt_ts(self.L3_msmt_PV, self.ui.ts_L3, value=value, char_value=char_value)

    def msmt_ts_IPWS1(self, value=None, char_value=None, **kw):
        self.msmt_ts(self.IPWS1_msmt_PV, self.ui.ts_IPWS1, value=value, char_value=char_value)

    def msmt_ts_IPBlen(self, value=None, char_value=None, **kw):
        self.msmt_ts(self.IPBlen_msmt_PV, self.ui.ts_IPBlen, value=value, char_value=char_value)

    def msmt_ts(self, PV_msmt_obj, label_obj, value=None, char_value=None, **kw):
        """ temp kludge to update L2, L3 & IP Blen measurement timestamps """
        if not value: caput(PV_ts, "BAD/NULL TIMESTAMP"); return
        ts_str = str(dt.fromtimestamp(PV_msmt_obj.timestamp).strftime('%d-%b-%Y %H:%M'))
        label_obj.setText(ts_str)

    def setup_injector(self):
        ind_gun   = klysIndicator('10-2', parent=self.ui.cont_gun_2)
        ind_L0A   = klysIndicator('10-3', parent=self.ui.cont_L0A_2)
        ind_L0B   = klysIndicator('10-4', parent=self.ui.cont_L0B_2)
        ind_TCAV0 = klysIndicator('10-5', parent=self.ui.cont_TCAV0_2)

        for ind in [ind_gun, ind_L0A, ind_L0B, ind_TCAV0]:
            ind.setGeometry(0,0,60,50)
        return

    def setup_L1(self):
        ind_L1SA = klysIndicator(
            '11-1', pv_pdes='KLYS:LI11:11:SSSB_PDES', parent=self.ui.cont_L1SA
            )
        ind_L1SB = klysIndicator(
            '11-2', pv_pdes='KLYS:LI11:21:SSSB_PDES', parent=self.ui.cont_L1SB
            )

        for ind in [ind_L1SA, ind_L1SB]:
            ind.setGeometry(0,0,60,50)
        return

    def setup_L2_L3(self):

        for linac, container in zip([L2, L3], [self.ui.area_L2, self.ui.area_L3]):
            L = QGridLayout()
            L.setSpacing(5)
            L.setContentsMargins(15,5,15,5)
            container.setLayout(L)

            for s in linac:
                i_sbst = int(s)-11
                sbst = sbstIndicator(s)
                L.addWidget(sbst, 0, i_sbst)

                for k in KLYSTRONS:
                    # exclude 11-1 & 2
                    if s == '11' and k in ['1','2']: continue
                    klys = klysIndicator(f'{s}-{k}')
                    L.addWidget(klys, int(k), i_sbst)
        return


# subclass to flip iamge in X/Y - performance intensive :(
class InvertedImage(PyDMImageView):
    def __init__(self, im_ch, w_ch, parent=None, args=None):
        PyDMImageView.__init__(self, parent=parent, image_channel=im_ch, width_channel=w_ch)

    def process_image(self, image): return np.flip(image)
