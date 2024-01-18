import os, sys
from os import path
from functools import partial
from socket import gethostname
from time import sleep

from epics import caget, caput

import pydm
from pydm import Display
from pydm import PyDMApplication
from pydm.widgets.label import PyDMLabel
from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel

from PyQt5.QtWidgets import QGridLayout, QWidget, QFrame, QPushButton, QComboBox, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

SELF_PATH = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)

from core import launch, common, beam_refs
import core.ACR_remote_control as rctrl


STYLE_KILL = """
QPushButton[enabled="true"] {
background-color: rgb(180,0,0);
color: rgb(255,255,255);
}
QPushButton[enabled="false"] {
background-color: rgb(180,100,100);
color: rgb(200,200,200);
}
"""

STYLE_LAUNCH = """
QPushButton[enabled="true"] {
background-color: rgb(144,194,255);
color: rgb(0,0,0);
}
QPushButton[enabled="false"] {
background-color: rgb(180,220,255);
color: rgb(200,200,200);
}
"""


# class F2CUDManager(Display):
class F2CUDManager(Display):

    def __init__(self, parent=None, args=None):
        super(F2CUDManager, self).__init__(parent=parent, args=args)

        self.hostname = gethostname()
        self.status(f'hostname is: {self.hostname}')

        self.CUD_IDs = common.CUD_IDs()
        self.CUD_descs = []
        for name in self.CUD_IDs: self.CUD_descs.append(common.CUD_desc(name))

        self.LM_names = rctrl.LM_names()
        self.SM_names = rctrl.SM_names()

        self.default_displays = _load_ACR_defaults()

        self.CUD_selectors = {}
        self.kill_buttons = {}
        self.launch_buttons = {}

        self.init_CUD_summary(monitors=self.LM_names, layout=self.ui.LM_control.layout())
        self.init_CUD_summary(monitors=self.SM_names, layout=self.ui.SM_control.layout())
        self.init_local_launch_buttons()

        self.ui.autosetup_LM.clicked.connect(
            partial(self.launch_monitors, monitors=self.LM_names)
            )
        self.ui.autosetup_SM.clicked.connect(
            partial(self.launch_monitors, monitors=self.SM_names)
            )
        self.ui.autosetup_all.clicked.connect(self.launch_full_quadrant)

        self.ui.kill_LM.clicked.connect(partial(self.kill_monitors, monitors=self.LM_names))
        self.ui.kill_SM.clicked.connect(partial(self.kill_monitors, monitors=self.SM_names))
        self.ui.kill_all.clicked.connect(self.kill_everything)

        self.ref_labels = {
            'img_SYAG': self.ui.ref_ts_img_SYAG,
            'img_DTOTR2': self.ui.ref_ts_img_DTOTR2,
            'orbit_inj': self.ui.ref_ts_orbit_inj,
            'orbit_s20': self.ui.ref_ts_orbit_s20,
            }

        # beam reference set/clear controls setup
        refs = [
            'img_SYAG',
            'img_DTOTR2',
            'orbit_inj',
            'orbit_s20',
            ]
        ref_sets = [
            self.ui.ref_set_img_SYAG,
            self.ui.ref_set_img_DTOTR2,
            self.ui.ref_set_orbit_inj,
            self.ui.ref_set_orbit_s20,
            ]
        ref_clears = [
            self.ui.ref_clear_img_SYAG,
            self.ui.ref_clear_img_DTOTR2,
            self.ui.ref_clear_orbit_inj,
            self.ui.ref_clear_orbit_s20,
            ]

        for ref_type, ref_set, ref_clear in zip(refs, ref_sets, ref_clears):
            ref_set.clicked.connect(partial(self.set_reference, ref_type=ref_type))
            ref_clear.clicked.connect(partial(self.clear_reference, ref_type=ref_type))

        self.refresh_beam_refs()

        self.status('CUD manager ready.')
        
        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')

    def status(self, msg): self.statusMessage.appendPlainText(msg)

    def init_CUD_summary(self, monitors, layout):
        """"
        initialize each row for LM/SM CUD controls, consists of:
        * label for current display, processID and windowID PVs
        * 'kill' button for current display, if any
        * dropdown menu to select CUDs, populated from ACR_defaults.csv
        * 'launch' button to send displays to LM/SMs
        """

        for i_monitor, monitor in enumerate(monitors):

            label_disp = PyDMLabel(init_channel=rctrl.CUD_PV_disp(monitor))
            label_pid  = PyDMLabel(init_channel=rctrl.CUD_PV_pid(monitor))
            label_wid  = PyDMLabel(init_channel=rctrl.CUD_PV_wid(monitor))

            kill_button = QPushButton('Kill')
            kill_button.clicked.connect(partial(self.kill_CUD, monitor=monitor))

            CUD_select = QComboBox()
            CUD_select.addItems(self.CUD_descs)
            _set_dropdown_default(CUD_select, self.default_displays[monitor])

            launch_button = QPushButton('Launch')
            launch_button.clicked.connect(partial(self.remote_CUD_launch, monitor=monitor))

            # watch the :PID PV and enable controls accordingly
            monitor_PID_channel = PyDMChannel(
                address=rctrl.CUD_PV_pid(monitor),
                value_slot=partial(self.set_control_enable_states, monitor=monitor))
            monitor_PID_channel.connect()

            label_disp.setMinimumWidth(130)
            label_pid.setFixedWidth(80)
            label_wid.setFixedWidth(100)
            kill_button.setFixedWidth(40)
            launch_button.setFixedWidth(70)

            label_disp.setAlignment(Qt.AlignCenter)
            label_pid.setAlignment(Qt.AlignCenter)
            label_wid.setAlignment(Qt.AlignCenter)

            kill_button.setStyleSheet(STYLE_KILL)
            launch_button.setStyleSheet(STYLE_LAUNCH)
            
            i_row = i_monitor+2
            for i_elem, elem in enumerate([
                label_disp,
                label_pid,
                label_wid,
                kill_button,
                CUD_select,
                launch_button,
                ]):
                layout.addWidget(elem, i_row, i_elem+1)

            # keep track of controls for each monitor to handle enable/disable logic
            # and dropdown menu selection
            self.CUD_selectors[monitor]  = CUD_select
            self.kill_buttons[monitor]   = kill_button
            self.launch_buttons[monitor] = launch_button

            current_disp = bool(caget(rctrl.CUD_PV_disp(monitor)))
            kill_button.setEnabled(current_disp)
            launch_button.setEnabled(not current_disp)

        return

    def set_control_enable_states(self, new_value, monitor):
        """
        disable/enable the launch/kill buttons if the ACR monitor's PID PV is set 
        """
        monitor_has_display = bool(new_value)
        self.kill_buttons[monitor].setEnabled(monitor_has_display)
        self.CUD_selectors[monitor].setEnabled(not monitor_has_display)
        self.launch_buttons[monitor].setEnabled(not monitor_has_display)
        self.kill_buttons[monitor].setStyleSheet(STYLE_KILL)
        self.launch_buttons[monitor].setStyleSheet(STYLE_LAUNCH)
        return

    def init_local_launch_buttons(self):
        """ connect each button on the 'run locally' tab to a launch method """
        buttons = {
            self.ui.launch_injector: 'injector',
            self.ui.launch_linac: 'linac',
            self.ui.launch_klystrons: 'klystrons',
            self.ui.launch_S20: 'S20',

            # self.ui.launch_LEM: 'LEM',
            self.ui.launch_transport: 'transport',
            self.ui.launch_long_FB: 'long_FB',
            self.ui.launch_long_FB_hist: 'long_FB_hist',
            
            self.ui.launch_mini_klys: 'mini_klys',

            self.ui.launch_PPS_BCS: 'PPS_BCS',
            self.ui.launch_MPS: 'MPS',
            
            self.ui.launch_orbit: 'orbit',
            self.ui.launch_alarms: 'alarms',
            self.ui.launch_network: 'network',
            }
        for button, CUD_ID in buttons.items():
            button.clicked.connect(partial(self.local_CUD_launch, CUD_ID))
        return

    def local_CUD_launch(self, CUD_ID):
        """ function for launching CUDs locally. Just a wrapper for launcher.run_CUD """
        CUD_desc = common.CUD_desc(CUD_ID)
        self.status(f'Launching display: [{CUD_desc}] ...')
        launcher.run_CUD(CUD_ID)
        return

    def remote_CUD_launch(self, monitor):
        """ function for sending displays to ACR LMs/SMs via thin client """
        mon_ID = rctrl.get_display_name(monitor)
        CUD_desc = self.CUD_selectors[monitor].currentText()
        CUD_ID = common.CUD_ID(CUD_desc)
        self.status(f'Launching display: [{CUD_desc}] on: {monitor} ({mon_ID}) ...')
        rctrl.send_to_monitor(monitor, CUD_ID)
        return

    def kill_CUD(self, monitor):
        mon_ID = rctrl.get_display_name(monitor)
        self.status(f'Killing display on: {monitor} ({mon_ID}) ...')
        # TO DO: disable buttons when working and when done
        rctrl.kill_monitor(monitor)
        return

    def launch_monitors(self, monitors):
        """ launch default displays on all monitors (LM or SM) """
        i_mon = 1 if (monitors == self.LM_names) else 2
        self.ui.CUD_summary.setCurrentIndex(i_mon)
        self._update_CUD_summary()
        for monitor in monitors:
            self.remote_CUD_launch(monitor)
            self._update_CUD_summary()
        self.ui.CUD_summary.setCurrentIndex(0)
        self.status('Done.')

    def kill_monitors(self, monitors):
        """ kill displays on all monitors (LM or SM) """
        i_mon = 1 if (monitors == self.LM_names) else 2
        self.ui.CUD_summary.setCurrentIndex(i_mon)
        self._update_CUD_summary()
        for monitor in monitors:
            self.kill_CUD(monitor)
            self._update_CUD_summary()
        self.ui.CUD_summary.setCurrentIndex(0)
        self.status('Done.')

    def _update_CUD_summary(self):
        self.ui.CUD_summary.repaint()

    def launch_full_quadrant(self):
        self.kill_everything()
        self.launch_monitors(monitors=self.LM_names)
        self.launch_monitors(monitors=self.SM_names)

    def kill_everything(self):
        self.status('Commencing hostilities.')
        self.kill_monitors(monitors=self.LM_names)
        self.kill_monitors(monitors=self.SM_names)

    def refresh_beam_refs(self):
        # set the beam ref labels appropriately from current_refs.csv
        for ref_type, ref_fname in beam_refs.read_current_refs().items():
            ts_raw = ref_fname.split('_')[-1].split('.')[0]
            self.ref_labels[ref_type].setText(beam_refs.readable_ts(ts_raw))
        return

    def set_reference(self, ref_type, N_avg=1):
        self.ref_labels[ref_type].setText('Working  ...')
        ts = beam_refs.set(ref_type=ref_type)
        self.ref_labels[ref_type].setText(ts)
        return

    def clear_reference(self, ref_type):
        """ general purpose clear function -- just needs to delete files """
        beam_refs.clear(ref_type)
        self.refresh_beam_refs()
        return

def _load_ACR_defaults():
    """" load default display setting for each LM/SM from config file """
    defaults = {}
    with open(path.join(REPO_ROOT, 'core', 'defaults.csv'), 'r') as f:
        for line in f.readlines():
            if line.startswith('#'): continue
            r = line.strip().split(',')
            monitor, CUD_ID = r[0], r[1]
            defaults[monitor] = CUD_ID
    return defaults


def _set_dropdown_default(combo_box, default):
    """ stupid thing to get the item index based on text from a QComboBox """
    for i in range(combo_box.count()):
        if common.CUD_ID(combo_box.itemText(i)) == default:
            combo_box.setCurrentIndex(i)
            break
