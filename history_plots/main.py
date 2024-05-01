# history plots CUD

import os, sys
from os import path
from sys import exit
import time
import numpy as np

from epics import caget

from PyQt5.QtCore import Qt, QTimer
import pydm
from pydm import Display
from pydm.widgets.channel import PyDMChannel

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)

DEFAULT_CYCLE_TIMER = 30


# ==============================================================================
# MAIN PANEL
# ==============================================================================

class F2HistoryPlots(Display):

    def __init__(self, parent=None, args=None):
        super(F2HistoryPlots, self).__init__(parent=parent, args=args)

        self.ui.cycleTime.currentTextChanged.connect(self.update_cycle_time)
        self.ui.tabCycle.stateChanged.connect(self.enable_autocycle)

        self.cycle_time = DEFAULT_CYCLE_TIMER

        # intialize and start timer for status watcher
        self.tabCycler = QTimer(self)
        self.tabCycler.start()
        self.tabCycler.setInterval(self.cycle_time*1000)
        self.tabCycler.timeout.connect(self.change_tab)

        # axis limits

        self.ui.plot_lrtemp.getAxis('Axis 1').linkedView().setYRange(68, 74)
        self.ui.plot_lrtemp.getAxis('Axis 2').linkedView().setYRange(40, 60)

        self.ui.plot_in10temp.getAxis('Axis 1').linkedView().setYRange(90, 120)
        self.ui.plot_in10temp.getAxis('Axis 2').linkedView().setYRange(90, 120)


        # self.ui.plot_gun_ampl.getAxis('Axis 1').linkedView().setYRange(0,0)
        self.ui.plot_gun_ampl.getAxis('Axis 2').linkedView().setYRange(10,60)
        # self.ui.plot_gun_phase.getAxis('Axis 1').linkedView().setYRange(0,0)
        self.ui.plot_gun_phase.getAxis('Axis 2').linkedView().setYRange(25,35)

        # self.ui.plot_l0a_ampl.getAxis('Axis 1').linkedView().setYRange(0,0)
        self.ui.plot_l0a_ampl.getAxis('Axis 2').linkedView().setYRange(10,60)
        # self.ui.plot_l0a_phase.getAxis('Axis 1').linkedView().setYRange(0,0)
        self.ui.plot_l0a_phase.getAxis('Axis 2').linkedView().setYRange(-15,15)

        # self.ui.plot_l0b_ampl.getAxis('Axis 1').linkedView().setYRange(0,0)
        self.ui.plot_l0b_ampl.getAxis('Axis 2').linkedView().setYRange(10,60)
        # self.ui.plot_l0b_phase.getAxis('Axis 1').linkedView().setYRange(0,0)
        self.ui.plot_l0b_phase.getAxis('Axis 2').linkedView().setYRange(-30,0)


        # self.ui.plot_pmdl.getAxis('Axis 1').linkedView().setYRange(0,0)
        # self.ui.plot_pmdl.getAxis('Axis 2').linkedView().setYRange(0,0)

        self.ui.plot_l2phase.getAxis('Axis 1').linkedView().setYRange(-65, -15)
        self.ui.plot_l2phase.getAxis('Axis 2').linkedView().setYRange(-65, -15)


        self.ui.plot_toros.getAxis('Axis 1').linkedView().setYRange(-200,3200)
        self.ui.plot_toros.getAxis('Axis 2').linkedView().setYRange(-200,3200)

        self.ui.plot_pmts.getAxis('Axis 1').linkedView().setYRange(-200,20200)
        self.ui.plot_pmts.getAxis('Axis 2').linkedView().setYRange(-200,20200)

        self.ui.plot_rdms.getAxis('Axis 1').linkedView().setYRange(-200,140200)
        self.ui.plot_rdms.getAxis('Axis 2').linkedView().setYRange(-200,140200)


        self.ui.plot_l0_energy.getAxis('Axis 1').linkedView().setYRange(-2.2,2.2)
        self.ui.plot_l0_energy.getAxis('Axis 2').linkedView().setYRange(20,50)

        self.ui.plot_l1_energy.getAxis('Axis 1').linkedView().setYRange(-3.3,3.3)
        self.ui.plot_l1_energy.getAxis('Axis 2').linkedView().setYRange(120,160)

        self.ui.plot_l2_energy.getAxis('Axis 1').linkedView().setYRange(-6.6,6.6)
        self.ui.plot_l2_energy.getAxis('Axis 2').linkedView().setYRange(-180,180)

        self.ui.plot_l3_energy.getAxis('Axis 1').linkedView().setYRange(-6.6,6.6)
        self.ui.plot_l3_energy.getAxis('Axis 2').linkedView().setYRange(-180,180)

        
        self.ui.plot_l1_blen.getAxis('Axis 1').linkedView().setYRange(-30,0)
        self.ui.plot_l1_blen.getAxis('Axis 2').linkedView().setYRange(-100,8100)

        self.ui.plot_l2_blen.getAxis('Axis 1').linkedView().setYRange(-65,-15)
        self.ui.plot_l2_blen.getAxis('Axis 2').linkedView().setYRange(-100,12100)

        self.ui.plot_l3_blen.getAxis('Axis 1').linkedView().setYRange(-20,320)
        self.ui.plot_l3_blen.getAxis('Axis 2').linkedView().setYRange(-20,320)




        return

    def change_tab(self):
        i_current = self.ui.tabWidget.currentIndex()
        self.ui.tabWidget.setCurrentIndex((i_current + 1) % 6)
        return

    def enable_autocycle(self):
        autocycle = self.ui.tabCycle.isChecked()
        if autocycle:
            self.tabCycler.stop()
            self.tabCycler.start()
        else:
            self.tabCycler.stop()
        return

    def update_cycle_time(self):
        self.cycle_time = int(self.ui.cycleTime.currentText())
        self.tabCycler.stop()
        if self.ui.tabCycle.isChecked(): self.tabCycler.start()
        self.tabCycler.setInterval(self.cycle_time*1000)
        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')
