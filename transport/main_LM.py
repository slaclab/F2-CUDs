from os import path
from pydm import Display

SELF_PATH = path.dirname(path.abspath(__file__))

class F2TransportLM(Display):

    def __init__(self, parent=None, args=None):
        super(F2TransportLM, self).__init__(parent=parent, args=args)
        for pw in [self.ui.plot_PMT, self.ui.plot_RDM, self.ui.plot_toroids, self.ui.plot_lions]:
            pw.plotItem.legend.setOffset((5,5))
            pw.plotItem.legend.setBrush(0,0,0,200)
            pw.plotItem.legend.setLabelTextColor(200,200,200)
        self.ui.plot_toroids.plotItem.legend.setColumnCount(2)
        self.ui.plot_lions.plotItem.legend.setColumnCount(2)
        return

    def ui_filename(self):
        return path.join(SELF_PATH, 'main_LM.ui')
