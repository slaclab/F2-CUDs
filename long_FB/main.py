"""
================================================================================
FACET-II LONGITUDINAL FEEDBACK CUD

while there's no MPS interlocks

@author: Zack Buschmann <zack@slac.stanford.edu>
================================================================================
"""


import os, sys
from sys import exit
import time
import numpy as np
import logging
from configparser import ConfigParser

from epics import caget

import pydm
from pydm import Display
from pydm.widgets.label import PyDMLabel
from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import  QGridLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QProgressBar
import sip


# ==============================================================================
# GLOBAL VARIABLES
# ==============================================================================

SELF_PATH = os.path.dirname(os.path.abspath(__file__))

STYLE_GLOBAL = """
background-color: rgb(35,35,40);
color: rgb(255, 255, 255);
"""

STYLE_BITLABEL_ON = """
background-color: rgb(0, 255, 0);
color: rgb(0, 0, 0);
"""

STYLE_BITLABEL_OFF = """
background-color: rgb(255, 0, 0);
color: rgb(255, 255, 255);
"""

STYLE_GAUGE_OFF = """
QProgressBar {
    background-color: #37373c;
    border-radius: 0px;
}
QProgressBar::chunk {
    background-color: #c8c8c8;
    margin: 0.5px;
    width: 2px;
    border-radius: 0px;
}
"""

STYLE_GAUGE_NOM = """
QProgressBar {
    background-color: #37373c;
    border-radius: 0px;
}
QProgressBar::chunk {
    background-color: #00ff00;
    margin: 0.5px;
    width: 2px;
    border-radius: 0px;
}
"""

STYLE_GAUGE_WARN = """
QProgressBar {
    background-color: #37373c;
    border-radius: 0px;
}
QProgressBar::chunk {
    background-color: #ffff00;
    margin: 0.5px;
    width: 2px;
    border-radius: 0px;
}
"""

STYLE_GAUGE_ALARM = """
QProgressBar {
    background-color: #37373c;
    border-radius: 0px;
}
QProgressBar::chunk {
    background-color: #ff0000;
    margin: 0.5px;
    width: 2px;
    border-radius: 0px;
}
"""

STYLE_STAT_NOM = """
background-color: rgb(55,55,60);
color: rgb(230, 230, 230);
"""

STYLE_STAT_ALM = """
background-color: rgb(255, 0, 0);
color: rgb(255, 255, 255);
"""

STYLE_OFF = """
color: rgb(230, 230, 230);
"""

STYLE_NOM = """
color: rgb(0, 255, 0);
"""

STYLE_WARN = """
color: rgb(255, 255, 0);
"""

STYLE_ALARM = """
color: rgb(255, 0, 0);
"""

STATUS_FONT = QFont()
STATUS_FONT.setBold(True)
STATUS_FONT.setPointSize(16)

INF_FONT_NOM = QFont()
INF_FONT_NOM.setPointSize(14)

INF_FONT_ALM = QFont()
INF_FONT_ALM.setPointSize(14)
INF_FONT_ALM.setBold(True)

ACT_GREEN = QColor(144,255,124)
ACT_ORANGE = QColor(255,197,97)
ACT_GREY = QColor(220,220,220)

IND_ENABLE_XYWH = (55, 60,  200, 40)
IND_STATUS_XYWH = (55, 110, 200, 40)

ACT_GAUGE_XYWH = (15, 455, 280, 30)

TWIN_GAUGE_NEG_FWD_XYWH = (155, 445, 136, 20)
TWIN_GAUGE_NEG_BAK_XYWH = (15,  445, 136, 20)
TWIN_GAUGE_POS_FWD_XYWH = (155, 470, 136, 20)
TWIN_GAUGE_POS_BAK_XYWH = (15,  470, 136, 20)

# cadence for status watcher updates in ms
STATUS_WATCHER_INTERVAL = 1000

# absolute tolerance of allowable difference between individual elements
# of a multiknob actuator
MKB_TOL = 1.0


# ==============================================================================
# MAIN PANEL
# ==============================================================================

class facetFeedbackCUD(Display):

    def __init__(self, parent=None, args=None):
        super(facetFeedbackCUD, self).__init__(parent=parent, args=args)
        
        # load global config
        cfgp = ConfigParser()
        cfgp.read(os.path.join(SELF_PATH, 'config.ini'))

        self.fb_names = cfgp.sections()
        self.fb_names.remove('global')

        self.config = {}
        for sc in cfgp.sections():
            self.config[sc] = {}
            for key,val in cfgp.items(sc):
                self.config[sc][key] = val

        # bucket for actuator gauge objects, keep track to
        self.actuator_gauges = {}
        for fb in self.fb_names: self.actuator_gauges[fb] = []

        # connect channel that broadcasts the BC14E, BC20E multiknob name
        # to monitor for chcanges
        self.BC14E_mkb = PyDMChannel(
            address=self.config['BC14E']['mkb'],
            value_slot=self.update_BC14E_acts
            )

        self.BC20E_mkb = PyDMChannel(
            address=self.config['BC20E']['mkb'],
            value_slot=self.update_BC20E_acts
            )

        # # monitor TMIT PVs for each FB
        # self.tmit_watcher = {
        #     'DL10E'  : PV(self.config['DL10E']['tmit']),
        #     'BC11E'  : PV(self.config['BC11E']['tmit']),
        #     'BC11BL' : PV(self.config['BC11BL']['tmit']),
        #     'BC14E'  : PV(self.config['BC14E']['tmit']),
        #     'BC14BL' : PV(self.config['BC14BL']['tmit']),
        #     'BC20E'  : PV(self.config['BC20E']['tmit']),
        #     }

        # keep track of BC14E, BC20E act gauges to update for mkb changes
        self.mkb_gauges = {}

        # mapping between multiknob descriptions and actuator PV
        self.mkb_acts = {}
        self.mkb_acts['BC14E'] = {
            '4AND5' : [
                self.config['BC14E']['act_1'], self.config['BC14E']['act_2']
                ],
            '4AND6' : [
                self.config['BC14E']['act_1'], self.config['BC14E']['act_3']
                ],
            '5AND6' : [
                self.config['BC14E']['act_2'], self.config['BC14E']['act_3']
                ],
            }

        self.mkb_acts['BC20E'] = {
            '3AND4' : [
                self.config['BC20E']['act_1'], self.config['BC20E']['act_2']
                ],
            '3AND5' : [
                self.config['BC20E']['act_1'], self.config['BC20E']['act_3']
                ],
            '4AND5' : [
                self.config['BC20E']['act_2'], self.config['BC20E']['act_3']
                ],
            }

        # mapping between multiknob descriptions and actuation percentage PV
        self.mkb_percent = {}
        self.mkb_percent['BC14E'] = {
            '4AND5' : 'SIOC:SYS1:ML00:CALC148',
            '4AND6' : 'SIOC:SYS1:ML00:CALC148',
            '5AND6' : 'SIOC:SYS1:ML00:CALC149',
            }

        self.mkb_percent['BC20E'] = {
            '3AND4' : 'SIOC:SYS1:ML00:CALC146',
            '3AND5' : 'SIOC:SYS1:ML00:CALC146',
            '4AND5' : 'SIOC:SYS1:ML00:CALC147',
            }

        # bucket for on/off & status indicators
        self.enable_indicators = []
        self.status_indicators = []

        # initialize FB summaries
        # ======================================================================
        self.init_DL10E()
        self.init_BC11E()
        self.init_BC11BL()
        self.init_BC14E()
        self.init_BC14BL()
        self.init_BC20E()

        self.ui.setStyleSheet(STYLE_GLOBAL)

        for plot in [
            self.ui.meas_1, self.ui.meas_2, self.ui.meas_3,
            self.ui.meas_4, self.ui.meas_5, self.ui.meas_6
            ]:
            plot.hideAxis('bottom')
            plot.setMouseEnabled(x=False, y=False)

        # style onOff/status indicators
        for ei in self.enable_indicators:
            ei.setGeometry(*IND_ENABLE_XYWH)
            ei.text_on = 'ENABLED'
            ei.text_off = 'DISABLED'

        for si in self.status_indicators:
            si.setGeometry(*IND_STATUS_XYWH)
            si.text_on = 'RUNNING'
            si.text_off = 'NOT RUNNING'

        # map of FB status indicators, one for actuator, measurement and TMIT
        self.stat_watchers = {
            'DL10E'  : {
                'act':  self.ui.stat_act_1,
                'meas': self.ui.stat_meas_1,
                'tmit': self.ui.stat_tmit_1,
                },
            'BC11E'  : {
                'act':  self.ui.stat_act_2,
                'meas': self.ui.stat_meas_2,
                'tmit': self.ui.stat_tmit_2,
                },
            'BC11BL' : {
                'act':  self.ui.stat_act_3,
                'meas': self.ui.stat_meas_3,
                'tmit': self.ui.stat_tmit_3,
                },
            'BC14E'  : {
                'act':  self.ui.stat_act_4,
                'meas': self.ui.stat_meas_4,
                'tmit': self.ui.stat_tmit_4,
                },
            'BC14BL' : {
                'act':  self.ui.stat_act_5,
                'meas': self.ui.stat_meas_5,
                'tmit': self.ui.stat_tmit_5,
                },
            'BC20E'  : {
                'act':  self.ui.stat_act_6,
                'meas': self.ui.stat_meas_6,
                'tmit': self.ui.stat_tmit_6,
                },
            }

        # initialize actuator/state/TMIT statuses
        self.check_FB_acts()
        self.check_FB_meas()
        self.check_FB_TMIT()

        # intialize and start timer for status watcher
        self.actWatcher = QTimer(self)
        self.actWatcher.start()
        self.actWatcher.setInterval(STATUS_WATCHER_INTERVAL)
        self.actWatcher.timeout.connect(self.check_FB_acts)

        # intialize and start timer for status watcher
        self.measWatcher = QTimer(self)
        self.measWatcher.start()
        self.measWatcher.setInterval(STATUS_WATCHER_INTERVAL)
        self.measWatcher.timeout.connect(self.check_FB_meas)

        # intialize and start timer for status watcher
        self.tmitWatcher = QTimer(self)
        self.tmitWatcher.start()
        self.tmitWatcher.setInterval(STATUS_WATCHER_INTERVAL)
        self.tmitWatcher.timeout.connect(self.check_FB_TMIT)

        # intialize and start timer for actuator severity watcher
        self.actSevrWatcher = QTimer(self)
        self.actSevrWatcher.start()
        self.actSevrWatcher.setInterval(STATUS_WATCHER_INTERVAL)
        self.actSevrWatcher.timeout.connect(self.check_act_level)

        self.setWindowTitle('FACET-II CUD: Longitudinal FB')

        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')

    def check_FB_acts(self):
        """
        check that FB actuators are in range & synced (within tolerance)
        """
        # function switcher for different styles of actuator
        # check_act returns None for OK status, message otherwise
        check_act = {
            'DL10E'  : self.check_act_single,
            'BC11E'  : self.check_act_double,
            'BC11BL' : self.check_act_double,
            'BC14E'  : self.check_act_mkb,
            'BC14BL' : self.check_act_single,
            'BC20E'  : self.check_act_mkb,
            }

        for fb_name in self.fb_names:

            stat = check_act[fb_name](fb_name)

            style = STYLE_STAT_ALM if stat else STYLE_STAT_NOM
            font = INF_FONT_ALM if stat else INF_FONT_NOM
            if not stat: stat = 'ACTUATOR OK'

            self.stat_watchers[fb_name]['act'].setText(stat)
            self.stat_watchers[fb_name]['act'].setStyleSheet(style)
            self.stat_watchers[fb_name]['act'].setFont(font)

        return

    def check_act_single(self, fb_name):
        """
        helper method, check FB actuator status for single-actuator feedbacks
        """
        stat = None

        act_c = caget(self.config[fb_name]['act'])
        act_lo = caget(self.config[fb_name]['act_lo'])
        act_hi = caget(self.config[fb_name]['act_hi'])

        if not act_c:           stat = 'ACTUATOR INVALID'
        elif (act_c <= act_lo): stat = 'ACTUATOR LIMIT LOW'
        elif (act_c >= act_hi): stat = 'ACTUATOR LIMIT HIGH'

        return stat

    def check_act_double(self, fb_name):
        """
        helper method, check FB actuator status for double-actuator feedbacks
        """
        act_lo = caget(self.config[fb_name]['act_lo'])
        act_hi = caget(self.config[fb_name]['act_hi'])
        act_neg = caget(self.config[fb_name]['act_1'])
        act_pos = caget(self.config[fb_name]['act_2'])

        return self._check_2_acts(act_neg, act_pos, act_lo, act_hi)

    def check_act_mkb(self, fb_name):
        """
        helper method, check FB actuator status for multi-actuator feedbacks
        """
        act_lo = caget(self.config[fb_name]['act_lo'])
        act_hi = caget(self.config[fb_name]['act_hi'])

        mkb_type = caget(self.config[fb_name]['mkb']).split('_')[2]
        act_channels = self.mkb_acts[fb_name][mkb_type]
        act_neg = caget(act_channels[0])
        act_pos = caget(act_channels[1])

        return self._check_2_acts(act_neg, act_pos, act_lo, act_hi)

    def _check_2_acts(self, act_neg, act_pos, act_lo, act_hi):
        """
        sub-helper, checks double-actuators within tolerance & synced together
        """
        stat = None

        if (not act_neg) or (not act_pos): stat = 'ACTUATOR INVALID'
        elif (act_neg <= act_lo):          stat = 'ACTUATOR LIMIT LOW'
        elif (act_neg >= act_hi):          stat = 'ACTUATOR LIMIT HIGH'

        if (abs(act_neg) - abs(act_pos)) >= MKB_TOL:
            stat = 'ACTUATOR MISMATCH'

        return stat

    def check_act_level(self):

        # color actuation labels to match the nominal/warning/alarm
        # regions of the PyDMAnalogIndicator
        pct_acts = [
            self.ui.act_1_pct, self.ui.act_2_pct, self.ui.act_4_pct, self.ui.act_6_pct
            ]
        for act_label in pct_acts:
            val = abs(int(act_label.text().replace('%', '')))
            if val <= 70.0: act_label.setStyleSheet(STYLE_NOM)
            elif val <= 90.0: act_label.setStyleSheet(STYLE_WARN)
            else:           act_label.setStyleSheet(STYLE_ALARM)

        # BC11BL_warn_lo,  BC11BL_warn_hi = -50, -10
        # BC11BL_alarm_lo, BC11BL_alarm_hi = -55, -5
        # BC14BL_warn_lo,  BC14BL_warn_hi = -50, -10
        # BC14BL_alarm_lo, BC14BL_alarm_hi = -55, -5
        warn_lo,  warn_hi = -50, -10
        alarm_lo, alarm_hi = -55, -5
        for act_label in [self.ui.act_3_deg, self.ui.act_5_deg]:
            val = act_label.value
            if (val <= warn_hi) or (val >= warn_lo):
                act_label.setStyleSheet(STYLE_NOM)
            elif (val <= alarm_hi) or (val >= alarm_lo):
                act_label.setStyleSheet(STYLE_WARN)
            elif (val > alarm_hi) or (val < alarm_lo):
                act_label.setStyleSheet(STYLE_ALARM)
        return

    def check_FB_meas(self):
        """
        check that BPM/BLEN measurement state is within tolerance
        """
        for fb_name in self.fb_names:
            stat = None

            meas = caget(self.config[fb_name]['meas'])
            set_lo = caget(self.config[fb_name]['set_lo'])
            set_hi = caget(self.config[fb_name]['set_hi'])

            if fb_name == 'BC14BL': meas /= 1.e9
                # set_lo *= 1.e9
                # set_hi *= 1.e9

            if not meas:            stat = 'STATE INVALID'
            elif (meas <= set_lo):  stat = 'STATE LIMIT LOW'
            elif (meas >= set_hi):  stat = 'STATE LIMIT HIGH'

            style = STYLE_STAT_ALM if stat else STYLE_STAT_NOM
            font = INF_FONT_ALM if stat else INF_FONT_NOM
            if not stat: stat = 'STATE OK'

            self.stat_watchers[fb_name]['meas'].setText(stat)
            self.stat_watchers[fb_name]['meas'].setStyleSheet(style)
            self.stat_watchers[fb_name]['meas'].setFont(font)

        return stat

    def check_FB_TMIT(self):
        """
        check for good TMIT on the associatd BPM for each FB
        if TMIT is high/low, set a status message
        """
        for fb_name in self.fb_names:
            stat = None

            # normalize tmit as upper/lower bounds are in units of 1e9 Nel
            tmit = caget(self.config[fb_name]['tmit']) / 1.e9
            tmit_lo = caget(self.config[fb_name]['tmit_lo'])
            tmit_hi = caget(self.config[fb_name]['tmit_hi'])

            if not tmit:            stat = 'TMIT INVALID'
            elif (tmit <= tmit_lo): stat = 'TMIT LOW'
            elif (tmit >= tmit_hi): stat = 'TMIT HIGH'

            style = STYLE_STAT_ALM if stat else STYLE_STAT_NOM
            font = INF_FONT_ALM if stat else INF_FONT_NOM
            if not stat: stat = 'TMIT OK'

            self.stat_watchers[fb_name]['tmit'].setText(stat)
            self.stat_watchers[fb_name]['tmit'].setStyleSheet(style)
            self.stat_watchers[fb_name]['tmit'].setFont(font)

        return

    def init_DL10E(self):
        """
        initialize the DL10E section of the CUD
        """
        DL10E_enable = bitStatusLabel(
            self.config['global']['fb_enable'],
            word_length=6, bit=0, parent=self.ui.FB_1_DL10E
            )
        DL10E_status = bitStatusLabel(
            self.config['global']['fb_status'],
            word_length=6, bit=0, parent=self.ui.FB_1_DL10E
            )
        self.enable_indicators.append(DL10E_enable)
        self.status_indicators.append(DL10E_status)

        act_min = caget(self.config['DL10E']['act_lo'])
        act_max = caget(self.config['DL10E']['act_hi'])

        self.ui.act_1_hist.setMinYRange(act_min)
        self.ui.act_1_hist.setMaxYRange(act_max)

        return


    def init_BC11E(self):
        """
        initialize the BC11E section of the CUD
        """
        BC11E_enable = bitStatusLabel(
            self.config['global']['fb_enable'],
            word_length=6, bit=2, parent=self.ui.FB_2_BC11E
            )
        BC11E_status = bitStatusLabel(
            self.config['global']['fb_status'],
            word_length=6, bit=2, parent=self.ui.FB_2_BC11E
            )
        self.enable_indicators.append(BC11E_enable)
        self.status_indicators.append(BC11E_status)

        act_min = caget(self.config['BC11E']['act_lo'])
        act_max = caget(self.config['BC11E']['act_hi'])

        self.ui.act_2_hist.setMinYRange(act_min)
        self.ui.act_2_hist.setMaxYRange(act_max)

        return

    def init_BC11BL(self):
        """
        initialize the BC11BL section of the CUD
        """
        BC11BL_enable = bitStatusLabel(
            self.config['global']['fb_enable'],
            word_length=6, bit=3, parent=self.ui.FB_3_BC11BL
            )
        BC11BL_status = bitStatusLabel(
            self.config['global']['fb_status'],
            word_length=6, bit=3, parent=self.ui.FB_3_BC11BL
            )
        self.enable_indicators.append(BC11BL_enable)
        self.status_indicators.append(BC11BL_status)

        # BC11BL actuator has a negative range
        # use absolute value so the linearGauge renders correctly
        # and switch acuator low/high limitss
        act_min = caget(self.config['BC11BL']['act_hi'])
        act_max = caget(self.config['BC11BL']['act_lo'])

        self.ui.act_3_deg.setStyleSheet(STYLE_NOM)

        self.ui.act_3_hist.setMinYRange(act_min)
        self.ui.act_3_hist.setMaxYRange(act_max)

        return

    def init_BC14E(self):
        """
        initialize the BC14E section of the CUD
        """
        BC14E_enable = bitStatusLabel(
            self.config['global']['fb_enable'],
            word_length=6, bit=1, parent=self.ui.FB_4_BC14E
            )
        BC14E_status = bitStatusLabel(
            self.config['global']['fb_status'],
            word_length=6, bit=1, parent=self.ui.FB_4_BC14E
            )
        self.enable_indicators.append(BC14E_enable)
        self.status_indicators.append(BC14E_status)

        act_min = caget(self.config['BC14E']['act_lo'])
        act_max = caget(self.config['BC14E']['act_hi'])

        # read multiknob description -- has the format BC14_ENERGY_XANDY
        mkb_type = caget(self.config['BC14E']['mkb']).split('_')[2]

        # set appropriate channel on the actuation indicator
        PV_act_pct = self.mkb_percent['BC14E'][mkb_type]
        self.ui.act_4_pct.channel = PV_act_pct
        self.ui.BC14E_act.channel = PV_act_pct

        self.ui.act_4_hist.addYChannel(
            y_channel=self.mkb_acts['BC14E'][mkb_type][1], color=ACT_GREY
            )
        self.ui.act_4_hist.addYChannel(
            y_channel=self.mkb_acts['BC14E'][mkb_type][0], color=ACT_GREY
            )

        # act_min = caget(self.config['BC14E']['act_lo'])
        # act_max = caget(self.config['BC14E']['act_hi'])
        self.ui.act_4_hist.setMinYRange(-180.0)
        self.ui.act_4_hist.setMaxYRange(180.0)
        
        return

    def update_BC14E_acts(self):
        """
        value change slot for multiknob descriptor PV
        removes multiknob linearGauges and reinitializes with new actuators
        corresponding to the new multiknob
        """
        # udpate actuation indicator PV
        mkb_type = caget(self.config['BC14E']['mkb']).split('_')[2]
        PV_act_pct = self.mkb_percent['BC14E'][mkb_type]
        self.ui.act_4_pct.channel = PV_act_pct
        self.ui.BC14e_act.channel = PV_act_pct

        # update actuator history plot!
        return

    def init_BC14BL(self):
        """
        initialize the BC14BL section of the CUD
        """
        BC14BL_enable = bitStatusLabel(
            self.config['global']['fb_enable'],
            word_length=6, bit=5, parent=self.ui.FB_5_BC14BL
            )
        BC14BL_status = bitStatusLabel(
            self.config['global']['fb_status'],
            word_length=6, bit=5, parent=self.ui.FB_5_BC14BL
            )
        self.enable_indicators.append(BC14BL_enable)
        self.status_indicators.append(BC14BL_status)

        # act_min = caget(self.config['BC14BL']['act_lo'])
        # act_max = caget(self.config['BC14BL']['act_hi'])
        act_min = 0.0
        act_max = 180.0

        self.ui.act_5_deg.setStyleSheet(STYLE_NOM)

        # self.ui.act_5_hist.setMinYRange(0.0)
        # self.ui.act_5_hist.setMaxYRange(-60.0)
        self.ui.act_5_hist.setMinYRange(-40.0)
        self.ui.act_5_hist.setMaxYRange(0.0)

        return

    def init_BC20E(self):
        """
        initialize the BC20E section of the CUD
        """
        BC20E_enable = bitStatusLabel(
            self.config['global']['fb_enable'],
            word_length=6, bit=4, parent=self.ui.FB_6_BC20E
            )
        BC20E_status = bitStatusLabel(
            self.config['global']['fb_status'],
            word_length=6, bit=4, parent=self.ui.FB_6_BC20E
            )
        self.enable_indicators.append(BC20E_enable)
        self.status_indicators.append(BC20E_status)

        # read multiknob description -- has the format BCXX_ENERGY_XANDY
        mkb_type = caget(self.config['BC20E']['mkb']).split('_')[2]

        # set appropriate channel on the actuation indicator
        PV_act_pct = self.mkb_percent['BC20E'][mkb_type]
        self.ui.act_6_pct.channel = PV_act_pct
        self.ui.BC20E_act.channel = PV_act_pct

        self.ui.act_6_hist.addYChannel(
            y_channel=self.mkb_acts['BC20E'][mkb_type][1], color=ACT_GREY
            )
        self.ui.act_6_hist.addYChannel(
            y_channel=self.mkb_acts['BC20E'][mkb_type][0], color=ACT_GREY
            )

        # act_min = caget(self.config['BC20E']['act_lo'])
        # act_max = caget(self.config['BC20E']['act_hi'])
        self.ui.act_6_hist.setMinYRange(-180.0)
        self.ui.act_6_hist.setMaxYRange(180.0)

        return

    def update_BC20E_acts(self):
        """
        value change slot for multiknob descriptor PV
        removes multiknob gauges and reinitializes with new actuators
        corresponding to the new multiknob
        """

        # udpate actuation indicator PV
        mkb_type = caget(self.config['BC20E']['mkb']).split('_')[2]
        PV_act_pct = self.mkb_percent['BC20E'][mkb_type]
        self.ui.act_6_pct.channel = PV_act_pct
        self.ui.BC20E_act.channel = PV_act_pct

        # update actuator history plot!
        return


class bitStatusLabel(PyDMLabel):
    """
    PyDMLabel subclass to display text based on status bits from a given word
    """

    def __init__(self, channel, word_length=8, bit=0, parent=None, args=None):
        super(bitStatusLabel, self).__init__(parent=parent)

        self.channel = channel
        self.word_length = word_length
        self.bit = bit
        self.text_on = 'ON'
        self.text_off = 'OFF'

        # set bold text, center text alignment
        self.setAlignment(Qt.AlignCenter)
        self.setFont(STATUS_FONT)

    def value_changed(self, new_value):
        """
        slot for PV value changes
        """
        super(bitStatusLabel, self).value_changed(new_value)

        # extract the desired bit
        on_state = (int(abs(new_value)) >> (self.bit)) & 1

        # set text and stylesheet accordingly
        style = STYLE_BITLABEL_ON if on_state else STYLE_BITLABEL_OFF
        text = self.text_on       if on_state else self.text_off

        self.setStyleSheet(style)
        self.setText(text)


class linearGauge(QProgressBar, PyDMWidget):
    """
    QProgressBar with hooks for channel access
    """

    def __init__(self, channel, lmin, lmax, \
        abs_val=False, ofs_90=False, parent=None, args=None
        ):
        QProgressBar.__init__(self, parent=parent)
        PyDMWidget.__init__(self)

        self.PV = PyDMChannel(address=channel, value_slot=self.value_changed)
        self.PV.connect()

        self.pct_label = None

        self.minimum = int(lmin)
        self.maximum = int(lmax)
        self.abs_val = abs_val
        self.ofs_90 = ofs_90
        self.reg_bounds = [75, 90]

        self.mkb_family = False

        if self.abs_val:
            self.minimum = abs(self.minimum)
            self.maximum = abs(self.maximum)

        self.setRange(self.minimum, self.maximum)
        self.setStyleSheet(STYLE_GAUGE_NOM)
        self.setTextVisible(False)

    def value_changed(self, new_value):
        """
        PV value change slot
        """
        # shift or take absolute value if needed
        if self.abs_val: new_value = abs(new_value)
        elif self.ofs_90: new_value = 90.0 - new_value

        if (new_value > self.maximum) or (new_value < self.minimum):
            self.reset()

        else:
            self.setValue(new_value)
        
        # color the progressBar chunks according to severity
        # and the actuation percentage label, if it exists
        if self.text():
            num_pct = abs(int(self.text().replace('%', '')))

            bd_lo, bd_hi = self.reg_bounds[0], self.reg_bounds[1]

            if num_pct < bd_lo:
                style_label = STYLE_NOM
                style_gauge = STYLE_GAUGE_NOM

            elif num_pct < bd_hi:
                style_label = STYLE_WARN
                style_gauge = STYLE_GAUGE_WARN

            elif num_pct >= bd_hi:
                style_label = STYLE_ALARM
                style_gauge = STYLE_GAUGE_ALARM

            self.setStyleSheet(style_gauge)

            if self.pct_label:
                self.pct_label.setStyleSheet(style_label)

