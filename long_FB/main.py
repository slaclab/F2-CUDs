# longitudinal feedbacks CUD v2 for new system

import sys
from os import path
import yaml
from PyQt5.QtGui import QFont
from pydm import Display

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
sys.path.append(REPO_ROOT)
sys.path.append('/usr/local/facet/tools/python/')
from F2_long_feedback.loop_stat_label import lfbLoopStatusLabel

FB_REPO = '/usr/local/facet/tools/python/F2_long_feedback'
with open(path.join(FB_REPO, 'config.yaml'), 'r') as f:
    CONFIG = yaml.safe_load(f)


STYLE_STAT_NOM = """
background-color: rgb(30,30,40);
color: rgb(170,170,170);
"""

STYLE_STAT_WARN = """
background-color: rgb(30,30,40);
color: rgb(255,255,0);
border-color: rgb(255,255,0);
border-width: 2px;
border-style: solid;
"""

STYLE_STAT_ALM = """
background-color: rgb(255,0,0);
color: rgb(255,255,255);
"""

STYLE_STAT_INV = """
color: rgb(220,50,255);
border-color: rgb(220,50,255);
background-color: rgb(30,30,40);
border-width: 2px;
border-style: solid;
"""

# alternate stylesheets to feed lfbLoopStatusLabel
LOOP_STATUS_STYLESHEETS = {
    0: STYLE_STAT_NOM,
    1: STYLE_STAT_WARN,
    2: STYLE_STAT_ALM,
    3: STYLE_STAT_INV,
    }

STATUS_FONT = QFont()
STATUS_FONT.setPointSize(18)

class facetFeedbackCUD(Display):

    def __init__(self, parent=None, args=None):
        super(facetFeedbackCUD, self).__init__(parent=parent, args=args)

        for plot in [
            self.ui.meas_1, self.ui.meas_2, self.ui.meas_3,
            self.ui.meas_4, self.ui.meas_5, self.ui.meas_6
            ]:
            plot.hideAxis('bottom')
            plot.setMouseEnabled(x=False, y=False)

        # put in loop status labels
        self.stat_containers = [
            self.ui.stat_dl10e, self.ui.stat_bc11e, self.ui.stat_bc11bl,
            self.ui.stat_bc14e, self.ui.stat_bc14bl, self.ui.stat_bc20e
            ]

        for loop_name, stat_cont in zip(CONFIG['loop_names'], self.stat_containers):
            label = lfbLoopStatusLabel(loop_name, style_defs=LOOP_STATUS_STYLESHEETS)
            label.setFont(STATUS_FONT)
            label.setWordWrap(True)
            stat_cont.layout().addWidget(label)

        self.setWindowTitle('FACET-II CUD: Longitudinal FB')

        return

    def ui_filename(self):
        return path.join(SELF_PATH, 'main.ui')

