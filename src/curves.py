# -*- coding: utf-8 -*-

import numpy as np

import utils
import dialogs


class Curve(object):
    dialog_class = None

    def __init__(self, ui):
        self.ui = ui
        self.name = None
        self.line = None
        self.data = {}
        self.translation = [0, 0]
        self.rotation = 0

    def create(self):
        is_valid, data = self.draw_curve_dialog(False)
        if is_valid:
            self.name = data.get('name')
            self.data = data
            fig = self.ui.figure
            ax = fig.add_subplot(111)

            try:
                x, y = self.get_plot_functions()
                self.line, = ax.plot(x, y)
                return True
            except:
                return False

        return False

    def edit(self):
        is_valid, data = self.draw_curve_dialog(True)

        if is_valid:
            if data != self.data:
                self.name = data.get('name')
                self.data = data
                self.line.set_data(self.get_plot_functions())
                self.ui.update_plot()

    def get_plot_functions(self):
        pass

    def translate(self):
        dialog = dialogs.TranslateDialog()

        if dialog.exec_():
            data = dialog.get_data()

            self.translation[0] += data.get('x')
            self.translation[1] += data.get('y')

            self.line.set_data(self.get_plot_functions())
            self.ui.update_plot()

    def rotate(self):
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


class ParametricCurve(Curve):
    dialog_class = dialogs.ParamDialog

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
    dialog_class = dialogs.InterpolateDialog

    def get_plot_functions(self):
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
    pass
