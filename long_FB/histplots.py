import sys
from os import path
from pydm import Display

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
sys.path.append(REPO_ROOT)

class F2longHist(Display):

    def __init__(self, parent=None, args=None):
        super(F2longHist, self).__init__(parent=parent, args=args)

        for plot in [
            self.ui.L0_energy, self.ui.L1_energy, self.ui.L1_blen,
            self.ui.L2_energy, self.ui.L2_blen, self.ui.L3_energy,
            ]:
            plot.hideAxis('bottom')

        self.ui.L1_blen.getAxis('Axis 2').linkedView().setYRange(-40,0)
        self.ui.L2_blen.getAxis('Axis 2').linkedView().setYRange(-70,0)

        return

    def ui_filename(self):
        return path.join(SELF_PATH, 'histplots_stacked.ui')
