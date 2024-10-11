from qgis.PyQt.QtWidgets import QDockWidget, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface

class ParamPanel(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('ParamHistory')
        self.setWindowTitle("Param History")

    def loadHistory(self):
        # TODO: get dbs, fetch histories, parse histories
        pass

    # TODO: combine, sort histories
    # TODO: populate table widget with combined history
    # TODO: add algorithm icon to table
    # TODO: add ability to re-launch algorithm with previous parameters from table
    # TODO: connect to whatever signal is emitted by an algorithm to dynamically update history
    # TODO: save history table in project to avoid expensive re-fetch every time it opens?
    # TODO: add ability to copy selected history item to clipboard (so you can put it in qNote)
