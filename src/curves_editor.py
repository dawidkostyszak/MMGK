# -*- coding: utf-8 -*-

import os
import sys

import matplotlib as mp
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

import curves
import dialogs
import widgets
from figure import CustomFigure

Ui_MainWindow, QMainWindow = loadUiType("designs/curves_editor_design.ui")

BUTTONS = {
    'LPM': 1,
    'PPM': 3,
}


class CurvesEditor(QMainWindow, Ui_MainWindow):
    """
    Main class for curves editor
    """

    figure = None
    figures = {}

    active_curve = None
    active_point = {
        'id': None,
        'press': False
    }

    def __init__(self):
        super(CurvesEditor, self).__init__()
        self.point_binded = False
        self.canvas = None
        self.toolbar = None
        self.setup_ui()
        self.custom_settings()
        self.bind_actions()
        self.show()

    def setup_ui(self):
        super(CurvesEditor, self).setupUi(self)

        self.figures_list = widgets.FiguresList()
        self.curves_list = widgets.CurvesList()
        self.edit_curve_data = widgets.EditCurveData()
        self.curve_points = widgets.CurvePoints()

        self.curves_layout.addWidget(self.figures_list)
        self.curves_layout.addWidget(self.curves_list)
        self.curves_layout.addWidget(self.edit_curve_data)
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
        self.edit_curve_data.change_curve_data.clicked.connect(
            self.__handle_editing
        )

    def unbind_point_actions(self):
        param_curve = isinstance(self.active_curve, curves.ParametricCurve)
        if param_curve or not self.point_binded:
            return

        self.canvas.mpl_disconnect(self.cid_press)
        self.canvas.mpl_disconnect(self.cid_release)
        self.canvas.mpl_disconnect(self.cid_pick)
        self.canvas.mpl_disconnect(self.cid_motion)
        self.point_binded = False

    def bind_point_actions(self):
        param_curve = isinstance(self.active_curve, curves.ParametricCurve)
        if param_curve or self.point_binded:
            return

        self.cid_press = self.canvas.mpl_connect(
            'button_press_event',
            self.__add_point
        )
        self.cid_release = self.canvas.mpl_connect(
            'button_release_event',
            self.__on_release
        )
        self.cid_pick = self.canvas.mpl_connect(
            'pick_event',
            self.__pick_point
        )
        self.cid_motion = self.canvas.mpl_connect(
            'motion_notify_event',
            self.__move_point
        )
        self.point_binded = True

    def __add_point(self, event):
        if event.button != BUTTONS.get('LPM') or not self.active_curve:
            return

        index = self.active_point['id']
        if index is not None:
            index += 1

        self.active_curve.add_point(event, index)

    def __pick_point(self, event):
        if event.artist != self.active_curve.help_line:
            return

        self.active_point['press'] = True
        self.active_point['id'] = event.ind[0]

    def __move_point(self, event):
        is_ppm = event.button == BUTTONS.get('PPM')
        if not (self.active_point['press'] and is_ppm):
            return

        self.active_curve.edit_point(event, self.active_point['id'])
        self.canvas.draw()

    def __on_release(self, event):
        self.active_point['press'] = False
        self.active_point['id'] = None
        if self.active_curve:
            self.update_plot()

    def __handle_editing(self):
        self.active_curve.edit()

    def __translate_curve(self):
        if not self.active_curve:
            return
        self.active_curve.translate()

    def __rotate_curve(self):
        if not self.active_curve:
            return
        self.active_curve.rotate()

    def add_toolbar(self):
        self.toolbar = widgets.CustomNavigationToolbar(
            self, self.canvas, self.draw_view
        )
        self.draw_layout.addWidget(self.toolbar)

    def __add_curve(self, curve):
        """
        Add new curve to curves list and update draw
        :param curve
        """
        created = curve.create()
        if not created:
            return

        if self.active_curve:
            self.unbind_point_actions()
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

        self.bind_point_actions()

    def __change_curve(self, item):
        """
        Update curve
        :param item:
        """
        self.unbind_point_actions()
        name = item.text()
        mp.artist.setp(self.active_curve.line, linewidth=1)
        self.active_curve = self.figure.curves[name]
        mp.artist.setp(self.active_curve.line, linewidth=4)
        self.update_plot()

        self.bind_point_actions()

    def __clear_curve_data(self):
        self.curve_points.table.setRowCount(0)

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

    def __open_project(self):
        """
        Open file with project amd draw on screen
        """
        filename = self.open_file()

        if filename:
            f = open(filename, 'r')

            with f:
                data = f.read()

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
        self.__add_curve(curve)

    def __draw_parametric_curve(self):
        curve = curves.ParametricCurve(self)
        self.__add_curve(curve)

    def __draw_bezier_curve(self):
        """
        Draw bezier curve
        """
        curve = curves.BezierCurve(self)
        self.__add_curve(curve)

    def update_plot(self):
        self.__clear_curve_data()
        xs, ys = self.active_curve.help_line.get_data()

        for i in range(len(xs)):
            self.curve_points.table.insertRow(i)
            self.curve_points.table.setItem(
                i, 0, QtWidgets.QTableWidgetItem(str(xs[i]))
            )
            self.curve_points.table.setItem(
                i, 1, QtWidgets.QTableWidgetItem(str(ys[i]))
            )

        self.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = CurvesEditor()
    sys.exit(app.exec_())