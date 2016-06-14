# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

import consts
import utils

UI_ParamDialog, _ = loadUiType("designs/param_curve_dialog.ui")
UI_NameCurveDialog, _ = loadUiType("designs/name_curve_dialog.ui")
UI_TranslateDialog, _ = loadUiType("designs/translate_curve_dialog.ui")
UI_RotateDialog, _ = loadUiType("designs/rotate_curve_dialog.ui")
UI_FigureDialog, _ = loadUiType("designs/add_figure_dialog.ui")
UI_BezierOptionsDialog, _ = loadUiType("designs/bezier_curve_options_dialog.ui")
UI_NewtonOptionsDialog, _ = loadUiType("designs/newton_curve_options_dialog.ui")


class DialogMixin(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def get_data(self):
        pass


class OptionsDialogMixin(DialogMixin):
    action = None
    params = {}

    def get_action(self):
        return self.action

    def get_params(self):
        return self.params


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


class CurveNameDialog(DialogMixin, UI_NameCurveDialog):
    def get_data(self):
        return {
            'name': self.name.text()
        }

    def fill_data(self, data):
        self.name.insert(data.get('name'))

    def validate(self):
        if not self.name.text():
            return False
        return True


class OpenFileDialog(object):
    def __init__(self, ui):
        self.ui = ui

    def open_file(self):
        """
        Open file
        :return: filename
        """
        filename, ext = QtWidgets.QFileDialog.getOpenFileName(
            self.ui,
            'Otwórz plik'
        )
        return filename


class SaveFileDialog(QtWidgets.QFileDialog):
    default_path = 'untitled.json'

    def __init__(self, default_path=None):
        super(SaveFileDialog, self).__init__()
        if default_path:
            self.default_path = default_path

    def save(self):
        return self.getSaveFileName(self, 'Zapisz plik', self.default_path)


class NewtonOptionsDialog(OptionsDialogMixin, UI_NewtonOptionsDialog):
    def __init__(self):
        super(NewtonOptionsDialog, self).__init__()
        self.convert.clicked.connect(self.__handle_convert)

    def __handle_convert(self):
        self.action = 'transform_newton_to_bezier'
        self.accept()


class BezierOptionsDialog(OptionsDialogMixin, UI_BezierOptionsDialog):
    def __init__(self):
        super(BezierOptionsDialog, self).__init__()
        self.increase.clicked.connect(self.__handle_increase)
        self.reduce.clicked.connect(self.__handle_reduce)

    def __handle_increase(self):
        self.action = 'bezier_degree_elevation'
        self.params['number'] = self.increase_number.value()
        self.accept()

    def __handle_reduce(self):
        self.action = 'bezier_degree_reduction'
        self.params['number'] = self.reduce_number.value()
        self.accept()
