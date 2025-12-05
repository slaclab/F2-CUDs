import math
import numpy as np
from PyQt5.QtWidgets import QGraphicsView, QGraphicsLineItem, QApplication, QMenu, QAction
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtCore import pyqtSlot, QLineF, QRectF, QPoint, QPointF, Qt, Q_ENUMS
from pyqtgraph import GraphicsLayoutWidget, PlotItem, ViewBox, GraphicsItem, GraphicsView, PlotDataItem, TextItem, ButtonItem, FillBetweenItem
from bpm_line_item import BPMLineItem
# from magnet_view import MagnetView
from PyQt5.QtCore import QTimer

class RMSMode(object):
    Off = 0
    FilledLine = 1
    Bars = 2

class OrbitView(GraphicsLayoutWidget):

    RMSMode = RMSMode
    Q_ENUMS(RMSMode)

    def __init__(self, orbit=None, axis="X", use_sector_ticks=True, parent=None, ymin=-1.0, ymax=1.0, name=None, label=None, units=None, draw_timer=None, magnet_list=None):
        super(OrbitView, self).__init__(parent=parent)
        axis = axis.lower()
        if axis not in ["x", "y", "tmit"]:
            raise Exception("Axis must be 'x', 'y', or 'tmit'")
        self.axis = axis
        self.use_sector_ticks = use_sector_ticks
        self.sector_ticks = [[],[]]
        self.ci.layout.setSpacing(0.0)
        plot_label = name
        if units:
            plot_label = plot_label + " ({})".format(units)
        #self.up_magnet_view = MagnetView(magnet_list=orbit, direction="up")
        #self.up_magnet_view.hideAxis('left')
        #self.up_magnet_view.hideAxis('bottom')
        self.ci.layout.setRowStretchFactor(0,3)
        self.plotItem = self.addPlot(name=name, row=0, col=1)
        self.ci.layout.setRowStretchFactor(1,0)
        #self.down_magnet_view = MagnetView(magnet_list=orbit, direction="down")
        #self.down_magnet_view.hideAxis('left')
        #self.up_magnet_view.setXLink(self.plotItem)
        #self.down_magnet_view.setXLink(self.plotItem)
        self.ci.layout.setRowStretchFactor(2,0)
        self.show_magnet_buttons = False
        #if axis != "tmit" and magnet_list is not None:
        #    self.show_magnet_views(True)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate) # Greatly improves drawing performance.
        self.plotItem.setMouseEnabled(y=False)
        #Customize the right-click menu.
        self.plotItem.setMenuEnabled(enableMenu=False, enableViewBoxMenu=None)
        reset_view_range = QAction("Reset View Range", self.plotItem.vb.menu)
        reset_view_range.triggered.connect(self.reset_range)
        self.plotItem.vb.scene().contextMenu = []
        existing_menu_actions = self.plotItem.vb.menu.actions()
        self.plotItem.vb.menu.insertAction(existing_menu_actions[0], reset_view_range)
        for action in existing_menu_actions:
            if str(action.text()) == "View All":
                self.plotItem.vb.menu.removeAction(action)
        self.plotItem.showGrid(y=True)
        self.plotItem.getAxis('left').setStyle(tickTextWidth=60)
        self.plotItem.getAxis('left').setStyle(autoExpandTextSpace=False)
        self.bpm_brush = QBrush(QColor(0, 255, 0))
        if label is not None:
            self.plotItem.getAxis('left').enableAutoSIPrefix(enable=False)
            self.plotItem.getAxis('left').setLabel(text=label, units=units)
        self.energy_bpm_brush = QBrush(QColor(100,200,255))
        self.ymin = ymin #Y axis goes from self.ymin to self.ymax by default.
        self.ymax = ymax
        self.yminlimit = 10.0*ymin #This is the limit on the Y axis range.
        self.ymaxlimit = 10.0*ymax #This is the upper limit on the Y axis range.
        self.plotItem.setLimits(minYRange=0.04, maxYRange=abs(self.ymaxlimit - self.yminlimit))
        self.axis_pen = QPen(QBrush(QColor(255,255,255)), 0)
        self.axis_pen.setCapStyle(Qt.FlatCap)
        self.bpm_pen = QPen(self.bpm_brush, 2)
        self.bpm_pen.setCosmetic(True)
        self.bpm_pen.setCapStyle(Qt.FlatCap)
        self.no_beam_brush = QBrush(QColor(0,255,0,255))
        self.no_beam_pen = QPen(self.no_beam_brush, 2)
        self.no_beam_pen.setCosmetic(True)
        self.no_beam_pen.setCapStyle(Qt.FlatCap)
        self.energy_bpm_pen = QPen(self.energy_bpm_brush, 2)
        self.energy_bpm_pen.setCosmetic(True)
        self.energy_bpm_pen.setCapStyle(Qt.FlatCap)
        self.fit_brush = QBrush(QColor(255,255,255,255))
        self.fit_pen = QPen(self.fit_brush, 0)
        self.fit_pen.setCosmetic(True)
        self.fit_pen.setCapStyle(Qt.FlatCap)
        self.rms_brush = QBrush(QColor(170,170,255,255))
        self.rms_fill_brush = QBrush(QColor(50,50,255,120))
        self.rms_pen = QPen(self.rms_brush, 0)
        self.rms_pen.setCosmetic(True)
        self.rms_pen.setCapStyle(Qt.FlatCap)
        self.axis_line = QGraphicsLineItem(0.0,0.0,1.0,0.0)
        self.axis_line.setPen(self.axis_pen)
        self.plotItem.addItem(self.axis_line, ignoreBounds=True)
        self.lines = {}
        self.orbit = None
        self.needs_initial_range = True
        self.set_draw_timer(draw_timer)
        self._display_fit = False
        self._rms_mode = RMSMode.Off
        self.fit_data_item = None
        self.rms_data_item = None
        self.zero_data_item = None
        self.rms_fill_item = None
        self.fit_options = {}
        if orbit is not None:
            self.set_orbit(orbit)
    
    def make_right_click_menu(self):
        menu = QMenu(self)
        return menu

    def display_rms(self, rms_mode):
        if rms_mode == RMSMode.FilledLine:
            if self.rms_data_item is None:
                self.rms_data_item = PlotDataItem(pen=self.rms_pen)
                self.zero_data_item = PlotDataItem(pen=self.axis_pen)
                self.zero_data_item.setData(x=self.orbit.z_vals(), y=np.zeros(len(self.orbit.z_vals())))
                self.rms_fill_item = FillBetweenItem(curve1=self.rms_data_item, curve2=self.zero_data_item, brush=self.rms_fill_brush)
                self.plotItem.addItem(self.rms_data_item)
                self.plotItem.addItem(self.zero_data_item)
                self.plotItem.addItem(self.rms_fill_item)
                self.rms_data_item.setZValue(-10.0)
                self.rms_fill_item.setZValue(-20.0)
            self.rms_data_item.show()
            self.rms_fill_item.show()
        else:
            self.plotItem.removeItem(self.rms_fill_item)
            self.plotItem.removeItem(self.rms_data_item)
            self.plotItem.removeItem(self.zero_data_item)
            self.rms_data_item = None
            self.rms_fill_item = None
            self.zero_data_item = None
        self._rms_mode = rms_mode

    def display_fit(self, enabled=True):
        if enabled and self.fit_data_item is None:
            self.fit_data_item = PlotDataItem(pen=self.fit_pen)
            self.plotItem.addItem(self.fit_data_item)
        elif not enabled:
            self.plotItem.removeItem(self.fit_data_item)
            self.fit_data_item = None
        self._display_fit = enabled
        
    def set_draw_timer(self, new_timer, start=False):
        try:
            self.draw_timer.timeout.disconnect(self.redraw_bpms)
        except:
            pass
        if new_timer is None:
            new_timer = QTimer(self)
            new_timer.setInterval(int(1000/60))
        self.draw_timer = new_timer
        self.draw_timer.timeout.connect(self.redraw_bpms)
        if start:
            self.draw_timer.start()
            
    def set_orbit(self, orbit, reset_range=True, show_title=False):
        if self.orbit == orbit:
            return
        old_range = None
        old_zmax = None
        old_zmin = None
        if self.orbit is not None:
            old_range = self.plotItem.viewRect()
            old_zmax = self.orbit.zmax()
            old_zmin = self.orbit.zmin()
        self.clear_orbit()
        self.orbit = orbit
        extent = self.orbit.zmax() - self.orbit.zmin()
        self.plotItem.setLimits(xMin=self.orbit.zmin()-(0.02*extent), xMax=self.orbit.zmax()+(0.02*extent))
        self.plotItem.enableAutoRange(enable=False)
        self.axis_line.setLine(self.orbit.zmin(),0.0,self.orbit.zmax(),0.0)
        if show_title and self.orbit.name:
            self.plotItem.setTitle("<h2>{}</h2>".format(self.orbit.name))
        for bpm in self.orbit:
            line = BPMLineItem(bpm)
            self.lines[bpm.name] = line
            self.set_pen_for_bpm(bpm)
            self.plotItem.addItem(self.lines[bpm.name])
            self.lines[bpm.name].setZValue(50.0)
        if self.use_sector_ticks:
            self.sector_ticks = [[],[]]
            self.sector_ticks[0] = self.orbit.sector_locations()
            unit_nums = [name.split(":")[-1] for name in self.orbit.names()]
            self.sector_ticks[1] = list(zip(self.orbit.z_vals(), unit_nums))
            self.plotItem.getAxis('bottom').setTicks(self.sector_ticks)
            self.plotItem.getAxis('bottom').setStyle(textFillLimits=[(0,0.72)])
            self.plotItem.showGrid(x=True)
        if reset_range or self.needs_initial_range:
            self.reset_range()
            self.needs_initial_range = False
        else:
            self.plotItem.setRange(old_range, padding=0.0, update=False)
        self.draw_timer.start()

    def show_magnet_views(self, enabled):
        if enabled == self.show_magnet_buttons:
            return
        self.show_magnet_buttons = enabled
        if enabled:
            self.addItem(self.up_magnet_view, row=1, col=1)
            self.addItem(self.down_magnet_view, row=2, col=1)
            self.up_magnet_view.setXLink(self.plotItem)
            self.down_magnet_view.setXLink(self.plotItem)
        else:
            self.removeItem(self.up_magnet_view)
            self.removeItem(self.down_magnet_view)
    
    def set_magnet_list(self, magnet_list):
        self.up_magnet_view.set_magnets(magnet_list, reset_range=False)
        self.down_magnet_view.set_magnets(magnet_list, reset_range=False)

    @pyqtSlot(bool)
    def reset_range(self, checked=False):
        self.plotItem.enableAutoRange(axis=ViewBox.XAxis)
        self.plotItem.setYRange(self.ymin, self.ymax)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            numPixels = event.pixelDelta()
            numDegrees = event.angleDelta()
            if not numPixels.isNull():
                s = (1.005) ** (numPixels.y())
            else:
                s = (1.005) ** (numDegrees.y() * (-1.0/8.0))
            self.plotItem.vb.scaleBy(y=s)
        else:
            super(OrbitView, self).wheelEvent(event)
    
    def clear_orbit(self):
        self.draw_timer.stop()
        auto_range_x_enabled = self.plotItem.vb.state['autoRange'][0]
        auto_range_y_enabled = self.plotItem.vb.state['autoRange'][1]
        self.plotItem.enableAutoRange(enable=False)
        if self.orbit is None:
            return
        for bpm in self.orbit:
            self.plotItem.removeItem(self.lines[bpm.name])
        self.plotItem.enableAutoRange(x=auto_range_x_enabled, y=auto_range_y_enabled)
        self.lines = {}
            
    @pyqtSlot()
    def redraw_bpms(self):
        if self._rms_mode == RMSMode.Bars:
            for bpm in self.orbit:
                self.set_pen_for_bpm(bpm)
                self.lines[bpm.name].setLine(bpm.z,0.0,bpm.z,bpm.rms(self.axis))
        else:
            for bpm in self.orbit:
                self.set_pen_for_bpm(bpm)
                self.lines[bpm.name].setLine(bpm.z,0.0,bpm.z,bpm[self.axis])
        if self._rms_mode != RMSMode.Off:
            self.orbit.save_latest()
            self.update_rms()
        self.update_fit()

    def set_pen_for_bpm(self, bpm):
        if bpm.severity(self.axis) != 0:
            self.lines[bpm.name].setPen(self.no_beam_pen)
        else:
            if bpm.is_energy_bpm:
                self.lines[bpm.name].setPen(self.energy_bpm_pen)
            else:
                self.lines[bpm.name].setPen(self.bpm_pen)

    def update_fit(self):
        if not self._display_fit:
            return
        if self.orbit.fit_data is None:
            if self.fit_data_item is not None:
                self.fit_data_item.hide()
            return
        fit_data = None
        if self.axis == 'x':
            fit_data = self.orbit.fit_data['xpos']
        elif self.axis == 'y':
            fit_data = self.orbit.fit_data['ypos']
        self.fit_data_item.show()
        self.fit_data_item.setData(x=self.orbit.fit_data['zs'], y=fit_data)

    def update_rms(self):
        if self._rms_mode != RMSMode.FilledLine:
            return
        rms_data = self.orbit.rms(self.axis)
        self.rms_data_item.setData(x=self.orbit.z_vals(), y=rms_data)

    @pyqtSlot()
    def stop(self):
        self.draw_timer.stop()

    @pyqtSlot()
    def start(self):
        if self.orbit is not None:
            self.draw_timer.start()

    def set_bpm_color(self, new_color):
        self.bpm_brush = QBrush(new_color)
        self.bpm_pen = QPen(self.bpm_brush, 2)
        self.bpm_pen.setCosmetic(True)
        self.bpm_pen.setCapStyle(Qt.FlatCap)
        
    def setXLink(self, view):
        return self.plotItem.setXLink(view.plotItem)
        
    def setYLink(self, view):
        return self.plotItem.setYLink(view.plotItem)
