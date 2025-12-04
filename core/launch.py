# launcher.py
# contains controls and metadata for launching CUDs

import sys
from os import path
from subprocess import Popen
import shlex
import yaml

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
with open(path.join(REPO_ROOT, 'core', 'config.yaml'), 'r') as f:
    CONFIG = yaml.safe_load(f)

COMMAND_PYDM_LAUNCH = f'pydm --hide-nav-bar --hide-menu-bar --hide-status-bar {REPO_ROOT}/{{}}'

# oh god this is disgusting get rid of this once fphysics@facet-srv02 works
TMP_MACROS = "accel_type=FACET, IOC_PREFIX=IOC:SYS1:MP01, configDB_Prefix=/usr/local/facet/epics/iocTop/MpsConfiguration-FACET/current/database/, logicDB_Prefix=/usr/local/facet/epics/iocTop/MpsConfiguration-FACET/current/algorithm/, RECENT_DB_FILE=gui/dbinteraction/recentStatesDB/recent_states_facet.sqlite, CUD=SUMMARY"
MPS_GUI_PATH = '/home/fphysics/zack/workspace/F2_CUD_MPS/gui/mps_gui_main.py'
MPS_CMD = f'pydm --hide-nav-bar --hide-menu-bar --hide-status-bar -m "{TMP_MACROS}" {MPS_GUI_PATH}'

# shell commands to launch displays not captured by the above
ALT_LAUNCH_COMMANDS = {
    'orbit': 'python /home/fphysics/zack/workspace/F2_CUD_orbit/orbit_display.py --cud --path facet --rate TH',
    # 'MPS': 'bash /home/fphysics/zack/workspace/F2_CUD_MPS/nc_mps_gui.bash -c summary',
    'MPS': MPS_CMD,
}


def run_CUD(CUD_ID):
    if CUD_ID in CONFIG['CUD_IDs'] and (CUD_ID not in ALT_LAUNCH_COMMANDS.keys()):
        return _run_pydm_CUD(CUD_ID)
    
    # special cases go here :) there better not be many >:(
    else: return Popen(ALT_LAUNCH_COMMANDS[CUD_ID], shell=True)

def _run_pydm_CUD(CUD_ID):
    if CUD_ID not in CONFIG['CUD_IDs']: raise KeyError("Invalid CUD name provided")
    args = shlex.split(COMMAND_PYDM_LAUNCH.format(CONFIG[CUD_ID]['pydm']))
    return Popen(args, shell=False)
