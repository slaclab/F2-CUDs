import sys
from os import path
from epics import get_pv
from datetime import datetime as dt
from functools import partial
from pydm import Display
from pydm.widgets.label import PyDMLabel
from pydm.widgets.channel import PyDMChannel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
sys.path.append(REPO_ROOT)
from widgets.bitStatusLabel import bitStatusLabel
from widgets.SCPSteeringFBIndicator import SCPSteeringFBIndicator


PV_L0_MSMT     = 'PROF:IN10:571:EMITN_X'
PV_L2_MSMT     = 'WIRE:LI11:614:EMITN_X'
PV_L3_MSMT     = 'WIRE:LI19:144:EMITN_X'
PV_IPWS1_MSMT  = 'WIRE:LI20:3179:XRMS'
PV_IPBlen_MSMT = 'CAMR:LI20:107:BLEN'

PV_FB_ENABLE = 'SIOC:SYS1:ML00:AO856'

STAT_REG  = QFont('Sans Serif', 18)

STYLE_GREEN = """
PyDMLabel {
  border-radius: 0px;
}
PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="0"] {
  background-color: rgb(0,0,10);
  color: rgb(0,255,0);
  border-width: 0px;
}
"""

STYLE_YELLOW = """
PyDMLabel {
  border-radius: 0px;
}
PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="0"] {
  background-color: rgb(0,0,10);
  color: rgb(255,255,0);
  border-color: rgb(180,180,0);
  border-width: 2px;
}
"""


class F2_CUD_linac(Display):

    def __init__(self, parent=None, args=None):
        super(F2_CUD_linac, self).__init__(parent=parent, args=args)

        # connect to emittance & S20 measurement PVs to update timestamps
        self.L0_msmt_PV     = get_pv(PV_L0_MSMT)
        self.L2_msmt_PV     = get_pv(PV_L2_MSMT)
        self.L3_msmt_PV     = get_pv(PV_L3_MSMT)
        self.IPWS1_msmt_PV  = get_pv(PV_IPWS1_MSMT)
        self.IPBlen_msmt_PV = get_pv(PV_IPBlen_MSMT)

        self.L0_msmt = PyDMChannel(
            address=PV_L0_MSMT,
            value_slot=partial(self.msmt_ts, self.L0_msmt_PV, self.ui.ts_L0)
            )
        self.L2_msmt = PyDMChannel(
            address=PV_L2_MSMT,
            value_slot=partial(self.msmt_ts, self.L2_msmt_PV, self.ui.ts_L2)
            )
        self.L3_msmt = PyDMChannel(
            address=PV_L3_MSMT,
            value_slot=partial(self.msmt_ts, self.L3_msmt_PV, self.ui.ts_L3)
            )
        self.IPWS1_msmt = PyDMChannel(
            address=PV_IPWS1_MSMT,
            value_slot=partial(self.msmt_ts, self.IPWS1_msmt_PV, self.ui.ts_IPWS1)
            )
        self.IPBlen_msmt = PyDMChannel(
            address=PV_IPBlen_MSMT,
            value_slot=partial(self.msmt_ts, self.IPBlen_msmt_PV, self.ui.ts_IPBlen)
            )
        for ch in [self.L0_msmt, self.L2_msmt, self.L3_msmt, self.IPWS1_msmt, self.IPBlen_msmt]:
            ch.connect()

        Qbunch_enable = bitStatusLabel(
            'SIOC:SYS1:ML03:AO502', word_length=1, bit=0, parent=self.ui.ind_qfb)
        Qbunch_enable.setGeometry(0,0,70,38)
        Qbunch_enable.setFont(STAT_REG)
        # override default style for bitStatusLabel
        Qbunch_enable.onstyle = STYLE_GREEN
        Qbunch_enable.offstyle = STYLE_YELLOW

        ind_LI11 = SCPSteeringFBIndicator(
            'LI11:FBCK:26:HSTA', parent=self.ui.ind_l2steer)
        ind_LI18 = SCPSteeringFBIndicator(
            'LI18:FBCK:28:HSTA', parent=self.ui.ind_l3steer)
        ind_LI11.setFont(STAT_REG)
        ind_LI18.setFont(STAT_REG)
        ind_LI11.setGeometry(0,0,70,38)
        ind_LI18.setGeometry(0,0,70,38)

        self.setWindowTitle('FACET-II CUD: Linac')
        return 

    def ui_filename(self):
        return path.join(SELF_PATH, 'main.ui')

    def msmt_ts(self, PV_msmt_obj, label_obj, value=None, char_value=None, **kw):
        """ sets the text of <label_obj> to the update timestamp of PV_msmt_obj """
        ts_str = str(dt.fromtimestamp(PV_msmt_obj.timestamp).strftime('%d-%b-%Y %H:%M'))
        label_obj.setText(ts_str)