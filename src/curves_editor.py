# -*- coding: utf-8 -*-

import os
import sys

import matplotlib as mp
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar
)
from PIL import Image
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

import curves
import dialogs
import utils
import widgets
from figure import CustomFigure

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

    figure = None
    figures = {}

    active_curve = None

    canvas = None
    toolbar = None

    def __init__(self):
        super(CurvesEditor, self).__init__()
        self.setup_ui()
        self.custom_settings()
        self.bind_actions()
        self.show()

    def setup_ui(self):
        super(CurvesEditor, self).setupUi(self)

        self.figures_list = widgets.FiguresList()
        self.curves_list = widgets.CurvesList()
        self.curves_data = widgets.CurvesData()
        self.curve_points = widgets.CurvePoints()

        self.curves_layout.addWidget(self.figures_list)
        self.curves_layout.addWidget(self.curves_list)
        self.curves_layout.addWidget(self.curves_data)
        self.curves_layout.addWidget(self.curve_points)

        self.edit.menuAction().setVisible(False)

    def custom_settings(self):
        self.curve_points.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

    def bind_actions(self):
        """
        Bind functions to action buttons
        """

        # Actions file
        self.action_new.triggered.connect(self.__add_figure)
        self.action_open.triggered.connect(self.__open_project)
        self.action_save.triggered.connect(self.__save_project_file)
        self.action_save_as.triggered.connect(self.__save_file)
        self.action_exit.triggered.connect(QtCore.QCoreApplication.quit)

        # Actions edit
        self.action_parametric.triggered.connect(self.__draw_parametric_curve)
        self.action_interpolate.triggered.connect(
            self.__draw_interpolate_curve
        )
        self.action_bezier.triggered.connect(self.__draw_bezier_curve)
        self.action_translate.triggered.connect(self.__translate_curve)
        self.action_rotate.triggered.connect(self.__rotate_curve)

        # Actions on lists
        self.figures_list.list.itemClicked.connect(self.__change_figure)
        self.curves_list.list.itemClicked.connect(self.__change_curve)

        # Actions on inputs
        self.curves_data.range_t.editingFinished.connect(self.__handle_editing)
        self.curves_data.function_x.editingFinished.connect(
            self.__handle_editing
        )
        self.curves_data.function_y.editingFinished.connect(
            self.__handle_editing
        )

    def __handle_editing(self):
        self.active_curve.edit()

    def __translate_curve(self):
        self.active_curve.translate()

    def __rotate_curve(self):
        self.active_curve.rotate()

    def add_toolbar(self):
        NavigationToolbar.toolitems = TOOLITEMS
        self.toolbar = NavigationToolbar(self.canvas, self.draw_view)
        extended_toolitems = (
            ('Tło', 'Dodaj tło', 'background.png', 'configure_background'),
        )

        for text, tooltip_text, image_file, callback in extended_toolitems:
            a = self.toolbar.addAction(
                utils.get_icon(image_file),
                text,
                getattr(self, callback)
            )

            if tooltip_text is not None:
                a.setToolTip(tooltip_text)

        self.draw_layout.addWidget(self.toolbar)

    def __add_curve(self, curve):
        """
        Add new curve to curves list and update draw
        :param curve
        """
        if self.active_curve:
            mp.artist.setp(self.active_curve.line, linewidth=1)

        self.active_curve = curve
        self.figure.curves[curve.name] = curve

        mp.artist.setp(self.active_curve.line, linewidth=4)

        self.curves_list.list.addItem(self.active_curve.name)
        item = self.curves_list.list.findItems(
            self.active_curve.name,
            QtCore.Qt.MatchFixedString
        )[-1]
        self.curves_list.list.setCurrentItem(item)

        self.update_plot()

    def __change_curve(self, item):
        """
        Update curve
        :param item:
        """
        name = item.text()
        mp.artist.setp(self.active_curve.line, linewidth=1)
        self.active_curve = self.figure.curves[name]
        mp.artist.setp(self.active_curve.line, linewidth=4)
        self.update_plot()

    def __clear_curve_data(self):
        self.curve_points.table.setRowCount(0)
        self.curves_data.range_t.clear()
        self.curves_data.function_x.clear()
        self.curves_data.function_y.clear()

    def __add_figure(self):
        """
        Create new figure and add to figures list and update draw
        """
        dialog = dialogs.FigureDialog()

        if dialog.exec_():
            data = dialog.get_data()
            name = data.get('name')

            self.edit.menuAction().setVisible(True)

            self.__clear_figure_data()
            self.__clear_curve_data()

            self.figure = CustomFigure(self)
            self.figure.create(name)

            self.figures[name] = self.figure
            self.figures_list.list.addItem(name)
            item = self.figures_list.list.findItems(
                name,
                QtCore.Qt.MatchFixedString
            )[0]
            self.figures_list.list.setCurrentItem(item)

    def __change_figure(self, item):
        name = item.text()
        self.__clear_figure_data()
        self.__clear_curve_data()
        self.figure = self.figures[name]
        self.figure.draw_figure()
        for curve_name in self.figure.curves.keys():
            self.curves_list.list.addItem(curve_name)

    def __clear_figure_data(self):
        if self.figure:
            self.figure.clear()
            self.curves_list.list.clear()

    def __remove_figure(self, item):
        self.figure.clear()
        name = item.text()
        del self.figures[name]

    def __open_file(self):
        """
        Open file
        :return: filename
        """
        filename, ext = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Otwórz plik'
        )
        return filename

    def __open_project(self):
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
        filename = self.__open_file()

        if filename:
            img = Image.open(filename)
            ax = self.figure.axes[0]

            x0, x1 = ax.get_xlim()
            y0, y1 = ax.get_ylim()
            ax.imshow(img, extent=[x0, x1, y0, y1], aspect='auto')

            self.canvas.draw()
            # self.update_plot()

    @staticmethod
    def __save_project_file():
        """
        Save file as project with special extension
        """
        file_name = 'test.txt'
        f = open(file_name, 'w')
        f.write('test')
        f.close()

    def __save_file(self):
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

    def __draw_interpolate_curve(self):
        """
        Draw interpolate curve
        """
        curve = curves.InterpolateCurve(self)
        curve.create()
        self.__add_curve(curve)

    def __draw_parametric_curve(self):
        curve = curves.ParametricCurve(self)
        created = curve.create()
        if created:
            self.__add_curve(curve)

    def __draw_bezier_curve(self):
        """
        Draw bezier curve
        """
        curve = curves.BezierCurve(self)
        curve.create()
        self.__add_curve(curve)

    def update_plot(self):
        self.__clear_curve_data()
        xs, ys = self.active_curve.line.get_data()

        for i in range(len(xs)):
            self.curve_points.table.insertRow(i)
            self.curve_points.table.setItem(
                i, 0, QtWidgets.QTableWidgetItem(str(xs[i]))
            )
            self.curve_points.table.setItem(
                i, 1, QtWidgets.QTableWidgetItem(str(ys[i]))
            )

        self.curves_data.range_t.insert(
            self.active_curve.data.get('range')
        )
        self.curves_data.function_x.insert(
            self.active_curve.data.get('function_x')
        )
        self.curves_data.function_y.insert(
            self.active_curve.data.get('function_y')
        )

        self.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = CurvesEditor()
    sys.exit(app.exec_())
