import sys
from os import path
from sys import exit
from numpy import nanmean, reshape
from functools import partial
from pydm import Display
from pydm.widgets.channel import PyDMChannel
from pyqtgraph import colormap
from PyQt5.QtCore import QTimer
from epics import get_pv

# import orbit
from orbit import FacetOrbit, DiffOrbit, BaseOrbit, BPM, FacetSCPBPM
from orbit_view import OrbitView 


SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])

sys.path.append(REPO_ROOT)

from core import beam_refs
from widgets.InvertedPyDMImage import InvertedPyDMImage

ORBIT_DRAW_RATE = 10
ORBIT_POS_SCALE = 1.1
ORBIT_TMIT_MAX = 1.4e10

PV_REF_UPDATE = 'SIOC:SYS1:ML03:AO976'

PV_SYAG = 'CAMR:LI20:100'
PV_DTOTR = 'CAMR:LI20:107'
PV_DTOTR_ESCALE_ETA = 'SIOC:SYS1:ML00:AO332'
PV_DTOTR_ESCALE_E0 = 'SIOC:SYS1:ML00:AO333'

PV_DTOTR_TRACK_UPDATE = 'SIOC:SYS1:ML03:AO977'


def calc_dtotr_centroid():
    """ get the image centroid (x/y peaks) from DTOTR2 & determine CUD image ROI """
    pv_img = get_pv(f'{PV_DTOTR}:Image:ArrayData')
    pv_imgw = get_pv(f'{PV_DTOTR}:Image:ArraySize0_RBV')
    pv_imgh = get_pv(f'{PV_DTOTR}:Image:ArraySize1_RBV')
    imraw = pv_img.get()
    w, h = pv_imgw.get(), pv_imgh.get()
    image = reshape(imraw, (w,h), order='F')
    image = image - min(image.flatten())
    px = nanmean(image, axis=0)
    py = nanmean(image, axis=1)
    cx = px.argmax()
    cy = py.argmax()
    return cx, cy

class F2_CUD_S20(Display):

    def __init__(self, parent=None, args=None):
        super(F2_CUD_S20, self).__init__(parent=parent, args=args)
        # super(F2_CUD_S20, self).__init__()

        SYAG_image = InvertedPyDMImage(
            im_ch=f'{PV_SYAG}:Image:ArrayData',
            w_ch=f'{PV_SYAG}:Image:ArraySize0_RBV',
            parent=self.ui.frame_SYAG
            )
        SYAG_image.readingOrder = 1
        SYAG_image.colorMap = 4
        SYAG_image.setGeometry(5, 5, 490, 240)
        SYAG_image.setShowAxes(True)
        SYAG_image.getView().getViewBox().setLimits(
            xMin=0, xMax=get_pv(f'{PV_SYAG}:Image:ArraySize0_RBV').get()+100,
            yMin=0, yMax=get_pv(f'{PV_SYAG}:Image:ArraySize1_RBV').get()/2.0
            )
        SYAG_image.setColorMap(cmap=colormap.get('inferno'))
        SYAG_image.setScaleXAxis(get_pv(f'{PV_SYAG}:RESOLUTION').value*1e-3)
        SYAG_image.setScaleYAxis(get_pv(f'{PV_SYAG}:RESOLUTION').value*1e-3)

        reso = get_pv(f'{PV_DTOTR}:RESOLUTION').value*1e-3
        Escale_eta = get_pv(PV_DTOTR_ESCALE_ETA).value
        Escale_E0 = get_pv(PV_DTOTR_ESCALE_E0).value
        self.ui.live_DTOTR2.setScaleXAxis(reso)
        self.ui.live_DTOTR2.setScaleYAxis(reso)

        self.track_dtotr = QTimer(self)
        self.track_dtotr.start()
        self.track_dtotr.setInterval(500)
        self.track_dtotr.timeout.connect(self.set_DTOTR2_ROI)

        # setup S20 orbit
        self.draw_orbit = QTimer(self)
        self.live_orbit = FacetOrbit(
            ignore_bad_bpms=True, rate_suffix='TH', scp_suffix='57',
            name='FACET-II BC20 - DUMP orbit'
            )
        self.live_orbit.bpms = self.S20_BPMs()
        self.live_orbit.connect()        

        cud_orbit = partial(OrbitView,
            parent=self, draw_timer=self.draw_orbit,
            units="mm",  ymin=-ORBIT_POS_SCALE, ymax=ORBIT_POS_SCALE, orbit=self.live_orbit
            )
        self.xOrbitView = cud_orbit(axis="x", name="X", label="X")
        self.yOrbitView = cud_orbit(axis="y", name="Y", label="Y")
        self.yOrbitView.setXLink(self.xOrbitView)
        self.yOrbitView.setYLink(self.xOrbitView)
        self.ui.cont_orbit.layout().addWidget(self.xOrbitView)
        self.ui.cont_orbit.layout().addWidget(self.yOrbitView)
        self.draw_orbit.start()

        self.reference_orbit = None
        self.difference_orbit = None
        ref_update_flag = PyDMChannel(address=PV_REF_UPDATE, value_slot=self.udpate_ref_orbit)
        ref_update_flag.connect()

        self.ui.plot_PMT.plotItem.legend.setOffset((5,5))
        self.ui.plot_PMT.plotItem.legend.setBrush(0,0,0,200)
        self.ui.plot_PMT.plotItem.legend.setLabelTextColor(200,200,200)
        self.ui.plot_RDM.plotItem.legend.setOffset((5,5))
        self.ui.plot_RDM.plotItem.legend.setBrush(0,0,0,200)
        self.ui.plot_RDM.plotItem.legend.setLabelTextColor(200,200,200)

        self.setWindowTitle('FACET-II CUD: Sector 20')
        return


    def ui_filename(self):
        return path.join(SELF_PATH, 'main.ui')

    def udpate_ref_orbit(self):
        ref_dict = beam_refs.read_current_refs()
        orbit_fpath, ftype = ref_dict['orbit_s20'], 'Absolute'
        if orbit_fpath != 'NOTSET':
            try:
                self.reference_orbit = BaseOrbit.from_MATLAB_file(orbit_fpath)
                fname = path.split(orbit_fpath)[-1]
                ftype = 'Diff'
                self.difference_orbit = DiffOrbit(self.live_orbit, self.reference_orbit)
                print(f"Reference orbit loaded from file {orbit_fpath}")
            except Exception as e:
                print("Couldn't load orbit from MATLAB file.")
                print("Only MATLAB files created by Orbit Display are supported\n")
                raise(e)
        self.ui.ref_orbit_name.setText(path.split(orbit_fpath)[-1])
        self.ui.label_orbit_type.setText(ftype)

        orbit = self.live_orbit
        if ftype == 'Diff': orbit = DiffOrbit(self.live_orbit, self.reference_orbit)
        self.xOrbitView.set_orbit(orbit)
        self.yOrbitView.set_orbit(orbit)
        return

    def S20_BPMs(self):
        s20_BPMs_SCP = [
            'BPMS:LI20:2050', 'BPMS:LI20:2147', 'BPMS:LI20:2160', 'BPMS:LI20:2223',
            'BPMS:LI20:2235', 'BPMS:LI20:2245', 'BPMS:LI20:2261', 'BPMS:LI20:2278', 
            'BPMS:LI20:2340', 'BPMS:LI20:2360', 'BPMS:LI20:3013', 'BPMS:LI20:3036', 
            'BPMS:LI20:3101', 'BPMS:LI20:3120', 'BPMS:LI20:3340',
            ]
        s20_BPMs_EPICS = [
            "BPMS:LI20:2445", "BPMS:LI20:3156", "BPMS:LI20:3218", "BPMS:LI20:3265",
            "BPMS:LI20:3315"
            ]
        bpms = []
        for bpm_name in s20_BPMs_EPICS:
            bpm = BPM(bpm_name, edef='TH')
            if bpm.name in FacetOrbit.energy_bpms(): bpm.is_energy_bpm = True
            bpms.append(bpm)
        for bpm_name in s20_BPMs_SCP:
            bpm = FacetSCPBPM(bpm_name, suffix='57')
            if bpm.name in FacetOrbit.energy_bpms(): bpm.is_energy_bpm = True
            bpms.append(bpm)
        return bpms

    def set_DTOTR2_ROI(self):
        if get_pv(PV_DTOTR_TRACK_UPDATE).get() != 1: return
        try:
            cx,cy = calc_dtotr_centroid()
            self.ui.live_DTOTR2.getView().getViewBox().setLimits(
                xMin=cx-200, xMax=cx+200, yMin=cy-200, yMax=cy+200
                )
            return
        except:
            print('dtotr image processing failed')
            return
