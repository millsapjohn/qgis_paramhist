from qgis.PyQt.QtWidgets import (
                                QWidget,
                                QTextEdit,
                                QAbstractItemView,
                                QDockWidget, 
                                QTableWidget, 
                                QTableWidgetItem,
                                QHBoxLayout,
                                QLineEdit,
                                QLabel,
                                )
from qgis.PyQt.QtGui import QIcon
import qgis.processing
from qgis.utils import iface
from qgis.core import QgsApplication
from .hist_connect import getNewDb, readNewHistory

class ParamPanel(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('ParamHistory')
        self.setWindowTitle("Param History")
        self.instance = QgsApplication.instance()
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.histtable = QTableWidget()
        self.histtable.setColumnCount(5)
        self.histtable.setHorizontalHeaderLabels(["", "Algorithm", "Timestamp"])
        self.loadHistory()
        self.histtable.resizeColumnToContents(0)
        self.histtable.resizeColumnToContents(1)
        self.histtable.resizeColumnToContents(2)
        self.histtable.setMaximumWidth(500)
        self.histtable.itemClicked.connect(self.populateDetailView)
        self.histtable.itemDoubleClicked.connect(self.launchAlgorithm)
        self.layout.addWidget(self.histtable)
        self.detaillabel = QTextEdit("Detail View")
        self.detaillabel.setMinimumWidth(300)
        self.detaillabel.setMaximumWidth(500)
        self.detaillabel.setReadOnly(True)
        self.layout.addWidget(self.detaillabel)
        self.searchbox = QLineEdit()
        self.searchbox.setPlaceholderText("Search")
        self.searchbox.setMaximumWidth(150)
        self.searchbox.textChanged.connect(self.findItem)
        self.layout.addWidget(self.searchbox)
        self.widget.setLayout(self.layout)
        self.setWidget(self.widget)

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
            icontableitem = QTableWidgetItem()
            icontableitem.setIcon(icon)
            self.histtable.setItem(pos, 0, icontableitem)
            algtableitem = QTableWidgetItem(item[1])
            self.histtable.setItem(pos, 1, algtableitem)
            timestamptableitem = QTableWidgetItem(item[3])
            self.histtable.setItem(pos, 2, timestamptableitem)
            paramtableitem = QTableWidgetItem(item[2])
            self.histtable.setItem(pos, 3, paramtableitem)
            idtableitem = QTableWidgetItem(item[0])
            self.histtable.setItem(pos, 4, idtableitem)
            pos += 1
        self.histtable.sortItems(2, 1)
        self.histtable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.histtable.setColumnHidden(3, True)
        self.histtable.setColumnHidden(4, True)

    def populateDetailView(self):
        row = self.histtable.currentItem().row()
        algo = self.histtable.item(row, 1).text()
        time = self.histtable.item(row, 2).text()
        params = self.parseParams(self.histtable.item(row, 3).text())
        self.detailstring = "Algorithm: " + algo + "\n" + "time: " + time + "\n" + "Parameters: \n" + params
        self.detaillabel.setText(self.detailstring)

    def launchAlgorithm(self):
        row = self.histtable.currentItem().row()
        id = self.histtable.item(row, 4).text()
        raw_params = self.histtable.item(row, 3).text()
        qgis.processing.execAlgorithmDialog(id)

    def parseParams(self, params):
        parsed_params = params.replace(";", "\n")
        return parsed_params

    def findItem(self):
        search_term = self.searchbox.text().lower()
        num_rows = self.histtable.rowCount()
        if num_rows != 0 and len(search_term) != 0:
            for row in range(self.histtable.rowCount()):
                item = self.histtable.item(row, 1)
                self.histtable.setRowHidden(row, search_term not in item.text().lower())
        
    # TODO: add ability to copy selected history item to clipboard (so you can put it in qNote)
    # TODO: connect to algorithm run signal to update history
