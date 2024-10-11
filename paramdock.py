from qgis.PyQt.QtWidgets import QDockWidget, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface

class ParamPanel(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('ParamHistory')
        self.setWindowTitle("Param History")
