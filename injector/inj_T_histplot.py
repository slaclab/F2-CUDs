import sys
from os import path
from pydm import Display
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPen
import pyqtgraph as pg
from matplotlib import colormaps as cm

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
sys.path.append('/usr/local/facet/tools/python/')
from F2_pytools import inj_T_hist

DT_LABELS = [
    'now',
    '-6h', '-12h', '-18h', '-1d',
    '-6h', '-12h', '-18h', '-2d',
    ]

CMAP = cm.get_cmap('hsv')
COLORS = [CMAP(i/7) for i in range(1,7)]
PENS = []
for c in COLORS:
    r,g,b,_ = c
    print(255*r,255*g,255*b)
    PENS.append(QPen(QColor(int(255*r),int(255*g),int(255*b))))
for p in PENS:
    p.setStyle(Qt.SolidLine)
    p.setCosmetic(True)
    p.setWidth(1)

class F2_inj_T_plot(Display):

    def __init__(self, parent=None, args=None):
        super(F2_inj_T_plot, self).__init__(parent=parent, args=args)
        
        self.update_hist = QTimer(self)
        self.update_hist.start()
        self.update_hist.setInterval(5*60*1000)
        self.update_hist.timeout.connect(self.update_dT_plot)

        self.dTemp, self.dt = inj_T_hist.inj_dT_history()

        self.labels = self.dTemp.keys()
        self.plotdata = {}

        self.pw = pg.plot(title='S10 injector temparture history (normalized)')
        self.ui.layout().addWidget(self.pw)
        self.pw.showGrid(x=True, y=True, alpha=0.5)
        self.pw.hideAxis('left')
        self.pw.showAxis('right')
        self.pw.getAxis('right').setTickSpacing(10,1)
        self.pw.addLegend(offset=(5,5), labelTextColor=(200,200,200), brush=(0,0,0,200))

        self.make_dT_plot()
        self.update_dT_plot()

        self.TempData = None

        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background',(0,0,0))
        pg.setConfigOption('foreground','w')

        return

    def make_dT_plot(self):
        self.plotdata = {}
        for label in self.labels:
            temp, times = self.dTemp[label], self.dt[label]
            lpw = self.pw.plot(times, temp, name=label)
            self.plotdata[label] = lpw
        return

    def update_dT_plot(self):
        
        self.dTemp, self.dt = inj_T_hist.inj_dT_history()
        for i,label in enumerate(self.labels):
            temp, times = self.dTemp[label], self.dt[label]
            self.plotdata[label].setData(times, temp, name=label, pen=PENS[i])
        
        xax = self.pw.getAxis('bottom')
        maxx = self.dt['Vitara'][-1]
        minx = maxx - 2*86400
        self.pw.setXRange(minx, maxx)
        tticks, t0 = [], self.dt['Vitara'][-1]
        tticks.append(t0)
        for i in range(1,10):
            tt = t0 - i*21600
            tticks.append(tt)
        xax.setTicks([[(tv, tl) for tv,tl in zip(tticks, DT_LABELS)]])
        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'inj_T_hist.ui')
