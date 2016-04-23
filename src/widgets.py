from PyQt5 import QtWidgets
from PyQt5.uic import loadUiType

UI_CurvePoints, _ = loadUiType("designs/curve_points.ui")
UI_CurvesData, _ = loadUiType("designs/curves_data.ui")
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


class CurvesData(WidgetMixin, UI_CurvesData):
    def get_data(self):
        return {
            'range': self.range_t.text(),
            'function_x': self.function_x.text(),
            'function_y': self.function_y.text(),
        }


class CurvePoints(WidgetMixin, UI_CurvePoints):
    pass
