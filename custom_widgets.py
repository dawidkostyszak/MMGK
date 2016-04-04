import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

UI_ParamDialog, _ = loadUiType("designs/param_curve_dialog.ui")


class ParamDialog(QtWidgets.QDialog, UI_ParamDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    @staticmethod
    def parse_curve_function(func):
        pars_list = [
            ('^', '**'), ('sin', 'np.sin'), ('cos', 'np.cos'), ('tg', 'np.tg'),
            ('ctg', 'np.ctg'), ('sqrt', 'np.sqrt')
        ]
        if func:
            for i, j in pars_list:
                func = func.replace(i, j)

        return func

    def parse_range(self):
        range_t = self.range_t.text()
        if range_t:
            for i in ['[', ']']:
                range_t = range_t.strip(i)
            range_t = range_t.replace('pi', str(np.pi))
            range_t = range_t.split(',')
            range_t = map(eval, range_t)
        else:
            range_t = [0, 0, 0]

        return {
            'min': float(range_t[0]),
            'max': float(range_t[1]),
            'interval': float(range_t[2])
        }

    def get_values(self):
        return {
            'name': self.name.text(),
            'param': self.param_a.text(),
            'range': self.parse_range(),
            'function_x': self.parse_curve_function(self.function_x.text()),
            'function_y': self.parse_curve_function(self.function_y.text()),
        }