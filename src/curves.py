import numpy as np

from dialogs import (
    ParamDialog, TranslateDialog, RotateDialog, InterpolateDialog
)
from utils import Utils


class Curve(object):
    data = {}
    translation = [0, 0]
    rotation = 0

    def __init__(self, ui):
        self.ui = ui
        self.name = None
        self.line = None

    def edit(self):
        pass

    def create(self):
        pass

    def get_plot_functions(self):
        pass

    def translate(self):
        dialog = TranslateDialog()

        if dialog.exec_():
            data = dialog.get_data()

            self.translation[0] += data.get('x')
            self.translation[1] += data.get('y')

            self.line.set_data(self.get_plot_functions())
            self.ui.update_plot()

    def rotate(self):
        dialog = RotateDialog()

        if dialog.exec_():
            data = dialog.get_data()

            self.rotation += data
            self.rotation /= 360

            self.line.set_data(self.get_plot_functions())
            self.ui.update_plot()


class ParametricCurve(Curve):
    def create(self):
        dialog = ParamDialog()

        if dialog.exec_():
            data = dialog.get_data()

        if dialog.validate():
            self.name = data.get('name')
            data.pop('name')
            self.data = data

            fig = self.ui.figure
            ax = fig.add_subplot(111)

            try:
                x, y = self.get_plot_functions()
                self.line, = ax.plot(x, y)
            except:
                pass

    def edit(self):
        is_modified = (
            self.ui.curves_data.range_t.isModified() or
            self.ui.curves_data.function_x.isModified() or
            self.ui.curves_data.function_y.isModified()
        )

        if is_modified:
            data = self.ui.curves_data.get_data()
            if data != self.data:
                self.data = data
                self.line.set_data(self.get_plot_functions())
                self.ui.update_plot(self)

        self.ui.curves_data.range_t.setModified(False)
        self.ui.curves_data.function_x.setModified(False)
        self.ui.curves_data.function_y.setModified(False)

    def get_plot_functions(self):
        range_t = Utils.parse_range(self.data.get('range'))

        t_min = range_t.get('min')
        t_max = range_t.get('max')
        t_interval = range_t.get('interval')

        function_x = Utils.parse_curve_function(self.data.get('function_x'))
        function_y = Utils.parse_curve_function(self.data.get('function_y'))

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
    def draw(self):
        dialog = InterpolateDialog()

        if dialog.exec_():
            name, points = dialog.get_data()
            points = [(0, 0), (25, 30), (50, 10), (57, 0)]
            P = self.lagrange(points)

            data = {
                'name': name,
                'points': points,
                'f': P
            }

            self.data = points
            self.create(data)
            self.ui.add_plot(data)

    def create(self):
        fig = Figure()
        self.figure = fig
        ax = fig.add_subplot(111)

        f = data.get('f')
        name = data.get('name')
        points = data.get('points')
        x = range(-10, 100)
        y = map(f, x)

        self.ui.line, = ax.plot(x, y)

        # x_list = []
        # y_list = []
        # for x, y in points:
        #     x_list.append(x)
        #     y_list.append(y)
        #
        # ax2.plot(x_list, y_list, 'ro')

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


class BezierCurve(Curve):
    pass
