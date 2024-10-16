from qgis.PyQt.QtWidgets import (
                                QWidget,
                                QTextEdit,
                                QAbstractItemView,
                                QDockWidget, 
                                QTableWidget, 
                                QTableWidgetItem,
                                QHBoxLayout,
                                QVBoxLayout,
                                QLineEdit,
                                QLabel,
                                QPushButton,
                                )
from qgis.PyQt.QtGui import QIcon
import qgis.processing
from qgis.utils import iface
from qgis.core import QgsApplication
from .hist_connect import getProfileDb, getNewDb, readNewHistory, getSingleEntry, writeSingleEntry, parseSingleEntry, readSingleNewEntry

class ParamPanel(QDockWidget):
    def __init__(self, iface):
        super().__init__()
        self.setObjectName('ParamHistory')
        self.setWindowTitle("Param History")
        self.instance = QgsApplication.instance()
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.canvas.layersChanged.connect(self.updateHistory)
        # overall layout
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        # history table setup
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
        # detail box setup
        self.detaillayout = QVBoxLayout()
        self.detaillabel = QTextEdit("Detail View")
        self.detaillabel.setMinimumWidth(300)
        self.detaillabel.setMaximumWidth(500)
        self.detaillabel.setReadOnly(True)
        self.detaillayout.addWidget(self.detaillabel)
        self.clipbutton = QPushButton("Copy to Clipboard")
        self.clipbutton.clicked.connect(self.clipAction)
        self.detaillayout.addWidget(self.clipbutton)
        self.layout.addLayout(self.detaillayout)
        # search boxes setup
        self.searchlayout = QVBoxLayout()
        self.searchbox = QLineEdit()
        self.searchbox.setPlaceholderText("Search by Keyword")
        self.searchbox.setMaximumWidth(150)
        self.searchbox.textChanged.connect(self.findItem)
        self.searchlayout.addWidget(self.searchbox)
        self.datebox = QLineEdit()
        self.datebox.setPlaceholderText("Search by Date")
        self.datebox.setMaximumWidth(150)
        self.datebox.textChanged.connect(self.findDate)
        self.searchlayout.addWidget(self.datebox)
        self.layout.addLayout(self.searchlayout)
        # final UI setup
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
        split_params = raw_params.split(';')
        stripped_params = [item.strip() for item in split_params]
        for item in stripped_params:
            if item == '' or item == ' ':
                stripped_params.pop(stripped_params.index(item))
        resplit_params = [item.split(': ') for item in stripped_params]
        raw_param_dict = dict((param, value) for param, value in resplit_params)
        final_param_dict = {key: val for key, val in raw_param_dict.items() if key != 'unknown' and raw_param_dict.get(key) != 'N/A'}
        final_param_dict.update((key, value.split()) for key, value in final_param_dict.items() if key == 'TABLE')
        qgis.processing.execAlgorithmDialog(id, final_param_dict)

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

    def findDate(self):
        search_term = self.datebox.text().lower()
        num_rows = self.histtable.rowCount()
        if num_rows != 0 and len(search_term) != 0:
            for row in range(self.histtable.rowCount()):
                item = self.histtable.item(row, 2)
                self.histtable.setRowHidden(row, search_term not in item.text().lower())

    def clipAction(self):
        self.instance.clipboard().setText(self.detaillabel.toPlainText())

    def updateHistory(self):
        oldDb = getProfileDb(self.instance)
        newDb = getNewDb(self.instance)
        singleEntry = getSingleEntry(oldDb)
        if singleEntry[0] == self.histtable.item(0, 2).text():
            pass
        else:
            parsedEntry = parseSingleEntry(singleEntry)
            writeSingleEntry(newDb, parsedEntry)
            newEntry = readSingleNewEntry(newDb)
            rowCount = self.histtable.rowCount()
            id = newEntry[0]
            try:
                icon = self.instance.processingRegistry().algorithmById(id).icon()
            except AttributeError:
                icon = QIcon(":/qt-project.org/styles/commonstyle/images/stop-32.png")
            self.histtable.insertRow(0)
            icontableitem = QTableWidgetItem()
            icontableitem.setIcon(icon)
            self.histtable.setItem(0, 0, icontableitem)
            algtableitem = QTableWidgetItem(newEntry[1])
            self.histtable.setItem(0, 1, algtableitem)
            timestamptableitem = QTableWidgetItem(newEntry[3])
            self.histtable.setItem(0, 2, timestamptableitem)
            paramtableitem = QTableWidgetItem(newEntry[2])
            self.histtable.setItem(0, 3, paramtableitem)
            idtableitem = QTableWidgetItem(newEntry[0])
            self.histtable.setItem(0, 4, idtableitem)
