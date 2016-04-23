from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

UI_ParamDialog, _ = loadUiType("designs/param_curve_dialog.ui")
UI_InterpolateDialog, _ = loadUiType("designs/interpolate_curve_dialog.ui")
UI_TranslateDialog, _ = loadUiType("designs/translate_curve_dialog.ui")
UI_RotateDialog, _ = loadUiType("designs/rotate_curve_dialog.ui")
UI_FigureDialog, _ = loadUiType("designs/add_figure_dialog.ui")


class DialogMixin(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def get_data(self):
        pass


class FigureDialog(DialogMixin, UI_FigureDialog):
    def get_data(self):
        return {
            'name': self.name.text()
        }


class TranslateDialog(DialogMixin, UI_TranslateDialog):
    def get_data(self):
        return {
            'x': self.translate_x.value(),
            'y': self.translate_y.value()
        }


class RotateDialog(DialogMixin, UI_RotateDialog):
    def get_data(self):
        return self.angle.value()


class ParamDialog(DialogMixin, UI_ParamDialog):
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


class InterpolateDialog(DialogMixin, UI_InterpolateDialog):
    def get_data(self):
        return {
            'name': self.name.text(),
            'points': self.points.text()
        }
