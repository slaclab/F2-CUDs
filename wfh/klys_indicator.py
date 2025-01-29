"""
special PyDMLabel sublass with some extra style handling for
klystron CUD status codes
"""

import pydm
from pydm.widgets.frame import PyDMFrame
from pydm.widgets.label import PyDMLabel
from pydm.widgets.byte import PyDMByteIndicator

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QFrame, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


# SBST_BOLD = QFont('Sans Serif', 26, QFont.Bold)
SBST_BOLD = QFont('Sans Serif', 18)
SBST_REG = QFont('Sans Serif', 12)

STAT_BOLD = QFont('Sans Serif', 16, QFont.Bold)
STAT_REG  = QFont('Sans Serif', 16)

# default flag appearance
# no alarm is grey, minor alarm is yellow
STYLE_DEFAULT = """
    PyDMLabel {
      border-radius: 2px;
    }
    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="0"] {
      background-color: rgb(0,0,10);
      color: rgb(255,255,255);
      border-color: rgb(0,0,10)
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="1"] {
      background-color: rgb(0,0,10);
      color: rgb(255,255,0);
      border-color: rgb(255,255,0);
      border-width: 2px;
      border-style: solid;
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="2"] {
      background-color: rgb(255,0,0);
      color: rgb(255,255,255);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="3"] {
      background-color: rgb(192,0,255);
      color: rgb(255,255,0);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="4"] {
      color: rgb(218,218,218);
      background-color: rgb(25,25,25);
    }
"""

STYLE_DEFAULT_NO_BORDER_GREEN = """
    PyDMLabel {
      border-radius: 2px;
    }
    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="0"] {
      background-color: rgb(0,0,10);
      color: rgb(0,255,0);    
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="1"] {
      background-color: rgb(0,0,10);
      color: rgb(255,255,0);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="2"] {
      background-color: rgb(255,0,0);
      color: rgb(255,255,255);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="3"] {
      background-color: rgb(192,0,255);
      color: rgb(255,255,0);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="4"] {
      color: rgb(218,218,218);
      background-color: rgb(25,25,25);
    }
"""

# default style but with zero alarm severity green
STYLE_DEFAULT_GREEN = """
    PyDMLabel {
      border-radius: 2px;
    }
    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="0"] {
      background-color: rgb(0,0,10);
      color: rgb(0,255,0);
      border-color: rgb(0,0,10)
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="1"] {
      background-color: rgb(0,0,10);
      color: rgb(255,255,0);
      border-color: rgb(255,255,0);
      border-width: 2px;
      border-style: solid;
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="2"] {
      background-color: rgb(255,0,0);
      color: rgb(255,255,255);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="3"] {
      background-color: rgb(192,0,255);
      color: rgb(255,255,0);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="4"] {
      color: rgb(218,218,218);
      background-color: rgb(25,25,25);
    }
"""

# stylesheet for 'maintenance/TBR' type codes
# minor alarm is [BLUE OR GREY??] with no border
STYLE_MAINT = """
    PyDMLabel {
      border-radius: 2px;
    }
    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="0"] {
      background-color: rgb(0,0,10);
      color: rgb(180,180,180);
      border-color: rgb(0,0,10)
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="1"] {
      background-color: rgb(0,0,10);
      color: rgb(0,255,255);
      border-color: rgb(0,0,10);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="2"] {
      background-color: rgb(255,0,0);
      color: rgb(255,255,255);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="3"] {
      background-color: rgb(192,0,255);
      color: rgb(255,255,0);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="4"] {
      color: rgb(218,218,218);
      background-color: rgb(25,25,25);
    }
"""

# stylesheet for klystrons that are not triggering on accelerate time
# minor alarm is white text
STYLE_STBY = """
    PyDMLabel {
      border-radius: 2px;
    }
    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="0"] {
      background-color: rgb(0,0,10);
      color: rgb(255,255,255);
      border-color: rgb(200,200,200);
      border-width: 1px;
      border-style: solid;
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="1"] {
      background-color: rgb(0,0,10);
      color: rgb(255,255,0);
      border-color: rgb(255,255,0);
      border-width: 2px;
      border-style: solid;
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="2"] {
      background-color: rgb(255,0,0);
      color: rgb(255,255,255);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="3"] {
      background-color: rgb(192,0,255);
      color: rgb(255,255,0);
    }

    PyDMLabel[alarmSensitiveBorder="true"][alarmSeverity="4"] {
      color: rgb(218,218,218);
      background-color: rgb(25,25,25);
    }
"""

STYLE_PDES_ZERO = 'background-color: rgb(30,30,30);'
STYLE_PDES_NONZERO = 'background-color: rgb(255,120,0);'

# the follow klystrons don't exist, klysIndicator will be an empty QFrame
NONEXISTANT_RFS = ['11-3', '14-7', '15-2', '17-8', '19-7', '19-8']

# size parameters for klystron status indicators
H_ONBEAM    = 5
H_PDESALERT = 3
H_STAT      = 37
W_IND       = 60
H_SBST      = 40
H_SBSTBRK   = 3

class klysIndicator(QFrame):
    """ 
    QFrame with the on/off beam indicator
    and a klysStat label with some special formatting
    option to overload status PVs for weirdo stations if needed
    """
    def __init__(self,
        klys_str,
        pv_onbeam=None, pv_pdes=None, pv_kstat=None,
        parent=None, args=None
        ):
        QFrame.__init__(self, parent=parent)
        if klys_str in NONEXISTANT_RFS: return

        s, k = klys_str.split('-')[0], klys_str.split('-')[1]

        if not pv_onbeam: pv_onbeam = f'FCUDKLYS:LI{s}:{k}:ONBEAM10.RVAL'
        if not pv_pdes:   pv_pdes   = f'LI{s}:KLYS:{k}1:PDES'
        if not pv_kstat:  pv_kstat  = f'FCUDKLYS:LI{s}:{k}:STATUS.DESC'

        onbeam = PyDMByteIndicator(init_channel=pv_onbeam)
        pdes_alert = pdesAlert(init_channel=pv_pdes)
        stat = klysStat(init_channel=pv_kstat)

        onbeam.showLabels = False
        onbeam.alarmSensitiveBorder = True
        onbeam.onColor = QColor(144,194,255)
        onbeam.offColor = QColor(30,30,30)
        onbeam.setFixedHeight(H_ONBEAM)

        pdes_alert.setFixedHeight(H_PDESALERT)
        pdes_ind = QFrame()
        l = QVBoxLayout()
        l.setContentsMargins(45,1,0,0)
        l.addWidget(pdes_alert)
        pdes_ind.setLayout(l)

        stat.setFixedHeight(H_STAT)

        L = QVBoxLayout()
        L.addWidget(pdes_ind)
        L.addWidget(onbeam)
        L.addWidget(stat)
        L.setSpacing(2)
        L.setContentsMargins(2,0,2,2)
        self.setLayout(L)

        self.setFixedWidth(W_IND)

class sbstIndicator(QFrame):
    """
    QFrame with a SBST number and a status readback below
    """
    def __init__(self, sector, parent=None, args=None):
        QFrame.__init__(self, parent=parent)

        sector_label = QLabel(str(sector))
        sector_label.setFont(SBST_BOLD)
        sector_label.setAlignment(Qt.AlignCenter)
        # sector_label.setFixedHeight(H_SBST)

        stat = PyDMLabel(init_channel=f'FCUDSBST:LI{sector}:1:STATUS')
        stat.setStyleSheet(STYLE_DEFAULT_NO_BORDER_GREEN)
        stat.setFont(SBST_REG)
        stat.setAlignment(Qt.AlignCenter)
        stat.precisionFromPV = False
        stat.precision = 1

        brk = QWidget()
        brk.setFixedHeight(H_SBSTBRK)

        L = QVBoxLayout()
        L.addWidget(sector_label)
        L.addWidget(brk)
        L.addWidget(stat)
        L.addWidget(brk)
        L.setSpacing(0)
        self.setLayout(L)

        self.setFixedWidth(W_IND)


class klysStat(PyDMLabel):
    """ subclass to handle special coloring for klystron CUD statuses """

    def __init__(self, init_channel, parent=None, args=None):
        PyDMLabel.__init__(self, init_channel=init_channel, parent=parent)
        self.setStyleSheet(STYLE_DEFAULT)
        self.setFont(STAT_REG)
        self.setAlignment(Qt.AlignCenter)

    def value_changed(self, new_value):
        PyDMLabel.value_changed(self, new_value)

        if new_value in ['TBR', 'MNT', 'ARU']:
            self.setStyleSheet(STYLE_MAINT)
            self.setFont(STAT_REG)

        elif new_value in ['1','2','3','4','5','6','7','8','ACC']:

            self.setFont(STAT_REG)
            self.setStyleSheet(STYLE_DEFAULT)
            # self.setStyleSheet(STYLE_DEFAULT_GREEN)
            self.setFrameShape(QFrame.NoFrame)
            if new_value == 'ACC': self.setStyleSheet(STYLE_STBY)

        else:
            self.setStyleSheet(STYLE_DEFAULT)
            self.setFont(STAT_BOLD)
            self.setFrameShape(QFrame.Box)
            self.setLineWidth(2)


        return

class pdesAlert(PyDMFrame):
    """ subclass to change color when klys PDES is nonzero"""

    def __init__(self, init_channel, parent=None):
        PyDMFrame.__init__(self, init_channel=init_channel)
        self.alartmSensitiveBorder = True

    def value_changed(self, new_value):
        if abs(new_value) < 0.01: self.setStyleSheet(STYLE_PDES_ZERO)
        else:                     self.setStyleSheet(STYLE_PDES_NONZERO)
