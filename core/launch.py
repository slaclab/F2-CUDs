# launcher.py
# contains controls and metadata for launching CUDs

import sys
from os import path
from subprocess import Popen
import shlex

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

from core import common

COMMAND_PYDM_LAUNCH = f'pydm --hide-nav-bar --hide-menu-bar --hide-status-bar {REPO_ROOT}/{{}}'

# mapping between CUD shorthand names, and filenames for pydm
PYDM_LAUNCH_OBJECTS = {

    # primary LM displays
    'injector':  'injector/main.py',
    'linac':     'linac/main.py',
    'klystrons': 'klystrons/main.py',
    'S20':       'S20/main.py',

    # secondary/SM displays
    'alarms':       'alarms/main.ui',
    'long_FB':      'long_FB/main.py',
    'long_FB_hist': 'long_FB/hist.py',
    'transport':    'transport/main.py',
    'PPS_BCS':      'PPS_BCS/main.ui',
    'mini_klys':    'klystrons_mini/main.py',
    'wfh':          'wfh/main.py',
    # 'network': 'network/main.py',
}

# oh god this is disgusting get rid of this once fphysics@facet-srv02 works
TMP_MACROS = "accel_type=FACET, IOC_PREFIX=IOC:SYS1:MP01, configDB_Prefix=/usr/local/facet/epics/iocTop/MpsConfiguration-FACET/current/database/, logicDB_Prefix=/usr/local/facet/epics/iocTop/MpsConfiguration-FACET/current/algorithm/, RECENT_DB_FILE=gui/dbinteraction/recentStatesDB/recent_states_facet.sqlite, CUD=SUMMARY"
MPS_GUI_PATH = '/home/fphysics/zack/workspace/F2_CUD_MPS/gui/mps_gui_main.py'
MPS_CMD = f'pydm --hide-nav-bar --hide-menu-bar --hide-status-bar -m "{TMP_MACROS}" {MPS_GUI_PATH}'

# shell commands to launch displays not captured by the above
ALT_LAUNCH_COMMANDS = {
    # 'orbit': 'bash /home/fphysics/zack/workspace/F2_CUD_orbit/launcher.sh',
    'orbit': 'python /home/fphysics/zack/workspace/F2_CUD_orbit/orbit_display.py --cud --path facet --rate TH',
    # 'MPS': 'bash /home/fphysics/zack/workspace/F2_CUD_MPS/nc_mps_gui.bash -c summary',
    'MPS': MPS_CMD,
    'network': 'pydm --hide-nav-bar --hide-menu-bar --hide-status-bar /home/fphysics/aaditya/workspace/network_panel/F2_CUD_watcher.py',
}


def run_CUD(CUD_ID):
    if CUD_ID in PYDM_LAUNCH_OBJECTS.keys(): return _run_pydm_CUD(CUD_ID)
    
    # special cases go here :) there better not be many >:(
    else: return Popen(ALT_LAUNCH_COMMANDS[CUD_ID], shell=True)

def _run_pydm_CUD(CUD_ID):
    if CUD_ID not in common.CUD_IDs(): raise KeyError("Invalid CUD name provided")
    args = shlex.split(COMMAND_PYDM_LAUNCH.format(PYDM_LAUNCH_OBJECTS[CUD_ID]))
    return Popen(args, shell=False)
