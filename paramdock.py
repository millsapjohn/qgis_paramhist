from qgis.PyQt.QtWidgets import QDockWidget, QAction, QTableWidget, QTableWidgetItem
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface
from qgis.core import QgsApplication

class ParamPanel(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('ParamHistory')
        self.setWindowTitle("Param History")
        self.instance = QgsApplication.instance()
        self.histtable = QTableWidget(3, 3)
        self.histtable.setParent(self)
        self.histtable.show()

    def loadHistory(self):
        pass
        
    # TODO: populate table widget with history
    # TODO: add ability to re-launch algorithm with previous parameters from table
    # TODO: add ability to copy selected history item to clipboard (so you can put it in qNote)
