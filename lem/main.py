import os, sys
from os import path
from sys import exit

import pydm
from pydm import Display

from PyQt5 import QtGui, QtCore

SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
sys.path.append(REPO_ROOT)

class F2_CUD_LEM(Display):

    def __init__(self, parent=None, args=None):
        super(F2_CUD_LEM, self).__init__(parent=parent, args=args)
        return

    def ui_filename(self): return os.path.join(SELF_PATH, 'main.ui')
