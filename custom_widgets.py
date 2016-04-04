from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

UI_ParamDialog, _ = loadUiType("designs/param_curve_dialog.ui")
UI_CurvePoints, _ = loadUiType("designs/curve_points.ui")
UI_CurvesData, _ = loadUiType("designs/curves_data.ui")
UI_CurvesList, _ = loadUiType("designs/curves_list.ui")


class CurvesList(QtWidgets.QWidget, UI_CurvesList):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)


class CurvesData(QtWidgets.QWidget, UI_CurvesData):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

    def get_data(self):
        return {
            'range': self.range_t.text(),
            'function_x': self.function_x.text(),
            'function_y': self.function_y.text(),
        }


class CurvePoints(QtWidgets.QWidget, UI_CurvePoints):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)


class ParamDialog(QtWidgets.QDialog, UI_ParamDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def get_data(self):
        return {
            'name': self.name.text(),
            'range': self.range_t.text(),
            'function_x': self.function_x.text(),
            'function_y': self.function_y.text(),
        }

    def validate(self):
        if not self.name.text():
            return False
        if not self.range_t.text():
            return False
        if not self.function_x.text():
            return False
        if not self.function_y.text():
            return False
        return True
