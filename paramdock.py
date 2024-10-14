from qgis.PyQt.QtWidgets import (
                                QDockWidget, 
                                QAction,
                                QTableWidget, 
                                QTableWidgetItem,
                                QVBoxLayout,
                                )
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface
from qgis.core import QgsApplication
from .hist_connect import getNewDb, readNewHistory

class ParamPanel(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('ParamHistory')
        self.setWindowTitle("Param History")
        self.instance = QgsApplication.instance()
        self.histtable = QTableWidget()
        self.histtable.setColumnCount(4)
        self.histtable.setHorizontalHeaderLabels(["", "Algorithm", "Parameters", "Timestamp"])
        self.loadHistory()
        self.histtable.setParent(self)
        self.histtable.show()

    def loadHistory(self):
        self.dbpath = getNewDb(self.instance)
        self.hist = readNewHistory(self.dbpath) # returns list of tuples
        pos = 0
        for item in self.hist:
            self.histtable.insertRow(pos)
            id = item[0]
            try:
                icon = self.instance.processingRegistry().algorithmById(id).icon()
            except AttributeError:
                icon = QIcon(":/qt-project.org/styles/commonstyle/images/stop-32.png")
            icontableitem = QTableWidgetItem("icon")
            self.histtable.setItem(pos, 0, icontableitem)
            algtableitem = QTableWidgetItem(item[1])
            self.histtable.setItem(pos, 1, algtableitem)
            paramtableitem = QTableWidgetItem(item[2])
            self.histtable.setItem(pos, 2, paramtableitem)
            timestamptableitem = QTableWidgetItem(item[3])
            self.histtable.setItem(pos, 3, timestamptableitem)
            pos += 1
        self.histtable.sortItems(3, 1)
        
    # TODO: add ability to re-launch algorithm with previous parameters from table
    # TODO: add ability to copy selected history item to clipboard (so you can put it in qNote)
    # TODO: expand params on click (text box to right)
