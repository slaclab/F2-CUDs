import os, sys
from sys import exit

from epics import caget

import pydm
from pydm import Display

from matplotlib import pyplot as plt
from numpy import linspace

SELF_PATH = os.path.dirname(os.path.abspath(__file__))

# F2 PLOT COLORS
# chosen to avoid collision with alarm statuses
# so no pure red/yellow/green
"""
141 211 199   #8dd3c7
255 255 179   #ffffb3
190 186 218   #bebada
251 128 114   #fb8072
128 177 211   #80b1d3
253 180 98    #fbd462
179 222 105   #b3de69
252 205 229   #fccde5
188 128 189   #bc80bd
204 235 197   #ccebc5
"""

class F2Transport(Display):

    def __init__(self, parent=None, args=None):
        super(F2Transport, self).__init__(parent=parent, args=args)

        cstr = 'color: rgb({}, {}, {});'
        cmap = plt.get_cmap('Set3')

        # toro_colors2 = (255*cmap(linspace(0,1,20))).astype(int)
        # for i in toro_colors2: print(i[0], i[1], i[2])

        toro_colors2 = (255*cmap(linspace(0,1,12))).astype(int)

        # del toro_colors[8]
        # del toro_colors[]

        toro_colors = [
            toro_colors2[0],
            toro_colors2[1],
            toro_colors2[2],
            toro_colors2[3],
            toro_colors2[4],
            toro_colors2[5],
            toro_colors2[6],
            toro_colors2[7],
            toro_colors2[9],
            toro_colors2[10],
            ]

        toro_labels = [
            self.ui.toro_1,
            self.ui.toro_2,
            self.ui.toro_3,
            self.ui.toro_4,
            self.ui.toro_5,
            self.ui.toro_6,
            self.ui.toro_7,
            self.ui.toro_8,
            self.ui.toro_9,
            self.ui.toro_10,
            ]


        for toro_label, toro_color in zip(toro_labels, toro_colors):
            r, g, b = toro_color[0], toro_color[1], toro_color[2]
            # print(r,g,b)
            toro_label.setStyleSheet(cstr.format(r, g, b))

        self.setWindowTitle('FACET-II CUD: Beam Transport')

        return

    def ui_filename(self):
        return os.path.join(SELF_PATH, 'main.ui')
