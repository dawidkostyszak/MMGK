from matplotlib.figure import Figure
import numpy as np

from custom_widgets import ParamDialog, TranslateDialog, RotateDialog
from utils import Utils


class Curve(object):
    figure = None
    data = {}
    translation = [0, 0]
    rotation = 0

    def __init__(self, ui):
        self.ui = ui

    def edit(self):
        pass

    def create(self):
        pass

    def get_plot_functions(self, data):
        pass

    def translate(self):
        dialog = TranslateDialog()

        if dialog.exec_():
            data = dialog.get_data()

            self.translation[0] += data.get('x')
            self.translation[1] += data.get('y')

            line = self.figure.axes[0].lines[0]
            line.set_data(self.get_plot_functions(self.data))
            self.ui.update_plot()

    def rotate(self):
        dialog = RotateDialog()

        if dialog.exec_():
            data = dialog.get_data()

            self.rotation += data
            self.rotation /= 360

            line = self.figure.axes[0].lines[0]
            line.set_data(self.get_plot_functions(self.data))
            self.ui.update_plot()


class ParametricCurve(Curve):
    def draw(self):
        dialog = ParamDialog()
        data = None

        if dialog.exec_():
            data = dialog.get_data()

        if dialog.validate():
            before = data.items()
            before.remove(('name', data.get('name')))
            self.data = dict(before)
            self.create(data)
            self.ui.add_plot(data)

    def get_plot_functions(self, data):
        range_t = Utils.parse_range(data.get('range'))

        t_min = range_t.get('min')
        t_max = range_t.get('max')
        t_interval = range_t.get('interval')

        function_x = Utils.parse_curve_function(data.get('function_x'))
        function_y = Utils.parse_curve_function(data.get('function_y'))

        xs = []
        ys = []
        for i in np.arange(t_min, t_max, t_interval):
            t = float(i)
            x = eval(function_x) + self.translation[0]
            y = eval(function_y) + self.translation[1]
            rot_x = x * np.cos(self.rotation) - y * np.sin(self.rotation)
            rot_y = x * np.sin(self.rotation) + y * np.cos(self.rotation)

            xs.append(rot_x)
            ys.append(y)

        return xs, ys

    def create(self, data):
        fig = Figure()
        ax = fig.add_subplot(111)

        try:
            x, y = self.get_plot_functions(data)
            self.ui.line, = ax.plot(x, y)
            self.figure = fig
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
                # self.create(data)
                line = self.figure.axes[0].lines[0]
                line.set_data(self.get_plot_functions(data))
                self.ui.update_plot()

        self.ui.curves_data.range_t.setModified(False)
        self.ui.curves_data.function_x.setModified(False)
        self.ui.curves_data.function_y.setModified(False)
