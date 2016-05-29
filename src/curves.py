# -*- coding: utf-8 -*-

import numpy as np

import utils
import dialogs

from scipy.special import binom


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
                self.line.set_data(self.get_plot_functions())
                self.ui.update_plot()
                return True
            return False

        return False

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

    def edit_point(self, event, index):
        self.xp[index] = event.xdata
        self.yp[index] = event.ydata
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


class RationalBezierCurve(CurveWithHelpLine):
    type = 'RATIONAL_BEZIER'
    dialog_class = dialogs.CurveNameDialog

    def __init__(self, ui):
        super(RationalBezierCurve, self).__init__(ui)
        self.wp = []

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

        n = len(points)
        t = np.linspace(0, 1, num=num)
        curve = np.zeros((num, 2))
        temp = np.zeros((num, 2))
        self.wp = [(1, 1) for i in range(num)]

        for ii in range(n):
            temp += np.outer(
                self.bernstein(n - 1, ii)(t),
                points[ii][0]
            )

        for ii in range(n):
            curve += np.outer(
                self.bernstein(n - 1, ii)(t),
                (self.wp[ii][0]*points[ii][0], self.wp[ii][1]*points[ii][1])
            )
            # curve += np.outer(
            #     self.bernstein(n - 1, ii)(t),
            #     map(lambda x: self.wp[ii]*x, points[ii])
            # ) / np.outer(self.bernstein(n - 1, ii)(t), self.wp)
        for ii in range(n):
            curve /= np.outer(self.bernstein(n - 1, ii)(t), self.wp[ii])

        return curve

    def bernstein(self, n, k):
        """
        Bernstein polynomial.
        """

        coeff = binom(n, k)  # Newton symbol

        def _bpoly(x):
            return coeff * x ** k * (1 - x) ** (n - k)  # (n i)t^i(1-t)^n-i

        return _bpoly