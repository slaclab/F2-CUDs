# remote launch/kill controls for ACR

import os, sys
from subprocess import call, check_output, CalledProcessError
from time import sleep

from epics import caget, caput

from core import launch, common


# list of LM/SM machines in ACR quadrant 2
# could be truncated if SPEAR ever colonizes half the quadrant ...
LARGE_MONITORS = [
    'LM20L',
    'LM20R',

    'LM21L',
    'LM21R',

    'LM22L',
    'LM22R',

    'LM23L',
    'LM23R',

    'LM24L',
    'LM24R',
    ]

SMALL_MONITORS = [
    'SM20A',
    'SM20B',
    'SM20C',
    'SM20D',

    'SM22A',
    'SM22B',
    'SM22C',
    'SM22D',

    'SM24A',
    'SM24B',
    'SM24C',
    'SM24D',

    'SM26A',
    'SM26B',
    'SM26C',
    'SM26D',

    'SM28A',
    'SM28B',
    'SM28C',
    'SM28D',
    ]

CUD_PV_ROOT = 'CUD:ACR0:{{}}:{}'
PVSTEM_DISP = CUD_PV_ROOT.format('DISPLAY')
PVSTEM_PID  = CUD_PV_ROOT.format('PID')
PVSTEM_WID  = CUD_PV_ROOT.format('WINDOWID')

COMMAND_WMCTRL_LIST = 'wmctrl -lpG'
COMMAND_WMCTRL_FIND = f'{COMMAND_WMCTRL_LIST} | grep "{{}}"'

COMMAND_WMCTRL_MOVE = 'wmctrl -i -r {}'
COMMAND_WMCTRL_REPOSITION = f'{COMMAND_WMCTRL_MOVE} -e 0,{{}},0,{{}},{{}}' # args: x, w, h
COMMAND_WMCTRL_FULLSCREEN = f'{COMMAND_WMCTRL_MOVE} -b add,fullscreen'

# need physics user to write to ACR CUD PVs 
PHYS_CAPUT = "ssh physics@lcls-srv01 'caput {} {}'"

def LM_names(): return LARGE_MONITORS

def SM_names(): return SMALL_MONITORS

def CUD_PV_disp(monitor): return PVSTEM_DISP.format(monitor)

def CUD_PV_pid(monitor): return PVSTEM_PID.format(monitor)

def CUD_PV_wid(monitor): return PVSTEM_WID.format(monitor)

def get_display_name(monitor):
    """
    turns the ACR monitor name ("LM21L" etc) into sunray IDs
    """
    command = f'cat /usr/local/admin/sunray/{monitor.lower()[:4]}'
    out = check_output(command, shell=True)
    return out.decode('utf-8').strip()+'0'

def get_x_coord(monitor):
    """
    offset X by multiples of 1920 based on L/R or A/B/C/D
    """
    suffix = monitor[-1]
    if   suffix in ['L', 'A']: return 0
    elif suffix in ['R', 'B']: return 1920
    elif suffix == 'C':        return 1920*2
    elif suffix == 'D':        return 1920*3

def kill_monitor(monitor):
    """
    kills the process labelled with CUD:ACR0:<monitor>:PID
    resets CUD:ACR0:<monitor> PVs
    """
    CUD_PID = caget(CUD_PV_pid(monitor))
    if CUD_PID:
        try:
            check_output(f'kill -9 {CUD_PID}', shell=True)
        except CalledProcessError:
            print('nothing running')

        # unset display name, PID and windowID PVs
        call(PHYS_CAPUT.format(CUD_PV_disp(monitor), '""'), shell=True)
        call(PHYS_CAPUT.format(CUD_PV_pid(monitor), '""'), shell=True)
        call(PHYS_CAPUT.format(CUD_PV_wid(monitor), '""'), shell=True)

    # verify success somehow?

    # # unset display name, PID and windowID PVs
    # call(PHYS_CAPUT.format(CUD_PV_disp(monitor), '""'), shell=True)
    # call(PHYS_CAPUT.format(CUD_PV_pid(monitor), '""'), shell=True)
    # call(PHYS_CAPUT.format(CUD_PV_wid(monitor), '""'), shell=True)

    return

def send_to_monitor(monitor, CUD_ID):
    """
    sends <CUD_ID> to <monistor>
    fullscreens the display after launch
    sets CUD:ACR0:<monitor> PVs
    """

    # set $DISPLAY env var to the relevant LM/SM sunray
    init_disp = os.environ['DISPLAY']
    os.environ['DISPLAY'] = get_display_name(monitor)

    p = launch.run_CUD(CUD_ID)

    # wmctrl+grep to check for the new window & grab its ID
    n, CUD_win_ID = 0, ''
    while not CUD_win_ID and n < 60:
        n = n+1
        CUD_win_ID = _find_win_ID(CUD_ID)
        if CUD_win_ID: break
        sleep(0.5)
    else:
        raise RuntimeError('Display was not visible to window manager within 30s')

    # resposition/fullscreen with wmctrl
    _reposition_CUD(CUD_win_ID, monitor)

    # TO DO: verify success somehow?

    # caput to display name, PID and windowID PVs
    call(PHYS_CAPUT.format(CUD_PV_disp(monitor), common.CUD_desc(CUD_ID)), shell=True)
    call(PHYS_CAPUT.format(CUD_PV_pid(monitor), str(p.pid)), shell=True)
    call(PHYS_CAPUT.format(CUD_PV_wid(monitor), CUD_win_ID), shell=True)

    # restore $DISPLAY to localhost
    os.environ['DISPLAY'] = init_disp
    return

def _get_win_ID_list():
    """ helper function - calls wmctrl, parses output, returns winID """
    init_win_list = check_output(COMMAND_WMCTRL_LIST, shell=True).decode('utf-8').strip()
    win_IDs = []
    for r in init_win_list.split('\n'): win_IDs.append(r.split()[0])
    return win_IDs

def _find_win_ID(CUD_ID):
    """
    use wmctrl and grep for the windowID of a CUD, if grep fails, return nothing
    """
    CUD_window_title = f'FACET-II CUD: {common.CUD_desc(CUD_ID)}'
    CUD_window_title_alt = f'{common.CUD_desc(CUD_ID)}'
    
    try:
        args = COMMAND_WMCTRL_FIND.format(CUD_window_title)
        return check_output(args, shell=True).decode('utf-8').strip().split()[0]

    except CalledProcessError:
        try:
            args = COMMAND_WMCTRL_FIND.format(CUD_window_title_alt)
            return check_output(args, shell=True).decode('utf-8').strip().split()[0]
        except CalledProcessError:
            return ''

def _reposition_CUD(win_ID, monitor):
    """
    step 1: reposition with x offset for L/R, A/B/C/D & set to 1920x1080
    step 2: fullscreen
    """
    x_offset = get_x_coord(monitor)
    w,h = 1920,1080
    cmd_reposition = COMMAND_WMCTRL_REPOSITION.format(win_ID, x_offset, w, h)
    cmd_fullscreen = COMMAND_WMCTRL_FULLSCREEN.format(win_ID)


    for command in [cmd_reposition, cmd_fullscreen]:
        try:
            out = check_output(command, shell=True)
        except CalledProcessError:
            raise RuntimeError('Display window adjustment failed.')
    return
