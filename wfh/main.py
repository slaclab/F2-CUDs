import sys
from os import path
from numpy import flip
from functools import partial
from epics import get_pv
from datetime import datetime as dt

from pydm import Display
from pydm.widgets.label import PyDMLabel
from pydm.widgets.channel import PyDMChannel
from pydm.widgets.image import PyDMImageView

from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)

from widgets.bitStatusLabel import bitStatusLabel
from widgets.klystronStatusIndicator import sbstIndicator, klysIndicator
from widgets.InvertedPyDMImage import InvertedPyDMImage
from widgets.SCPSteeringFBIndicator import SCPSteeringFBIndicator

SELF_PATH = path.dirname(path.abspath(__file__))


PV_L0_MSMT     = 'PROF:IN10:571:EMITN_X'
PV_L2_MSMT     = 'WIRE:LI11:614:EMITN_X'
PV_L3_MSMT     = 'WIRE:LI19:144:EMITN_X'
PV_IPWS1_MSMT  = 'WIRE:LI20:3179:XRMS'
PV_IPBlen_MSMT = 'CAMR:LI20:107:BLEN'

SELF_PATH = path.dirname(path.abspath(__file__))

# L2: S11-S14, L3: S15-S19, 8x klys per sector
L2 = [str(i) for i in range(11,15)]
L3 = [str(i) for i in range(15,20)]
SECTORS = L2 + L3
KLYSTRONS = [str(i) for i in range(1,9)]

# stations that don't exist
NONEXISTANT_RFS = ['11-3', '14-7', '15-2', '19-7', '19-8']

STAT_REG  = QFont('Sans Serif', 18)

class F2_WFH(Display):

    def __init__(self, parent=None, args=None):
        super(F2_WFH, self).__init__(parent=parent, args=args)

        self.setWindowTitle('FACET-II work-from-home CUD')

        self.SYAG_image = InvertedPyDMImage(
            im_ch='CAMR:LI20:100:Image:ArrayData',
            w_ch='CAMR:LI20:100:Image:ArraySize0_RBV',
            parent=self.ui.frame_SYAG
            )
        self.SYAG_image.readingOrder = 1
        self.SYAG_image.colorMap = 1
        # SYAG_image.setGeometry(0,0, 340, 170)

        self.VCCF_image = InvertedPyDMImage(
            im_ch='CAMR:LT10:900:Image:ArrayData',
            w_ch='CAMR:LT10:900:Image:ArraySize0_RBV',
            parent=self.ui.frame_vcc
            )
        self.VCCF_image.readingOrder = 1
        self.VCCF_image.colorMap = 1
        self.VCCF_image.colorMapMin = 10.0
        self.VCCF_image.colorMapMax = 60.0
        self.VCCF_image.showAxes = True
        self.VCCF_image.maxRedrawRate = 10
        # self.VCCF_image.setGeometry(15,85,360,300)
        # self.VCCF_image.getView().getViewBox().setLimits(
        #     xMin=170, xMax=1340, yMin=110, yMax=1000
        #     )

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

        ind_XTCAVF = klysIndicator('20-4', parent=self.ui.cont_XTCAVF, mini=True)
        ind_XTCAVF.setGeometry(0,0,60,50)

        Qbunch_enable = bitStatusLabel(
            'SIOC:SYS1:ML03:AO502', word_length=1, bit=0, parent=self.ui.ind_qfb
            )
        Qbunch_enable.setGeometry(0,0,114,27)
        ind_LI11 = SCPSteeringFBIndicator(
            'LI11:FBCK:26:HSTA', parent=self.ui.ind_l2steer)
        ind_LI18 = SCPSteeringFBIndicator(
            'LI18:FBCK:28:HSTA', parent=self.ui.ind_l3steer)
        ind_LI11.setFont(STAT_REG)
        ind_LI18.setFont(STAT_REG)
        ind_LI11.setGeometry(0,0,114,27)
        ind_LI18.setGeometry(0,0,114,27)

        return

    def ui_filename(self):
        return path.join(SELF_PATH, 'main.ui')

    def update_camera_FPS(self):
        self.VCCF_image.maxRedrawRate = int(self.ui.fps_VCC.currentText())
        self.SYAG_image.maxRedrawRate = int(self.ui.fps_SYAG.currentText())
        self.ui.live_DTOTR2.maxRedrawRate = int(self.ui.fps_DTOTR2.currentText())
        return

    def msmt_ts(self, PV_msmt_obj, label_obj, value=None, char_value=None, **kw):
        """ sets the text of <label_obj> to the update timestamp of PV_msmt_obj """
        ts_str = str(dt.fromtimestamp(PV_msmt_obj.timestamp).strftime('%d-%b-%Y %H:%M'))
        label_obj.setText(ts_str)

    def setup_injector(self):
        ind_gun   = klysIndicator('10-3', parent=self.ui.cont_gun_2, mini=True)
        ind_L0A   = klysIndicator('10-8', parent=self.ui.cont_L0A_2, mini=True)
        ind_L0B   = klysIndicator('10-4', parent=self.ui.cont_L0B_2, mini=True)
        ind_TCAV0 = klysIndicator('10-5', parent=self.ui.cont_TCAV0_2, mini=True)

        for ind in [ind_gun, ind_L0A, ind_L0B, ind_TCAV0]:
            ind.setGeometry(0,0,60,50)
        return

    def setup_L1(self):
        ind_L1SA = klysIndicator(
            '11-1', pv_pdes='KLYS:LI11:11:PREQ', parent=self.ui.cont_L1SA, mini=True
            )
        ind_L1SB = klysIndicator(
            '11-2', pv_pdes='KLYS:LI11:21:PREQ', parent=self.ui.cont_L1SB, mini=True
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
                sbst = sbstIndicator(s, mini=True)
                L.addWidget(sbst, 0, i_sbst)

                for k in KLYSTRONS:
                    # exclude 11-1 & 2
                    if s == '11' and k in ['1','2']: continue
                    klys = klysIndicator(f'{s}-{k}', mini=True)
                    L.addWidget(klys, int(k), i_sbst)
        return
