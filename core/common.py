# common methods/subclasses for FACET-II CUDs


from os import path
from functools import partial
from epics import caput, PV
import yaml

from pydm import Display
from pydm.widgets.label import PyDMLabel
from pydm.widgets.channel import PyDMChannel

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
DIR_CONFIG = path.join(SELF_PATH, 'config')
with open(path.join(REPO_ROOT, 'core', 'config.yaml'), 'r') as f:
    CONFIG = yaml.safe_load(f)


STYLE_BITLABEL_ON = """
background-color: rgb(0, 255, 0);
color: rgb(0, 0, 0);
"""

STYLE_BITLABEL_OFF = """
background-color: rgb(255, 0, 0);
color: rgb(255, 255, 255);
"""

STATUS_FONT = QFont()
STATUS_FONT.setBold(True)
STATUS_FONT.setPointSize(16)


def CUD_IDs(): return CONFIG['CUD_IDs']

def CUD_desc(CUD_ID): return CONFIG[CUD_ID]['desc']

def CUD_ID(CUD_desc):
    for k,v in CONFIG.items():
        if k not in CONFIG['CUD_IDs']: continue
        if v['desc'] == CUD_desc: return k


class F2SteeringFeedbackIndicator(PyDMLabel):
    """
    checks FBCK hardware status to check for feedback enable/compute
    """


    def __init__(self, init_channel, parent=None, args=None):
        PyDMLabel.__init__(self, init_channel=init_channel, parent=parent)
        self.setAlignment(Qt.AlignCenter)
        self.HSTA_FBCK_ON = 268601505
        self.HSTA_FBCK_COMP = 268599457

    def value_changed(self, new_value):
        PyDMLabel.value_changed(self, new_value)
        if new_value == self.HSTA_FBCK_ON:    
            self.setText('Enabled')
            self.setStyleSheet(STYLE_GREEN)
        elif new_value == self.HSTA_FBCK_COMP:
            self.setText('Compute')
            self.setStyleSheet(STYLE_YELLOW)
        else:                            
            self.setText('Off/Sample')


class F2FeedbackToggle(QFrame):
    """
    subclass to make a toggle button for F2 feedback controls
    needs to set single bits of an overall status word
    """

    def __init__(self, bit_ID, parent=None, args=None):
        QFrame.__init__(self, parent=parent)
        self.bit = bit_ID
        self.toggle_on = QPushButton('ON')
        self.toggle_off = QPushButton('OFF')
        self.status = PyDMByteIndicator()

        self.FB_state = PyDMChannel(address=PV_FB_CONTROL, value_slot=self.set_button_enable_states)
        self.FB_state.connect()

        self.toggle_on.clicked.connect(self.enable_fb)
        self.toggle_off.clicked.connect(self.disable_fb)

        self.toggle_on.setFixedWidth(50)
        self.toggle_off.setFixedWidth(50)

        L = QHBoxLayout()
        L.addWidget(self.toggle_on)
        L.addWidget(self.toggle_off)
        L.setSpacing(1)
        L.setContentsMargins(2,2,2,2)
        self.setLayout(L)

    def enable_fb(self):
        init_ctrl_state = int(caget(PV_FB_CONTROL))
        new_ctrl_state = init_ctrl_state | (1 << self.bit)
        caput(PV_FB_CONTROL, new_ctrl_state)

    def disable_fb(self):
        init_ctrl_state = int(caget(PV_FB_CONTROL))
        new_ctrl_state = init_ctrl_state & ~(1 << self.bit)
        caput(PV_FB_CONTROL, new_ctrl_state)

    def set_button_enable_states(self, new_value):
        feedback_on = (int(abs(new_value)) >> (self.bit)) & 1
        self.toggle_on.setDown(feedback_on)
        self.toggle_off.setDown(not feedback_on)

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

        self.onstyle = STYLE_BITLABEL_ON
        self.offstyle = STYLE_BITLABEL_OFF

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
        style = self.onstyle if on_state else self.offstyle
        text = self.text_on  if on_state else self.text_off

        self.setStyleSheet(style)
        self.setText(text)