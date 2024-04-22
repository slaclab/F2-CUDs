import os, sys
from sys import exit

from klys_indicator import sbstIndicator, klysIndicator

import pydm
from pydm import Display
from pydm.widgets.label import PyDMLabel
from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel
from pydm.widgets.byte import PyDMByteIndicator

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QWidget, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

SELF_PATH = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(*os.path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)

from core.common import bitStatusLabel


# L2: S11-S14, L3: S15-S19, 8x klys per sector
L2 = [str(i) for i in range(11,15)]
L3 = [str(i) for i in range(15,20)]
SECTORS = L2 + L3
KLYSTRONS = [str(i) for i in range(1,9)]

# stations that don't exist
NONEXISTANT_RFS = ['11-3', '14-7', '15-2', '19-7', '19-8']

STATUS_FONT = QFont()
STATUS_FONT.setBold(True)
STATUS_FONT.setPointSize(22)


class F2_CUD_klystrons(Display):

    def __init__(self, parent=None, args=None):
        super(F2_CUD_klystrons, self).__init__(parent=parent, args=args)

        self.setup_injector()
        self.setup_L1()
        self.setup_L2_L3()

        ind_XTCAVF = klysIndicator('20-4', parent=self.ui.cont_XTCAVF)
        ind_XTCAVF.setGeometry(0,0,100,80)

        for plot in [
            self.ui.plot_DL10, self.ui.plot_BC11,
            self.ui.plot_BC14,self.ui.plot_BC20
            ]:

            plot.hideAxis('bottom')

        mdlff_onstat = bitStatusLabel('SIOC:SYS1:ML01:AO489', word_length=1, bit=0)
        mdlff_onstat.text_on = 'Enabled'
        mdlff_onstat.text_off = 'Disabled'
        mdlff_onstat.setFont(STATUS_FONT)
        self.ui.procMonitor.layout().addWidget(mdlff_onstat)

        self.setWindowTitle('FACET-II CUD: RF (Klystrons)')
        
        return

    def setup_injector(self):
        ind_gun   = klysIndicator('10-2', parent=self.ui.cont_gun)
        ind_L0A   = klysIndicator('10-3', parent=self.ui.cont_L0A)
        ind_L0B   = klysIndicator('10-4', parent=self.ui.cont_L0B)
        ind_TCAV0 = klysIndicator('10-5', parent=self.ui.cont_TCAV0)

        for ind in [ind_gun, ind_L0A, ind_L0B, ind_TCAV0]:
            ind.setGeometry(0,0,100,80)

        return

    def setup_L1(self):
        ind_L1SA = klysIndicator(
            '11-1', pv_pdes='KLYS:LI11:11:SSSB_PDES', parent=self.ui.cont_L1SA
            )
        ind_L1SB = klysIndicator(
            '11-2', pv_pdes='KLYS:LI11:21:SSSB_PDES', parent=self.ui.cont_L1SB
            )

        for ind in [ind_L1SA, ind_L1SB]:
            ind.setGeometry(0,0,100,80)
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


    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')
