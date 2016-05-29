# -*- coding: utf-8 -*-

from math import floor
import numpy as np

import utils
import dialogs


class Curve(object):
    type = None
    dialog_class = None
    options_class = None

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
                if self.name != data.get('name'):
                    item = self.ui.get_curve_item()
                    self.name = data.get('name')
                    item.setText(self.name)

                self.data = data
                self.update()
                return True
            return False

        return False

    def update(self):
        self.line.set_data(self.get_plot_functions())
        self.ui.update_plot()

    def clone(self):
        """
        Clone curve.
        :return: cloned :type boolean
        """
        curve_data = dict(self.data)
        is_valid, data = self.draw_curve_dialog(True)

        curve_data['name'] = data.get('name')
        if self.xp:
            curve_data['x_data'] = self.xp
        if self.yp:
            curve_data['y_data'] = self.yp

        return is_valid, curve_data

    def delete(self):
        self.line.remove()
        self.help_line.remove()
        self.ui.canvas.draw()

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

    def edit_point(self, data, index):
        if data.get('x'):
            self.xp[index] = data.get('x')
        if data.get('y'):
            self.yp[index] = data.get('y')
        self.line.set_data(self.get_plot_functions())

    def remove_point(self, index):
        del self.xp[index]
        del self.yp[index]
        self.line.set_data(self.get_plot_functions())


class CurveWithHelpLine(Curve):
    def create(self, data):
        fig = self.ui.figure
        ax = fig.add_subplot(111)
        self.xp = data.get('x_data', [])
        self.yp = data.get('y_data', [])
        self.help_line, = ax.plot(
            self.xp, self.yp, ls='--', c='#666666', marker='x', mew=2,
            mec='#204a87', picker=5, label=data.get('name') + ' help line'
        )
        created = super(CurveWithHelpLine, self).create(data)

        return created


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


class NewtonCurve(CurveWithHelpLine):
    type = 'NEWTON'
    dialog_class = dialogs.CurveNameDialog
    options_class = dialogs.NewtonOptionsDialog

    def get_plot_functions(self, num=200):
        self.help_line.set_data(self.xp, self.yp)

        xs, ys = [], []

        if len(self.xp) >= 2:
            xs = np.linspace(self.xp[0], self.xp[-1], num)
            ys = [self.newton(self.coef(), x) for x in xs]

        return xs, ys

    def coef(self):
        """
        Calculate coefficients
        :return: an array of coefficient
        """
        n = len(self.xp)
        b = np.array(self.yp)

        for i in range(1, n):
            for k in range(n-1, i-1, -1):
                b[k] = (b[k] - b[k-1])/(self.xp[k] - self.xp[k-i])

        return b

    def newton(self, b, x):
        """
        Calculate newton polynomial
        :param b: array returned by function coef()
        :param x: the node to interpolate at
        :return: the y_value interpolation
        """
        n = len(b) - 1
        temp = b[n]
        for k in range(n - 1, -1, -1):
            temp = temp * (x - self.xp[k]) + b[k]
        return temp

    def transform_to_bezier(self):
        n = len(self.xp) - 1
        if n < 1:
            return []

        b = self.coef()
        c = np.zeros(n+1)
        c[n] = b[n]

        for k in range(n-1, -1, -1):
            t = 1 - self.xp[k]
            for i in range(k, n):
                c[i] = (t * (i-k) * c[i] - self.xp[k] * (n-i) * c[i+1]) / (n-k) + b[k]
        return list(c)


class BezierCurve(CurveWithHelpLine):
    type = 'BEZIER'
    dialog_class = dialogs.CurveNameDialog
    options_class = dialogs.BezierOptionsDialog

    def get_plot_functions(self):
        self.help_line.set_data(self.xp, self.yp)

        xs, ys = [], []

        if len(self.xp) >= 2:
            xs, ys = self.bezier(list(zip(self.xp, self.yp))).T
        return xs, ys

    @staticmethod
    def bezier(points, num=200):
        """
        Build Bezier curve from points.
        """
        def _casteljau(x):
            n = len(points)
            W = np.zeros((n, n, 2))

            for i in range(n):
                W[0][i] = points[i]

            for i in range(1, n):
                for k in range(0, n-i):
                    W[i][k] = (1 - x) * W[i-1][k] + x * W[i-1][k+1]
            return W[n-1][0]

        t = np.linspace(0, 1, num=num)

        curve = map(_casteljau, t)
        return np.array(curve)

    def degree_elevation(self):
        """
        Q[i] = i/n+1 * P[i-1] + (1 - i/n+1) * P[i] 1<=i<=n
        """
        P = np.array(zip(self.xp, self.yp))  # control points
        n = len(P)

        Q = np.zeros((n+1, 2))  # new control points
        Q[0] = P[0]
        Q[n] = P[n-1]
        for i in range(1, n):
            Q[i] = (i / float(n+1)) * P[i-1] + (1 - i / float(n+1)) * P[i]

        xp, yp = Q.T
        self.xp, self.yp = list(xp), list(yp)
        self.update()

    def degree_reduction(self):
        P = np.array(zip(self.xp, self.yp))  # control points

        n = len(P)
        half = int(floor(n/2))

        Q = np.zeros((n, 2))  # new control points
        W = np.zeros((n-1, 2))  # calculate from first to floor(n/2)
        Z = np.zeros((n, 2))  # calculate from last to floor(n/2) + 1

        Q[0] = P[0]
        for i in range(1, n):
            Q[i] = (i/n) * P[i-1] + (1 - i/n) * P[i]

        W[0] = Q[0]
        for i in range(1, half):
            W[i] = (n * Q[i] - i * W[i-1]) / (n - i)

        Z[n-1] = Q[n-1]
        for i in range(n-1, half, -1):
            Z[i-1] = (n * Q[i] - (n - i) * Z[i]) / i

        xp, yp = np.array(list(W[:half]) + list(Z[half:n-1])).T
        self.xp, self.yp = list(xp), list(yp)
        self.update()


class RationalBezierCurve(CurveWithHelpLine):
    type = 'RATIONAL_BEZIER'
    dialog_class = dialogs.CurveNameDialog
    default_weight = 1.0

    def __init__(self, ui):
        super(RationalBezierCurve, self).__init__(ui)
        self.weights = []

    def add_point(self, event, index=None):
        if index is not None:
            self.weights.insert(index, self.default_weight)
        else:
            self.weights.append(self.default_weight)
        super(RationalBezierCurve, self).add_point(event, index)

    def edit_point(self, data, index):
        if data.get('w'):
            self.weights[index] = data.get('w')
        super(RationalBezierCurve, self).edit_point(data, index)

    def get_plot_functions(self):
        self.help_line.set_data(self.xp, self.yp)

        xs, ys = [], []

        if len(self.xp) >= 2:
            xs, ys = self.rational_bezier(list(zip(self.xp, self.yp))).T
        return xs, ys

    def rational_bezier(self, points, num=200):
        """
        Build Rational Bezier curve from points.
        """
        wp = self.weights
        points = np.array(points)

        def _casteljau(x):
            n = len(points)
            W = np.zeros((n, n, 2))

            for i in range(n):
                W[0][i] = wp[i] * points[i]

            for i in range(1, n):
                for k in range(0, n-i):
                    W[i][k] = (1 - x) * W[i-1][k] + x * W[i-1][k+1]
            return W[n-1][0]

        t = np.linspace(0, 1, num=num)

        curve = map(_casteljau, t)
        return np.array(curve)
