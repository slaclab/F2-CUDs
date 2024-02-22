import os, sys
from sys import exit
from functools import partial
from epics import caput, PV
from datetime import datetime as dt

import pydm
from pydm import Display
from pydm.widgets.label import PyDMLabel
from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QGridLayout, QWidget, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

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

STAT_REG  = QFont('Sans Serif', 18)

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

# stupid magic numbers because I can't find a FBCK HSTA bit decoder
HSTA_FBCK_ON = 268601505
HSTA_FBCK_COMP = 268599457


class F2_CUD_linac(Display):

    def __init__(self, parent=None, args=None):
        super(F2_CUD_linac, self).__init__(parent=parent, args=args)

        SYAG_image = SYAGImg(
            im_ch='CAMR:LI20:100:Image:ArrayData',
            w_ch='CAMR:LI20:100:Image:ArraySize0_RBV',
            parent=self.ui.frame_SYAG
            )
        SYAG_image.readingOrder = 1
        SYAG_image.colorMap = 4
        SYAG_image.setGeometry(5, 5, 490, 240)

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

        ind_LI11 = F2SteeringFeedbackIndicator(
            'LI11:FBCK:26:HSTA', parent=self.ui.cont_LI11FB
            )
        ind_LI18 = F2SteeringFeedbackIndicator(
            'LI18:FBCK:28:HSTA', parent=self.ui.cont_LI18FB
            )
        ind_LI11.setFont(STAT_REG)
        ind_LI18.setFont(STAT_REG)
        ind_LI11.setGeometry(0,0,110,40)
        ind_LI18.setGeometry(0,0,110,40)

        self.setWindowTitle('FACET-II CUD: Linac')

        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')

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


# subclass to flip iamge in X/Y - performance intensive :(
class SYAGImg(PyDMImageView):
    def __init__(self, im_ch, w_ch, parent=None, args=None):
        PyDMImageView.__init__(self, parent=parent, image_channel=im_ch, width_channel=w_ch)

    def process_image(self, image): return np.flip(image)