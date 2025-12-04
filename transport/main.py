from os import path
from pydm import Display
from matplotlib.pyplot import get_cmap
from numpy import linspace

SELF_PATH = path.dirname(path.abspath(__file__))

class F2Transport(Display):

    def __init__(self, parent=None, args=None):
        super(F2Transport, self).__init__(parent=parent, args=args)

        # colors chosen to avoid collision with alarm statuses
        # so no pure red/yellow/green
        cstr = 'color: rgb({}, {}, {});'
        cmap = get_cmap('Set3')
        toro_colors2 = (255*cmap(linspace(0,1,12))).astype(int)
        toro_colors = [
            toro_colors2[0],
            toro_colors2[1],
            toro_colors2[2],
            toro_colors2[3],
            toro_colors2[4],
            toro_colors2[5],
            toro_colors2[6],
            toro_colors2[7],
            toro_colors2[9],
            toro_colors2[10],
            ]
        toro_labels = [
            self.ui.toro_1,
            self.ui.toro_2,
            self.ui.toro_3,
            self.ui.toro_4,
            self.ui.toro_5,
            self.ui.toro_6,
            self.ui.toro_7,
            self.ui.toro_8,
            self.ui.toro_9,
            self.ui.toro_10,
            ]


        for toro_label, toro_color in zip(toro_labels, toro_colors):
            r, g, b = toro_color[0], toro_color[1], toro_color[2]
            # print(r,g,b)
            toro_label.setStyleSheet(cstr.format(r, g, b))

        self.setWindowTitle('FACET-II CUD: Beam Transport')
        for pw in [self.ui.plot_PMT, self.ui.plot_toroids, self.ui.plot_plic_slices]:
            pw.plotItem.legend.setOffset((5,5))
            pw.plotItem.legend.setBrush(0,0,0,200)
            pw.plotItem.legend.setLabelTextColor(200,200,200)
        self.ui.plot_toroids.plotItem.legend.setColumnCount(2)
        self.ui.plot_plic_slices.plotItem.legend.setColumnCount(2)
        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')
