import sys
from os import path
from sys import exit
from functools import partial
from pydm import Display
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPen
import pyqtgraph as pg
from matplotlib import colormaps as cm

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
sys.path.append(REPO_ROOT)

sys.path.append('/usr/local/facet/tools/python/')
from F2_pytools.dpmdl import normed_pmdl_history, temp_prs_history


DT_LABELS = [
    'now',
    '-6h', '-12h', '-18h', '-1d',
    '-6h', '-12h', '-18h', '-2d',
    ]

CMAP = cm.get_cmap('jet')
COLORS = [CMAP(0.1*i) for i in range(1,11)]
PENS = []
for c in COLORS:
    r,g,b,_ = c
    # print(255*r,255*g,255*b)
    PENS.append(QPen(QColor(int(255*r),int(255*g),int(255*b))))
for p in PENS:
    p.setStyle(Qt.SolidLine)
    p.setCosmetic(True)
    p.setWidth(2)

class F2_dpmdl_plot(Display):
    def __init__(self, parent=None, args=None):
        super(F2_dpmdl_plot, self).__init__(parent=parent, args=args)
        self.update_hist = QTimer(self)
        self.update_hist.start()
        self.update_hist.setInterval(5*60*1000)
        self.update_hist.timeout.connect(self.update_plots)
        self.dpmdl, self.dT = normed_pmdl_history(ndays=2)
        self.SBSTs = self.dpmdl.keys()
        self.plotdata = {}

        self.TempData = None
        self.PrsData = None

        self.pw_p = pg.plot(title='PMDL phase correction (normalized)')
        self.ui.body.layout().addWidget(self.pw_p)
        self.pw_p.showGrid(x=True, y=True, alpha=0.5)
        self.pw_p.showAxis('right')
        self.pw_p.getAxis('left').setTickSpacing(10,1)
        self.pw_p.getAxis('right').setTickSpacing(10,1)
        self.pw_p.addLegend(offset=(5,5), labelTextColor=(200,200,200), brush=(0,0,0,200))

        self.plot_pmdl()
        self.update_pmdl_plots()

        self.pw_t = pg.plot(title='Outside Temperature & Pressure')
        self.ui.body.layout().addWidget(self.pw_t)
        self.pw_t.showGrid(x=True, y=True, alpha=0.5)
        # self.pw_t.showAxis('left')
        self.pw_t.showAxis('right')
        # self.pw_t.getAxis('left').setTickSpacing(10,1)
        self.pw_t.getAxis('right').setTickSpacing(10,1)
        self.pw_t.addLegend(offset=(5,5), labelTextColor=(200,200,200), brush=(0,0,0,200))

        self.TempData = None
        self.PrsData = None
        self.plot_temp()
        self.update_temp_plot()

        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background',(38,38,38))
        pg.setConfigOption('foreground','w')

        return

    def update_plots(self):
        self.update_pmdl_plots()
        self.update_temp_plot()
        return

    def plot_pmdl(self):
        self.plotdata = {}
        for sbst_pv in self.SBSTs:
            dp, dt = self.dpmdl[sbst_pv], self.dT[sbst_pv]
            lpw = self.pw_p.plot(dt, dp, name=sbst_pv[:4])
            self.plotdata[sbst_pv[:4]] = lpw
        return

    def update_pmdl_plots(self):
        self.dpmdl, self.dT = normed_pmdl_history(ndays=2)
        for i,sb in enumerate(self.SBSTs):
            dp, dt = self.dpmdl[sb], self.dT[sb]
            self.plotdata[sb].setData(dt,dp,name=sb,pen=PENS[i]
                )

        xax = self.pw_p.getAxis('bottom')
        maxx = self.dT['LI11'][-1]
        minx = maxx - 2*86400
        self.pw_p.setXRange(minx, maxx)
        tticks, t0 = [], self.dT['LI11'][-1]
        tticks.append(t0)
        for i in range(1,10):
            tt = t0 - i*21600
            tticks.append(tt)
        xax.setTicks([[(tv, tl) for tv,tl in zip(tticks, DT_LABELS)]])
        return

    def plot_temp(self):
        self.TempData = None
        self.PrsData = None
        dTT, Temp, dTP, Prs = temp_prs_history()
        pwt = self.pw_t.plot(dTT, Temp, name='T [F]')
        pwp = self.pw_t.plot(dTP, Prs, name='P [mbar]')

        xax = self.pw_t.getAxis('bottom')
        maxx = dTT[-1]
        minx = maxx - 2*86400

        v2 = pg.ViewBox()
        self.pw_t.scene().addItem(v2)
        self.pw_t.getAxis('left').linkToView(v2)
        v2.setXLink(self.pw_t)
        v2.addItem(pwp)
        v2.setYRange(980,1040)
        self.TempData = pwt
        self.PrsData = pwp
        self.pw_t.showGrid(x=True, y=False, alpha=0.5)
        # self.pw_t.showAxis('left')
        self.pw_t.showAxis('right')
        # self.pw_t.getAxis('left').setTickSpacing(10,1)
        self.pw_t.getAxis('right').setTickSpacing(10,1)
        self.pw_t.addLegend()
        self.update_views(v2)
        self.pw_t.getViewBox().sigResized.connect(partial(self.update_views, v2))
        self.pw_t.setXRange(minx, maxx)
        return

    def update_views(self, vb):
        vb.setGeometry(self.pw_t.getViewBox().sceneBoundingRect())
        vb.linkedViewChanged(self.pw_t.getViewBox(), vb.XAxis)
        return

    def update_temp_plot(self):
        dTT, Temp, dTP, Prs = temp_prs_history()
        self.TempData.setData(dTT, Temp, name='T [F]', pen=QPen(QColor(255,112,116)))
        self.PrsData.setData(dTP, Prs, name='P [mbar]', pen=QPen(QColor(255,255,255)))
        xax = self.pw_t.getAxis('bottom')
        tticks, t0 = [], dTT[-1]
        tticks.append(t0)
        for i in range(1,10):
            tt = t0 - i*21600
            tticks.append(tt)
        xax.setTicks([[(tv, tl) for tv,tl in zip(tticks, DT_LABELS)]])
        maxx = dTT[-1]
        minx = maxx - 2*86400
        self.pw_t.setXRange(minx, maxx)
        # self.pw_t.addLegend()
        return

    def ui_filename(self):
        return path.join(SELF_PATH, 'pmdl_plots.ui')
