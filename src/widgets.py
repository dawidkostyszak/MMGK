from PyQt5 import QtWidgets
from PyQt5.uic import loadUiType

import consts
import utils

UI_CurvePoints, _ = loadUiType("designs/curve_points.ui")
UI_EditCurveData, _ = loadUiType("designs/edit_curve_data.ui")
UI_CurvesList, _ = loadUiType("designs/curves_list.ui")
UI_FiguresList, _ = loadUiType("designs/figures_list.ui")


class WidgetMixin(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)


class FiguresList(WidgetMixin, UI_FiguresList):
    pass


class CurvesList(WidgetMixin, UI_CurvesList):
    pass


class EditCurveData(WidgetMixin, UI_EditCurveData):
    pass


class CurvePoints(WidgetMixin, UI_CurvePoints):
    pass
