# code for collecting beam references
# gets reference from relevant PV/device & saves to /beam_refs/

from os import path
from datetime import datetime
from epics import caget, caput
from numpy import loadtxt
from time import sleep


SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
REFS_PATH = path.join(REPO_ROOT, 'beam_refs')
CURRENT_REFS_FILE = path.join(REFS_PATH, 'current_refs.csv')

# defines what a valid <ref_type> is also
REF_TYPES = [
    'img_SYAG',
    'img_DTOTR2',
    'orbit_inj',
    'orbit_s20',
    ]

DATE_FMT_READABLE = '%d-%b-%Y %H:%M'
DATE_FMT_TIMESTAMP = '%Y%m%d%H%M%S'

PV_REF_UPDATE = 'SIOC:SYS1:ML03:AO976'

def set(ref_type, N_avg=1):
    """
    takes a new (possibly averaged) reference of the given <ref_type>
    wrapper to fork requests to the _set_ref_<ref_type> methods
    """
    ref_time = datetime.now()
    ts_readable = ref_time.strftime(DATE_FMT_READABLE)
    ts = ref_time.strftime(DATE_FMT_TIMESTAMP)

    if ref_type == 'img_SYAG': ref_fname = _set_ref_img_SYAG(ts, N_avg=N_avg)
    elif ref_type == 'img_DTOTR2': ref_fname = _set_ref_img_DTOTR2(ts, N_avg=N_avg)
    elif ref_type == 'orbit_inj': ref_fname = _set_ref_orbit_inj(ts, N_avg=N_avg)
    elif ref_type == 'orbit_s20': ref_fname = _set_ref_orbit_s20(ts, N_avg=N_avg)

    update_current_refs(ref_type, path.join(REFS_PATH, ref_fname))

    return ts_readable

def load(ref_type):
    """ loads the latest reference file for <ref_type> """
    # with open(CURRENT_REFS_FILE) as f:
    return

def clear(ref_type):
    """ update current_refs.csv to unset <ref_type> """
    update_current_refs(ref_type, 'NOTSET')
    return

def read_current_refs():
    """ load CURRENT_REFS_FILE to a dict """
    ref_dict = {}
    r = loadtxt(CURRENT_REFS_FILE, delimiter=',', dtype=str)
    for line in r: ref_dict[line[0]] = line[1]
    return ref_dict

def update_current_refs(ref_type, ref_fname):
    """ update CURRENT_REFS_FILE for ref_type"""
    ref_dict = read_current_refs()
    ref_dict[ref_type] = ref_fname
    _write_current_refs(ref_dict)
    _set_update_flag()
    return

def _write_current_refs(ref_dict):
    """ write CURRENT_REFS_FILE from dict """
    out = ''
    for ref_type, ref_fname in ref_dict.items(): out = out + f'{ref_type},{ref_fname}\n'
    with open(CURRENT_REFS_FILE, 'w') as f: f.write(out)
    return

def _set_update_flag():
    """ ping PV_REF_UPDATE to refresh all CUD reference displays """
    caput(PV_REF_UPDATE, 1)
    sleep(0.5)
    caput(PV_REF_UPDATE, 0)

# reference setter functions
# responsible for (1) getting ref from EPICS, (2) saving ref to file & returning filename

def _set_ref_img_SYAG(ts, N_avg=1):
    ref_fname = f'ref_img_SYAG_{ts}.png'

    PV_img = 'CAMR:LI20:100:Image:ArrayData'
    PV_w = 'CAMR:LI20:100:Image:ArraySize0_RBV'

    return ref_fname

def _set_ref_img_DTOTR2(ts, N_avg=1):
    ref_fname = f'ref_img_DTOTR2_{ts}.png'

    PV_img = 'CAMR:LI20:107:Image:ArrayData'
    PV_w = 'CAMR:LI20:107:Image:ArraySize0_RBV'

    return ref_fname

def _set_ref_orbit_inj(ts, N_avg=1):
    ref_fname = f'ref_orbit_inj_{ts}.mat'

    return ref_fname

def _set_ref_orbit_s20(ts, N_avg=1):
    ref_fname = f'ref_orbit_s20_{ts}.mat'

    return ref_fname


def _collect_reference_orbit(orbit_type, N_avg=1):
    """ create an orbit object of the correct type, save a reference """
    return

def ts_from_ref_fname(ref_fname):
    # ts_raw = ref_fname.split('_')[-1].split('.')
    return readable_ts(ref_fname.split('_')[-1].split('.')[0])

def readable_ts(ts):
    """ turns ymdhms filename timestamp back into human-friendly form """
    if ts == 'NOTSET': return 'NO REFERENCE SET'
    return datetime.strptime(ts, DATE_FMT_TIMESTAMP).strftime(DATE_FMT_READABLE)