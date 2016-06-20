# -*- coding: utf-8 -*-

import json
import os
import matplotlib as mp

from PIL import Image
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

import consts
import curves
import dialogs
import utils
import widgets
from figure import CustomFigure

Ui_MainWindow, QMainWindow = loadUiType("designs/curves_editor_design.ui")


CURVE_TYPES = {
    'PARAM': curves.ParametricCurve,
    'NEWTON': curves.NewtonCurve,
    'BEZIER': curves.BezierCurve,
    'RATIONAL_BEZIER': curves.RationalBezierCurve
}


class CurvesEditor(QMainWindow, Ui_MainWindow):
    """
    Main class for curves editor
    """

    figure = None

    active_curve = None
    active_point = {
        'id': None,
        'press': False
    }

    def __init__(self, interface):
        super(CurvesEditor, self).__init__()
        self.point_binded = False
        self.shift_is_held = False
        self.ctrl_is_held = False
        self.canvas = None
        self.toolbar = None
        self.setup_ui(interface)
        self.custom_settings()
        self.bind_actions()
        self.show()

    def setup_ui(self, interface):
        super(CurvesEditor, self).setupUi(self)

        self.curves_list = widgets.CurvesList()
        self.edit_curve_data = widgets.EditCurveData()
        self.curve_points = widgets.CurvePoints(self)
        self.rational_curve_points = widgets.RationalCurvePoints(self)

        self.curves_layout.addWidget(self.curves_list)
        self.curves_layout.addWidget(self.edit_curve_data)
        self.curves_layout.addWidget(self.curve_points)
        self.curves_layout.addWidget(self.rational_curve_points)

        if interface == 'gnome':
            self.menubar.setVisible(True)

        self.edit.menuAction().setVisible(False)
        self.__toggle_curve_menu(False)

    def custom_settings(self):
        self.curve_points.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.rational_curve_points.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

    def __toggle_curve_menu(self, visible):
        self.curves_list.setVisible(visible)
        self.edit_curve_data.setVisible(visible)
        self.curve_points.setVisible(False)
        self.rational_curve_points.setVisible(False)
        if self.active_curve:
            if isinstance(self.active_curve, CURVE_TYPES['RATIONAL_BEZIER']):
                self.rational_curve_points.setVisible(True)
            else:
                self.curve_points.setVisible(True)

    def bind_actions(self):
        """
        Bind functions to action buttons
        """

        # Actions file
        self.action_new.triggered.connect(self.__handle_add_figure)
        self.action_open.triggered.connect(self.__open_project)
        self.action_save.triggered.connect(self.__save_project)
        self.action_save_as.triggered.connect(self.__save_file)
        self.action_exit.triggered.connect(QtCore.QCoreApplication.quit)

        # Actions edit
        self.action_parametric.triggered.connect(self.__draw_parametric_curve)
        self.action_interpolate.triggered.connect(
            self.__draw_interpolate_curve
        )
        self.action_bezier.triggered.connect(self.__draw_bezier_curve)
        self.action_rational_bezier.triggered.connect(
            self.__draw_rational_bezier_curve
        )
        self.action_translate.triggered.connect(self.__translate_curve)
        self.action_rotate.triggered.connect(self.__rotate_curve)
        self.action_copy.triggered.connect(self.__clone_curve)
        self.action_delete.triggered.connect(self.__delete_curve)

        # Actions on lists
        self.curves_list.list.itemClicked.connect(self.__change_curve)
        self.edit_curve_data.change_curve_data.clicked.connect(
            self.__handle_editing
        )
        self.edit_curve_data.curve_options.clicked.connect(
            self.__curve_options
        )

    def unbind_point_actions(self):
        """
        Unbind actions from point.
        ParametricCurve doesn't support dynamic points.
        """
        param_curve = isinstance(self.active_curve, CURVE_TYPES['PARAM'])
        if param_curve or not self.point_binded:
            return

        self.canvas.mpl_disconnect(self.cid_press)
        self.canvas.mpl_disconnect(self.cid_release)
        self.canvas.mpl_disconnect(self.cid_pick)
        self.canvas.mpl_disconnect(self.cid_motion)
        self.canvas.mpl_disconnect(self.cid_key_press)
        self.canvas.mpl_disconnect(self.cid_key_release)
        self.point_binded = False

    def bind_point_actions(self):
        """
        Bind actions from point.
        ParametricCurve doesn't support dynamic points.
        """
        param_curve = isinstance(self.active_curve, CURVE_TYPES['PARAM'])
        if param_curve or self.point_binded:
            return

        self.cid_press = self.canvas.mpl_connect(
            'button_press_event',
            self.__point_event
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

        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()
        self.cid_key_press = self.canvas.mpl_connect(
            'key_press_event',
            self.__on_key_press
        )
        self.cid_key_release = self.canvas.mpl_connect(
            'key_release_event',
            self.__on_key_release
        )

        self.point_binded = True

    def __on_key_press(self, event):
        if event.key == 'shift':
            self.shift_is_held = True
        if event.key == 'control':
            self.ctrl_is_held = True

    def __on_key_release(self, event):
        self.shift_is_held = False
        self.ctrl_is_held = False

    def __point_event(self, event):
        """
        Action for adding point and split curve. Click LPM to add point.
        Click Alt + PPM to split curve.
        :param event:
        """
        if self.ctrl_is_held and event.button == consts.BUTTONS.get('PPM'):
            index = utils.check_index(
                event.xdata,
                self.active_curve.line.get_xdata()
            )
            self.bezier_split(self.active_curve.t_list[index])
        if event.button != consts.BUTTONS.get('LPM') or not self.active_curve:
            return

        index = self.active_point['id']
        if index is not None:
            index += 1

        self.active_curve.add_point(event, index)

    def __pick_point(self, event):
        """
        Action for picking point. Click PPM to pick point.
        :param event:
        """
        if event.artist != self.active_curve.help_line:
            return

        self.active_point['press'] = True
        self.active_point['id'] = event.ind[0]

        if self.shift_is_held:
            self.active_curve.remove_point(self.active_point['id'])

    def __move_point(self, event):
        """
        Action for moving point. Move mouse when click PPM on point.
        :param event:
        """
        is_ppm = event.button == consts.BUTTONS.get('PPM')
        if not (self.active_point['press'] and is_ppm):
            return

        data = {
            'x': event.xdata,
            'y': event.ydata
        }

        self.active_curve.edit_point(data, self.active_point['id'])
        self.canvas.draw()

    def __on_release(self, event):
        """
        Clear states and update plot when action released.
        :param event:
        """
        self.active_point['press'] = False
        self.active_point['id'] = None
        if self.active_curve:
            self.update_plot()

    def __handle_editing(self):
        self.active_curve.edit()

    def __curve_options(self):

        dialog = self.active_curve.options_class()

        if dialog.exec_():
            action = dialog.get_action()
            params = dialog.get_params()
            try:
                func = getattr(self, action)
            except AttributeError:
                pass
            else:
                func(**params)

    def __translate_curve(self):
        if not self.active_curve:
            return
        self.active_curve.translate()

    def __rotate_curve(self):
        if not self.active_curve:
            return
        self.active_curve.rotate()

    def transform_newton_to_bezier(self):
        if not self.active_curve.type == 'NEWTON':
            return

        yp = self.active_curve.transform_to_bezier()
        data = self.active_curve.data
        data['points'] = zip(self.active_curve.xp, yp)

        new_curve = CURVE_TYPES['BEZIER'](self)
        data = new_curve.load(data)
        self.__delete_curve()
        self.__add_curve(new_curve, data)

    def bezier_degree_elevation(self, number):
        self.active_curve.degree_elevation(number)

    def bezier_degree_reduction(self, number):
        self.active_curve.degree_reduction(number)

    def bezier_split(self, t):
        left, right = self.active_curve.split(t)
        name = self.active_curve.name
        c_type = self.active_curve.type
        self.__delete_curve()

        left_data = {
            'name': name + ' left',
            'points': left
        }
        c = CURVE_TYPES[c_type](self)
        self.__add_curve(c, left_data)

        right_data = {
            'name': name + ' right',
            'points': right
        }
        c = CURVE_TYPES[c_type](self)
        self.__add_curve(c, right_data)

    def add_toolbar(self):
        self.toolbar = widgets.CustomNavigationToolbar(
            self, self.canvas, self.draw_view
        )
        self.draw_layout.addWidget(self.toolbar)

    def get_curve_item(self):
        return self.curves_list.list.findItems(
            self.active_curve.name,
            QtCore.Qt.MatchFixedString
        )[-1]

    def __handle_add_curve(self, curve):
        """
        Handle add curve action.
        :param curve:
        """
        is_valid, data = curve.draw_curve_dialog(False)
        if is_valid:
            self.__add_curve(curve, data)

    def __add_curve(self, curve, data):
        """
        Add new curve to curves list and update draw.
        :param curve
        """
        created = curve.create(data)
        if not created:
            return

        if self.active_curve:
            self.unbind_point_actions()
            mp.artist.setp(self.active_curve.line, linewidth=1)
            self.__change_help_curve(curve)

        self.active_curve = curve
        self.figure.curves[curve.name] = curve

        mp.artist.setp(self.active_curve.line, linewidth=4)

        self.curves_list.list.addItem(self.active_curve.name)
        item = self.get_curve_item()
        self.curves_list.list.setCurrentItem(item)

        self.update_plot()

        self.__toggle_curve_menu(True)
        self.bind_point_actions()

    def __change_curve(self, item):
        """
        Update curve.
        :param item:
        """
        self.unbind_point_actions()
        name = item.text()
        self.__change_help_curve(self.figure.curves[name])
        mp.artist.setp(self.active_curve.line, linewidth=1)
        self.active_curve = self.figure.curves[name]
        mp.artist.setp(self.active_curve.line, linewidth=4)
        self.update_plot()

        self.__toggle_curve_menu(True)
        self.bind_point_actions()

    def __delete_curve(self):
        name = self.active_curve.name

        del self.figure.curves[name]
        self.active_curve.delete()

        row = self.curves_list.list.currentRow()
        self.curves_list.list.takeItem(row)
        item = self.curves_list.list.currentItem()
        if item:
            self.__change_curve(item)
        else:
            self.__toggle_curve_menu(False)
            self.__clear_curve_data()

    def __clone_curve(self):
        cloned, data = self.active_curve.clone()
        if cloned:
            new_curve = CURVE_TYPES[self.active_curve.type](self)
            self.__add_curve(new_curve, data)

    def __change_help_curve(self, new_curve):
        if self.active_curve.type != 'PARAM':
            self.active_curve.help_line.set_visible(False)
        new_curve.help_line.set_visible(True)

    def __clear_curve_data(self):
        self.curve_points.table.setRowCount(0)
        self.rational_curve_points.table.setRowCount(0)

    def __handle_add_figure(self):
        """
        Handle add figure action.
        """
        dialog = dialogs.FigureDialog()

        if dialog.exec_():
            data = dialog.get_data()
            name = data.get('name')
            if name:
                self.__add_figure(name)

    def __add_figure(self, name):
        """
        Create new figure and update draw
        """
        self.edit.menuAction().setVisible(True)

        self.__clear_figure_data()
        self.__clear_curve_data()

        self.figure = CustomFigure(self)
        self.figure.create(name)

    def __clear_figure_data(self):
        if self.figure:
            self.figure.clear()
            self.curves_list.list.clear()

    def __open_project(self):
        """
        Open file with project and draw on screen.
        Data format:
            {
                name: 'xyz',
                curves: [
                    {
                        data: {
                            name: 'cur1',
                            ...
                        },
                        type: 'PARAM',
                    },
                    {
                        data: {
                            name: 'cur2',
                            ...
                        },
                        type: 'BEZIER',
                    },
                ]
            }
        """
        dialog = dialogs.OpenFileDialog(self)
        filename = dialog.open_file()

        if filename:
            with open(filename) as infile:
                data = json.load(infile)
                infile.close()

            f_name = data.get('name')
            self.__add_figure(f_name)

            for curve in reversed(data.get('curves')):
                c_type = curve.get('type')

                c = CURVE_TYPES[c_type](self)
                c_data = c.load(curve.get('data'))
                self.__add_curve(c, c_data)

    def __save_project(self):
        """
        Save file as project.
        Data format:
            {
                name: 'xyz',
                curves: [
                    {
                        data: {
                            name: 'cur1',
                            ...
                        },
                        type: 'PARAM',
                    },
                    {
                        data: {
                            name: 'cur2',
                            ...
                        },
                        type: 'BEZIER',
                    },
                ]
            }
        """
        save_data = {
            'name': self.figure.name,
            'curves': [],
        }
        curves_list = []

        for curve in self.figure.curves.values():
            curves_list.append(curve.save())
        save_data['curves'] = curves_list

        dialog = dialogs.SaveFileDialog()
        filename, ext = dialog.save()
        with open(filename, 'w') as outfile:
            json.dump(save_data, outfile)
            outfile.close()

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

        dialog = dialogs.SaveFileDialog(default_path)
        filename, ext = dialog.save()

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
        Draw interpolate curve.
        """
        curve = CURVE_TYPES['NEWTON'](self)
        self.__handle_add_curve(curve)

    def __draw_parametric_curve(self):
        """
        Draw parametric curve.
        :return:
        """
        curve = CURVE_TYPES['PARAM'](self)
        self.__handle_add_curve(curve)

    def __draw_bezier_curve(self):
        """
        Draw bezier curve.
        """
        curve = CURVE_TYPES['BEZIER'](self)
        self.__handle_add_curve(curve)

    def __draw_rational_bezier_curve(self):
        """
        Draw rational bezier curve.
        """
        curve = CURVE_TYPES['RATIONAL_BEZIER'](self)
        self.__handle_add_curve(curve)

    def update_plot(self):
        """
        Update plot data.
        """
        self.__clear_curve_data()
        xp, yp = self.active_curve.help_line.get_data()
        weights = []
        if isinstance(self.active_curve, CURVE_TYPES['RATIONAL_BEZIER']):
            points_table = self.rational_curve_points
            weights = self.active_curve.weights
        else:
            points_table = self.curve_points

        for i in range(len(xp)):
            points_table.table.insertRow(i)
            points_table.table.setItem(
                i, 0, QtWidgets.QTableWidgetItem(str(xp[i]))
            )
            points_table.table.setItem(
                i, 1, QtWidgets.QTableWidgetItem(str(yp[i]))
            )
            if weights:
                points_table.table.setItem(
                    i, 2, QtWidgets.QTableWidgetItem(str(weights[i]))
                )

        self.canvas.draw()
