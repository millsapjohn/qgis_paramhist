from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QDockWidget, QMainWindow
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
from .paramdock import ParamPanel

app = QgsApplication.instance()

class ParamHistPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.dock = ParamPanel()
        self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dock)

    def unload(self):
        self.iface.removeDockWidget(self.dock)
        del self.dock
