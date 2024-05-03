# code for collecting beam references
# gets reference from relevant PV/device & saves to /beam_refs/

from os import path, environ
from datetime import datetime
from epics import caget, caput
from numpy import loadtxt
from time import sleep

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QTextEdit, QWidget, QHBoxLayout, QLabel, QPushButton


SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
REFS_PATH = path.join(REPO_ROOT, 'beam_refs')
# CURRENT_REFS_FILE = path.join(REFS_PATH, 'current_refs.csv')
'/home/fphysics/zack/workspace/F2-CUDs/beam_refs/current_refs.csv'

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


# @pyqtSlot()
#     def load_orbit_from_file(self):
#         matlab_data_dir = os.path.join("/u1", os.environ.get('FACILITY', 'lcls'), 'matlab', 'data')
#         filename = str(QFileDialog.getOpenFileName(self, "Open File", matlab_data_dir, "Orbit data files (*.mat *.json)")[0])
#         extension = os.path.splitext(filename)[1].lower()
#         if extension == ".json":
#             try:
#                 o = BaseOrbit.from_json_file(filename)
#                 self.add_reference_orbit(o)
#                 self.statusBar().showMessage("Reference orbit loaded from file {}".format(filename), 10000)
#             except Exception as e:
#                 msgBox = QMessageBox()
#                 msgBox.setText("Couldn't load orbit from JSON file.")
#                 msgBox.setInformativeText("Error: {}".format(str(e)))
#                 msgBox.setStandardButtons(QMessageBox.Ok)
#                 msgBox.exec_()
#                 return
#         elif extension == ".mat":
#             try:
#                 o = BaseOrbit.from_MATLAB_file(filename)
#                 self.add_reference_orbit(o)
#                 self.statusBar().showMessage("Reference orbit loaded from file {}".format(filename), 10000)
#             except Exception as e:
#                 msgBox = QMessageBox()
#                 msgBox.setText("Couldn't load orbit from MATLAB file.")
#                 msgBox.setInformativeText("Orbit Display supports MATLAB files created by Orbit Display, but not the MATLAB BPMs vs. Z GUI.  Error: {}".format(str(e)))
#                 msgBox.setStandardButtons(QMessageBox.Ok)
#                 msgBox.exec_()


# def set(ref_type, N_avg=1):
#     """
#     takes a new (possibly averaged) reference of the given <ref_type>
#     wrapper to fork requests to the _set_ref_<ref_type> methods
#     """
#     ref_time = datetime.now()
#     ts_readable = ref_time.strftime(DATE_FMT_READABLE)
#     ts = ref_time.strftime(DATE_FMT_TIMESTAMP)

#     if ref_type == 'img_SYAG': ref_fname = _set_ref_img_SYAG(ts, N_avg=N_avg)
#     elif ref_type == 'img_DTOTR2': ref_fname = _set_ref_img_DTOTR2(ts, N_avg=N_avg)
#     elif ref_type == 'orbit_inj': ref_fpath = _get_orbit_file()
#     elif ref_type == 'orbit_s20': ref_fpath = _get_orbit_file()

#     update_current_refs(ref_type, ref_fpath)

#     return ts_readable

# def load(ref_type):
#     """ loads the latest reference file for <ref_type> """
#     fpath = None
#     with open(CURRENT_REFS_FILE) as f:
#         for line in f.readlines():
#             if line.split(',')[0] == ref_type:
#                 fpath = line.split(',')[1]
#     return fpath

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

# def _set_ref_orbit_inj():
#     # ref_fname = f'ref_orbit_inj_{ts}.mat'
#     ref_fname = _get_orbit_file()
#     return ref_fname

# def _set_ref_orbit_s20():
#     # ref_fname = f'ref_orbit_s20_{ts}.mat'
#     ref_fname = _get_orbit_file()
#     return ref_fname

def ts_from_ref_fname(ref_fname):
    # ts_raw = ref_fname.split('_')[-1].split('.')
    return readable_ts(ref_fname.split('_')[-1].split('.')[0])

def readable_ts(ts):
    """ turns ymdhms filename timestamp back into human-friendly form """
    if ts == 'NOTSET': return 'NO REFERENCE SET'
    return datetime.strptime(ts, DATE_FMT_TIMESTAMP).strftime(DATE_FMT_READABLE)