from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsSimpleTextItem
from PyQt5.QtGui import QBrush, QColor

class BPMLineItem(QGraphicsLineItem):
	text_brush = QBrush(QColor(255,255,255))
	def __init__(self, bpm, parent=None):
		super(BPMLineItem, self).__init__(bpm.z, 0.0, bpm.z, 0.0, parent=parent)
		#self.setAcceptHoverEvents(True)
		self.bpm = bpm
		self.setToolTip(self.bpm.name)
