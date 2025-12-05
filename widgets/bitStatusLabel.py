from PyQt5.QtCore import Qt
from pydm.widgets.label import PyDMLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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