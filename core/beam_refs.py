# code for collecting beam references
# gets reference from relevant PV/device & saves to /beam_refs/

from os import path, environ
from datetime import datetime
from epics import caput
from numpy import loadtxt
from time import sleep


SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
REFS_PATH = path.join(REPO_ROOT, 'beam_refs')
# CURRENT_REFS_FILE = path.join(REFS_PATH, 'current_refs.csv')
CURRENT_REFS_FILE = '/home/fphysics/zack/workspace/F2-CUDs/beam_refs/current_refs.csv'

# defines what a valid <ref_type> is also
REF_TYPES = [
    'orbit_inj',
    'orbit_s20',
    ]

DATE_FMT_READABLE = '%d-%b-%Y %H:%M'
DATE_FMT_TIMESTAMP = '%Y%m%d%H%M%S'

PV_REF_UPDATE = 'SIOC:SYS1:ML03:AO976'

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


def ts_from_ref_fname(ref_fname):
    # ts_raw = ref_fname.split('_')[-1].split('.')
    return readable_ts(ref_fname.split('_')[-1].split('.')[0])

def readable_ts(ts):
    """ turns ymdhms filename timestamp back into human-friendly form """
    if ts == 'NOTSET': return 'NO REFERENCE SET'
    return datetime.strptime(ts, DATE_FMT_TIMESTAMP).strftime(DATE_FMT_READABLE)