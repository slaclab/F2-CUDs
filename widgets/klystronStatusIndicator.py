"""
special PyDMLabel sublass with some extra style handling for
klystron CUD status codes
"""
from pydm.widgets.frame import PyDMFrame
from pydm.widgets.label import PyDMLabel
from pydm.widgets.byte import PyDMByteIndicator
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QFrame, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont




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
NONEXISTANT_RFS = ['11-3', '14-7', '15-2', '19-7', '19-8']

# size parameters for klystron status indicators

# full size settings
H_ONBEAM_full    = 6
H_PDESALERT_full = 5
H_STAT_full      = 53
W_IND_full       = 100
H_SBST_full      = 50
H_SBSTBRK_full   = 5
L_MARGIN1_full   = 60
L_MARGIN2_full   = 10

# mini indicator settings for WFH display
H_ONBEAM_mini    = 5
H_PDESALERT_mini = 3
H_STAT_mini      = 37
W_IND_mini       = 60
H_SBST_mini      = 40
H_SBSTBRK_mini   = 3
L_MARGIN1_mini   = 45
L_MARGIN2_mini   = 2

# fonts for regular/mini indicators

SBST_BOLD_full = QFont('Sans Serif', 26)
SBST_REG_full = QFont('Sans Serif', 18)
STAT_BOLD_full = QFont('Sans Serif', 22, QFont.Bold)
STAT_REG_full  = QFont('Sans Serif', 22)

SBST_BOLD_mini = QFont('Sans Serif', 18)
SBST_REG_mini = QFont('Sans Serif', 12)
STAT_BOLD_mini = QFont('Sans Serif', 16, QFont.Bold)
STAT_REG_mini  = QFont('Sans Serif', 16)

class klysIndicator(QFrame):
    """ 
    QFrame with the on/off beam indicator
    and a klysStat label with some special formatting
    option to overload status PVs for weirdo stations if needed
    """
    def __init__(self,
        klys_str,
        mini=False,
        pv_onbeam=None, pv_pdes=None, pv_kstat=None,
        parent=None, args=None
        ):
        QFrame.__init__(self, parent=parent)
        if klys_str in NONEXISTANT_RFS: return

        if mini:
            H_ONBEAM    = H_ONBEAM_mini
            H_PDESALERT = H_PDESALERT_mini
            H_STAT      = H_STAT_mini
            W_IND       = W_IND_mini
            L_MARGIN1   = L_MARGIN1_mini
            L_MARGIN2   = L_MARGIN2_mini
        else:
            H_ONBEAM    = H_ONBEAM_full
            H_PDESALERT = H_PDESALERT_full
            H_STAT      = H_STAT_full
            W_IND       = W_IND_full
            L_MARGIN1   = L_MARGIN1_full
            L_MARGIN2   = L_MARGIN2_full

        s, k = klys_str.split('-')[0], klys_str.split('-')[1]

        if not pv_onbeam: pv_onbeam = f'FCUDKLYS:LI{s}:{k}:ONBEAM10.RVAL'
        if not pv_pdes:   pv_pdes   = f'LI{s}:KLYS:{k}1:PDES'
        if not pv_kstat:  pv_kstat  = f'FCUDKLYS:LI{s}:{k}:STATUS.DESC'

        onbeam = PyDMByteIndicator(init_channel=pv_onbeam)
        pdes_alert = pdesAlert(init_channel=pv_pdes)
        stat = klysStat(init_channel=pv_kstat, mini=mini)

        onbeam.showLabels = False
        onbeam.alarmSensitiveBorder = True
        onbeam.onColor = QColor(144,194,255)
        onbeam.offColor = QColor(30,30,30)
        onbeam.setFixedHeight(H_ONBEAM)

        pdes_alert.setFixedHeight(H_PDESALERT)
        pdes_ind = QFrame()
        l = QVBoxLayout()
        l.setContentsMargins(L_MARGIN1,2,0,0)
        l.addWidget(pdes_alert)
        pdes_ind.setLayout(l)

        stat.setFixedHeight(H_STAT)

        L = QVBoxLayout()
        L.addWidget(pdes_ind)
        L.addWidget(onbeam)
        L.addWidget(stat)
        L.setSpacing(2)
        L.setContentsMargins(L_MARGIN2,0,L_MARGIN2,L_MARGIN2)
        self.setLayout(L)

        self.setFixedWidth(W_IND)

class sbstIndicator(QFrame):
    """
    QFrame with a SBST number and a status readback below
    """
    def __init__(self, sector, mini=False, parent=None, args=None):
        QFrame.__init__(self, parent=parent)

        if mini:
            SBST_BOLD   = SBST_BOLD_mini
            SBST_REG    = SBST_REG_mini
            H_SBST      = H_SBST_mini
            H_SBSTBRK   = H_SBSTBRK_mini
            W_IND       = W_IND_mini
        else:
            SBST_BOLD   = SBST_BOLD_full
            SBST_REG    = SBST_REG_full
            H_SBST      = H_SBST_full
            H_SBSTBRK   = H_SBSTBRK_full
            W_IND       = W_IND_full

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
    def __init__(self, init_channel, mini=False, parent=None, args=None):
        PyDMLabel.__init__(self, init_channel=init_channel, parent=parent)
        self.mini = mini
        if self.mini:
            self.STAT_BOLD   = STAT_BOLD_mini
            self.STAT_REG    = STAT_REG_mini
        else:
            self.STAT_BOLD   = STAT_BOLD_full
            self.STAT_REG    = STAT_REG_full
        
        self.setStyleSheet(STYLE_DEFAULT)
        self.setFont(self.STAT_REG)
        self.setAlignment(Qt.AlignCenter)

    def value_changed(self, new_value):
        PyDMLabel.value_changed(self, new_value)

        if new_value in ['TBR', 'MNT', 'ARU']:
            self.setStyleSheet(STYLE_MAINT)
            self.setFont(self.STAT_REG)

        elif new_value in ['1','2','3','4','5','6','7','8','ACC']:
            self.setFont(self.STAT_REG)
            self.setStyleSheet(STYLE_DEFAULT)
            self.setFrameShape(QFrame.NoFrame)
            if new_value == 'ACC': self.setStyleSheet(STYLE_STBY)

        else:
            self.setStyleSheet(STYLE_DEFAULT)
            self.setFont(self.STAT_BOLD)
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
