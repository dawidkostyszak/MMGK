# -*- coding: utf-8 -*-

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from PIL import Image
from PyQt5 import QtWidgets
from PyQt5.uic import loadUiType

import consts
import dialogs
import utils

UI_CurvePoints, _ = loadUiType("designs/curve_points.ui")
UI_EditCurveData, _ = loadUiType("designs/edit_curve_data.ui")
UI_CurvesList, _ = loadUiType("designs/curves_list.ui")


class CustomNavigationToolbar(NavigationToolbar2QT):
    toolitems = consts.TOOLITEMS
    custom_toolitems = consts.EXTENDED_TOOLITEMS

    def __init__(self, ui, canvas, parent, coordinates=True):
        super(CustomNavigationToolbar, self).__init__(
            canvas, parent, coordinates
        )
        self.ui = ui

    def _init_toolbar(self):
        super(CustomNavigationToolbar, self)._init_toolbar()
        for text, tooltip_text, image_file, callback in self.custom_toolitems:
            a = self.addAction(
                utils.get_icon(image_file),
                text,
                getattr(self, callback)
            )

            if tooltip_text is not None:
                a.setToolTip(tooltip_text)

    def configure_background(self):
        """
        Open file with image and draw as background
        """
        dialog = dialogs.OpenFileDialog(self.ui)
        filename = dialog.open_file()

        if filename:
            img = Image.open(filename)
            ax = self.ui.figure.axes[0]

            x0, x1 = ax.get_xlim()
            y0, y1 = ax.get_ylim()
            ax.imshow(img, extent=[x0, x1, y0, y1], aspect='auto')

            self.canvas.draw()

    def pan(self, *args):
        super(CustomNavigationToolbar, self).pan(*args)
        if self._active == 'PAN':
            self.ui.unbind_point_actions()
        else:
            self.ui.bind_point_actions()

    def zoom(self, *args):
        super(CustomNavigationToolbar, self).zoom(*args)
        if self._active == 'ZOOM':
            self.ui.unbind_point_actions()
        else:
            self.ui.bind_point_actions()


class WidgetMixin(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)


class CurvesList(WidgetMixin, UI_CurvesList):
    pass


class EditCurveData(WidgetMixin, UI_EditCurveData):
    pass


class CurvePoints(WidgetMixin, UI_CurvePoints):
    pass
