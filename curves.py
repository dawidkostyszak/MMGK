from matplotlib.figure import Figure
import numpy as np

from custom_widgets import ParamDialog
from utils import Utils


class Curve(object):
    figure = None
    data = {}

    def __init__(self, ui):
        self.ui = ui

    def edit(self):
        pass


class InterpolateCurve(Curve):
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

    @staticmethod
    def get_plot_functions(data):
        range_t = Utils.parse_range(data.get('range'))

        t_min = range_t.get('min')
        t_max = range_t.get('max')
        t_interval = range_t.get('interval')

        function_x = Utils.parse_curve_function(data.get('function_x'))
        function_y = Utils.parse_curve_function(data.get('function_y'))

        x = [
            eval(function_x) for t in [
                float(i)
                for i in np.arange(t_min, t_max, t_interval)
            ]
        ]
        y = [
            eval(function_y) for t in [
                float(i)
                for i in np.arange(t_min, t_max, t_interval)
            ]
        ]

        return x, y

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
