# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

import consts
import utils

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
    def __init__(self):
        super(ParamDialog, self).__init__()
        self.name.setPlaceholderText('Przykładowa nazwa')

        self.range_t.setPlaceholderText('-10,10,0.01')
        self.range_icon.setPixmap(utils.get_pixmap('info.png'))
        self.range_icon.setToolTip(consts.RANGE_INFO)

        self.function_x.setPlaceholderText('t')
        self.function_x_icon.setPixmap(utils.get_pixmap('info.png'))
        self.function_x_icon.setToolTip(consts.SUPPORTED_FUNCTIONS)

        self.function_y.setPlaceholderText('t^2')
        self.function_y_icon.setPixmap(utils.get_pixmap('info.png'))
        self.function_y_icon.setToolTip(consts.SUPPORTED_FUNCTIONS)

    def get_data(self):
        return {
            'name': self.name.text(),
            'range': self.range_t.text(),
            'function_x': self.function_x.text(),
            'function_y': self.function_y.text(),
        }

    def fill_data(self, data):
        self.name.setReadOnly(True)
        self.name.insert(data.get('name'))
        self.range_t.insert(data.get('range'))
        self.function_x.insert(data.get('function_x'))
        self.function_y.insert(data.get('function_y'))

    def validate(self):
        if not self.name.text():
            return False
        elif not self.range_t.text():
            return False
        elif not self.function_x.text():
            return False
        elif not self.function_y.text():
            return False
        return True


class InterpolateDialog(DialogMixin, UI_InterpolateDialog):
    def get_data(self):
        return {
            'name': self.name.text(),
            'function': self.function.text()
        }

    def fill_data(self, data):
        self.name.insert(data.get('name'))
        self.function.insert(data.get('function'))

    def validate(self):
        if not self.name.text():
            return False
        elif not self.function.text():
            return False
        return True
