# -*- coding: utf-8 -*-
import os
import sys

import matplotlib as mp
from curves import ParametricCurve
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUiType

from custom_widgets import CurvePoints, CurvesData, CurvesList

Ui_MainWindow, QMainWindow = loadUiType("designs/curves_editor_design.ui")
TOOLITEMS = (
    ('Przesuń', 'PPM - przesuń skalę, LPM - przybliż/oddal skalę', 'move', 'pan'),
    ('Zoom', 'Przybliż krzywą', 'zoom_to_rect', 'zoom'),
    (None, None, None, None),
    ('Krzywa', 'Konfiguruj krzywą', 'subplots', 'configure_subplots'),
)


class CurvesEditor(QMainWindow, Ui_MainWindow):
    """
    Main class for curves editor
    """

    curves = {}
    canvas = None
    curve = None
    lines = None
    toolbar = None

    def __init__(self):
        super(CurvesEditor, self).__init__()
        self.setup_ui()
        self.custom_settings()
        self.bind_actions()
        self.show()

    def setup_ui(self):
        super(CurvesEditor, self).setupUi(self)

        self.curves_list = CurvesList()
        self.curves_data = CurvesData()
        self.curve_points = CurvePoints()

        self.curves_layout.addWidget(self.curves_list)
        self.curves_layout.addWidget(self.curves_data)
        self.curves_layout.addWidget(self.curve_points)

    def custom_settings(self):
        self.curve_points.table.setColumnWidth(0, 90)
        self.curve_points.table.setColumnWidth(1, 90)

    def bind_actions(self):
        """
        Bind functions to action buttons
        """
        self.action_new.triggered.connect(self.clear_all)
        self.action_open.triggered.connect(self.open_project)
        self.action_save.triggered.connect(self.save_project_file)
        self.action_save_as.triggered.connect(self.save_file)
        self.action_exit.triggered.connect(QtCore.QCoreApplication.quit)

        self.action_parametric.triggered.connect(self.draw_parametric_curve)
        self.action_interpolate.triggered.connect(self.draw_interpolate_curve)
        self.action_bezier.triggered.connect(self.draw_bezier_curve)
        self.action_translate.triggered.connect(self.__translate_curve)
        self.action_rotate.triggered.connect(self.__rotate_curve)

        self.curves_list.list.itemClicked.connect(self.change_fig)

        self.curves_data.range_t.editingFinished.connect(self.__handle_editing)
        self.curves_data.function_x.editingFinished.connect(
            self.__handle_editing
        )
        self.curves_data.function_y.editingFinished.connect(
            self.__handle_editing
        )

    def __handle_editing(self):
        self.curve.edit()

    def __translate_curve(self):
        self.curve.translate()

    def __rotate_curve(self):
        self.curve.rotate()

    def add_toolbar(self):
        def _icon(name):
            basedir = os.path.join(mp.rcParams['datapath'], 'images')
            return QtGui.QIcon(os.path.join(basedir, name))

        NavigationToolbar.toolitems = TOOLITEMS
        self.toolbar = NavigationToolbar(self.canvas, self.draw_view)
        extended_toolitems = (
            ('Tło', 'Dodaj tło', 'background', 'configure_background'),
        )

        for text, tooltip_text, image_file, callback in extended_toolitems:
            a = self.toolbar.addAction(
                _icon(image_file + '.png'),
                text,
                getattr(self, callback)
            )

            if tooltip_text is not None:
                a.setToolTip(tooltip_text)

        self.draw_layout.addWidget(self.toolbar)

    def change_fig(self, item):
        fig_name = item.text()
        self.curve = self.curves[fig_name]
        self.line = self.curve.figure.axes[0].lines[0]
        self.update_plot()

    def clear_all(self):
        """
        Clear all and create new file
        """
        self.curve = None
        self.curves = {}
        self.remove_plot()
        self.curves_list.list.clear()

    def open_file(self):
        """
        Open file
        :return: filename
        """
        filename, ext = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Otwórz plik'
        )
        return filename

    def open_project(self):
        """
        Open file with project amd draw on screen
        """
        filename = self.open_file()

        if filename:
            f = open(filename, 'r')

            with f:
                data = f.read()

    def configure_background(self):
        """
        Open file with image and draw as background
        """
        filename = self.open_file()

        if filename:
            img = Image.open(filename)
            ax = self.curve.figure.axes[0]

            x0, x1 = ax.get_xlim()
            y0, y1 = ax.get_ylim()
            ax.imshow(img, extent=[x0, x1, y0, y1], aspect='auto')

            self.update_plot()

    @staticmethod
    def save_project_file():
        """
        Save file as project with special extension
        """
        file_name = 'test.txt'
        f = open(file_name, 'w')
        f.write('test')
        f.close()

    def save_file(self):
        """
        Save file as image (BMP, JPG, PNG, etc.)
        """
        start_path = mp.rcParams.get('savefig.directory', '')
        start_path = os.path.expanduser(start_path)
        default_path = os.path.join(
            start_path,
            self.canvas.get_default_filename()
        )

        filename, ext = QtWidgets.QFileDialog.getSaveFileName(
            self,
            'Zapisz plik',
            default_path
        )

        if filename:
            extension = None
            try:
                filename.split('.')[1]
            except IndexError:
                extension = "PNG"

            pil_image = Image.frombytes(
                'RGB',
                self.canvas.get_width_height(),
                self.canvas.tostring_rgb()
            )
            pil_image.save(filename, extension)

    def get_fig_name(self, title):
        text, ok = QtWidgets.QInputDialog.getText(
            self,
            title,
            'Podaj nazwę krzywej:'
        )

        if ok and len(text.strip()) == 0:
            ok = False
        return text, ok

    def draw_interpolate_curve(self):
        """
        Draw interpolate curve
        """
        pass

    def draw_parametric_curve(self):
        self.curve = ParametricCurve(self)
        self.curve.draw()

    def draw_bezier_curve(self):
        """
        Draw bezier curve
        """
        fig_name, created = self.get_fig_name('Krzywa beziera')

        if created:
            pass

    def add_plot(self, fig_data):
        self.curves[fig_data.get('name')] = self.curve
        item = self.curves_list.list.addItem(fig_data.get('name'))
        self.curves_list.list.setCurrentItem(item)

        self.update_plot()

    def update_plot(self):
        self.remove_plot()

        xs, ys = self.line.get_data()

        for i in range(len(xs)):
            self.curve_points.table.insertRow(i)
            self.curve_points.table.setItem(
                i, 0, QtWidgets.QTableWidgetItem(str(xs[i]))
            )
            self.curve_points.table.setItem(
                i, 1, QtWidgets.QTableWidgetItem(str(ys[i]))
            )

        self.curves_data.range_t.insert(self.curve.data.get('range'))
        self.curves_data.function_x.insert(self.curve.data.get('function_x'))
        self.curves_data.function_y.insert(self.curve.data.get('function_y'))

        self.canvas = FigureCanvas(self.curve.figure)
        self.draw_layout.addWidget(self.canvas)
        self.canvas.draw()
        self.add_toolbar()

    def remove_plot(self):
        if self.canvas:
            self.draw_layout.removeWidget(self.canvas)
            self.draw_layout.removeWidget(self.toolbar)
            self.curve_points.table.setRowCount(0)
            self.curves_data.range_t.clear()
            self.curves_data.function_x.clear()
            self.curves_data.function_y.clear()
            self.canvas.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = CurvesEditor()
    sys.exit(app.exec_())
