import os
import sys
import time
import numpy as np
import yaml

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QFrame, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
import pyqtgraph as pg

# from p4p.client.thread import Context
from epics import get_pv
import pydm
from pydm import Display


sys.path.append('/usr/local/facet/tools/python/')
sys.path.append('/usr/local/facet/tools/python/F2_live_model')
from F2_live_model.bmad import BmadLiveModel

SELF_PATH = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(*os.path.split(SELF_PATH)[:-1])
sys.path.append(REPO_ROOT)
DIR_CONFIG = os.path.join('/usr/local/facet/tools/python/', 'F2_live_model', 'config')
with open(os.path.join(DIR_CONFIG, 'facet2e.yaml'), 'r') as f:
    CONFIG = yaml.safe_load(f)



class F2LatticePlots(Display):
    def __init__(self, parent=None, args=None):
        super(F2LatticePlots, self).__init__(parent=parent, args=args)

    def ui_filename(self): return os.path.join(SELF_PATH, 'main.ui')
