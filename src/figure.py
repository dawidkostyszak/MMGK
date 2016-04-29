# -*- coding: utf-8 -*-

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas
)
from matplotlib.figure import Figure


class CustomFigure(Figure):
    curves = {}
    curve = None

    def __init__(self, ui, *args, **kwargs):
        super(CustomFigure, self).__init__(*args, **kwargs)
        self.ui = ui

    def create(self, name):
        ax = self.add_subplot(111)
        ax.set_title(name)
        self.draw_figure()

    def draw_figure(self):
        self.clear()
        self.ui.canvas = FigureCanvas(self)
        self.ui.draw_layout.addWidget(self.ui.canvas)
        self.ui.canvas.draw()
        self.ui.add_toolbar()

    def clear(self):
        if self.canvas:
            self.ui.draw_layout.removeWidget(self.ui.canvas)
            self.ui.draw_layout.removeWidget(self.ui.toolbar)
            self.canvas.close()
