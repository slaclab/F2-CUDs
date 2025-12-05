from PyQt5.QtCore import Qt
from pydm.widgets.label import PyDMLabel

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

class SCPSteeringFBIndicator(PyDMLabel):
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