from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QDockWidget, QMainWindow
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
import os
from .paramdock import ParamPanel
from .hist_connect import getProfileDb, getNewDb, fetchHistory, parseHistory, writeHistory

class ParamHistPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.instance = QgsApplication.instance()
        if self.checkDbExists() == True:
            pass
        else:
            self.history_db = getProfileDb(self.instance)
            self.raw_history = fetchHistory(self.history_db)
            self.parsed_history = parseHistory(self.raw_history)
            writeHistory(self.newdbpath, self.parsed_history)

    def initGui(self):
        self.dock = ParamPanel()
        self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dock)

    def unload(self):
        self.iface.removeDockWidget(self.dock)
        del self.dock

    def checkDbExists(self):
        self.newdbpath = getNewDb(self.instance)
        if os.path.exists(self.newdbpath):
            return True
        else:
            return False

# TODO: connect to whatever signal is emitted by an algorithm to dynamically update history
