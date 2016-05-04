# -*- coding: utf-8 -*-

import numpy as np

import utils
import dialogs


class Curve(object):
    type = None
    dialog_class = None

    def __init__(self, ui):
        self.ui = ui
        self.name = None
        self.line = None
        self.help_line = None
        self.data = {}
        self.xp = []
        self.yp = []
        self.translation = [0, 0]
        self.rotation = 0

    def create(self, data):
        """
        Create curve.
        :param data:
        :return: created :type boolean
        """
        self.name = data.get('name')
        self.data = data
        fig = self.ui.figure
        ax = fig.add_subplot(111)

        try:
            x, y = self.get_plot_functions()
            self.line, = ax.plot(x, y, label=self.name)
            return True
        except:
            return False

    def edit(self):
        """
        Update curve.
        :return: edited :type boolean
        """
        is_valid, data = self.draw_curve_dialog(True)

        if is_valid:
            if data != self.data:
                self.name = data.get('name')
                self.data = data
                self.line.set_data(self.get_plot_functions())
                self.ui.update_plot()
                return True
            return False

        return False

    def get_plot_functions(self):
        """
        Get lists of points.
        :return: xp, yp :type list, list
        """
        pass

    def translate(self):
        """
        Translate list of curve points.
        """
        dialog = dialogs.TranslateDialog()

        if dialog.exec_():
            data = dialog.get_data()

            self.translation[0] += data.get('x')
            self.translation[1] += data.get('y')
            self.xp = map(lambda x: x + data.get('x'), self.xp)
            self.yp = map(lambda y: y + data.get('y'), self.yp)

            self.line.set_data(self.get_plot_functions())
            self.ui.update_plot()

    def rotate(self):
        """
        Rotate list of curve points.
        """
        dialog = dialogs.RotateDialog()

        if dialog.exec_():
            data = dialog.get_data()

            self.rotation += data
            self.rotation /= 360

            self.line.set_data(self.get_plot_functions())
            self.ui.update_plot()

    def draw_curve_dialog(self, edit):
        dialog = self.dialog_class()

        if edit:
            dialog.fill_data(self.data)

        if dialog.exec_():
            data = dialog.get_data()

            if dialog.validate():
                return True, data

        return False, {}

    def add_point(self, event, index=None):
        if event.inaxes != self.help_line.axes:
            return

        if index is not None:
            self.xp.insert(index, event.xdata)
            self.yp.insert(index, event.ydata)
        else:
            self.xp.append(event.xdata)
            self.yp.append(event.ydata)
        self.line.set_data(self.get_plot_functions())

    def edit_point(self, event, index):
        self.xp[index] = event.xdata
        self.yp[index] = event.ydata
        self.line.set_data(self.get_plot_functions())


class ParametricCurve(Curve):
    type = 'PARAM'
    dialog_class = dialogs.ParamDialog

    def create(self, data):
        created = super(ParametricCurve, self).create(data)
        if created:
            self.help_line = self.line

        return created

    def edit(self):
        edited = super(ParametricCurve, self).edit()
        if edited:
            self.help_line = self.line

        return edited

    def get_plot_functions(self):
        range_t = utils.parse_range(self.data.get('range'))

        t_min = range_t.get('min')
        t_max = range_t.get('max')
        t_interval = range_t.get('interval')

        function_x = utils.parse_curve_function(self.data.get('function_x'))
        function_y = utils.parse_curve_function(self.data.get('function_y'))

        xs = []
        ys = []
        for i in np.arange(t_min, t_max, t_interval):
            # this t is need for parametric curves
            t = float(i)
            x = eval(function_x) + self.translation[0]
            y = eval(function_y) + self.translation[1]

            xs.append(x)
            ys.append(y)

        return xs, ys


class InterpolateCurve(Curve):
    type = 'INTERPOLATE'
    dialog_class = dialogs.InterpolateDialog

    def create(self, data):
        fig = self.ui.figure
        ax = fig.add_subplot(111)
        self.xp = data.get('x_data', [])
        self.yp = data.get('y_data', [])
        self.help_line, = ax.plot(
            self.xp, self.yp, ls='--', c='#666666', marker='x', mew=2,
            mec='#204a87', picker=5, label=data.get('name') + ' help line'
        )
        created = super(InterpolateCurve, self).create(data)

        return created

    def get_plot_functions(self):
        self.help_line.set_data(self.xp, self.yp)

        return self.newton()

    @staticmethod
    def lagrange(points):
        def P(x):
            total = 0
            n = len(points)

            for i in xrange(n):
                xi, yi = points[i]

                def g(i, n):
                    tot_mul = 1
                    for j in xrange(n):
                        if i == j:
                            continue

                        xj, yj = points[j]
                        tot_mul *= (x - xj) / float(xi - xj)

                    return tot_mul

                total += yi * g(i, n)
            return total
        return P

    def newton(self):
        points = self.data.get('points')

        return [], []


class BezierCurve(Curve):
    type = 'BEZIER'
    pass
