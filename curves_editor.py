# -*- coding: utf-8 -*-
import os
import sys

import matplotlib as mp
import numpy as np
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas
)
from matplotlib.figure import Figure
from PIL import Image
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

Ui_MainWindow, QMainWindow = loadUiType("curves_editor_design.ui")


class CurvesEditor(QMainWindow, Ui_MainWindow):
    """
    Main class for curves editor
    """

    canvas = None
    current_figure = None
    figures = {}

    def __init__(self):
        super(CurvesEditor, self).__init__()
        self.setupUi(self)
        self.bind_actions()
        self.show()

    def bind_actions(self):
        """
        Bind functions to action buttons
        """
        self.action_new.triggered.connect(self.clear_all)
        self.action_open.triggered.connect(self.open_project)
        self.action_save.triggered.connect(self.save_project_file)
        self.action_save_as.triggered.connect(self.save_file)
        self.action_exit.triggered.connect(QtCore.QCoreApplication.quit)

        self.action_add_background.triggered.connect(self.open_image)
        self.action_interpolate.triggered.connect(self.draw_interpolate_curve)
        self.action_bezier.triggered.connect(self.draw_bezier_curve)

        self.figures_list.itemClicked.connect(self.change_fig)

    def change_fig(self, item):
        fig_name = item.text()
        self.current_figure = self.figures[fig_name]
        self.update_plot()

    def clear_all(self):
        """
        Clear all and create new file
        """
        self.current_figure = None
        self.figures = None
        self.remove_plot()
        self.figures_list.clear()

    def open_file(self):
        """
        Open file
        :return: filename
        """
        filename, ext = QtWidgets.QFileDialog.getOpenFileName(self, 'Otwórz plik')

        return filename

    def open_project(self):
        """
        Open file with project amd draw on screen
        """
        filename = self.open_file()

        if filename:
            f = open(filename, 'r')

            with f:
                data = f.read()

    def open_image(self):
        """
        Open file with image and draw as background
        """
        filename = self.open_file()
        img = Image.open(filename)
        ax = self.current_figure.axes[0]

        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        ax.imshow(img, extent=[x0, x1, y0, y1], aspect='auto')

        self.update_plot()

    @staticmethod
    def save_project_file():
        """
        Save file as project with special extension
        """
        file_name = 'test.txt'
        f = open(file_name, 'w')
        f.write('test')
        f.close()

    def save_file(self):
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

    def get_fig_name(self, title):
        text, ok = QtWidgets.QInputDialog.getText(
            self,
            title,
            'Podaj nazwę krzywej:'
        )

        if ok and len(text.strip()) == 0:
            ok = False
        return text, ok

    def draw_interpolate_curve(self):
        """
        Draw interpolate curve
        """
        fig_name, created = self.get_fig_name(
            'Parametryczna krzywa interpolacyjna'
        )

        if created:
            fig = Figure()
            ax = fig.add_subplot(111)
            ax.plot(np.random.rand(5))

            self.add_plot(fig, fig_name)

    def draw_bezier_curve(self):
        """
        Draw bezier curve
        """
        fig_name, created = self.get_fig_name('Krzywa beziera')

        if created:
            pass

    def add_plot(self, fig, fig_name):
        self.current_figure = fig
        self.figures[fig_name] = fig
        self.figures_list.addItem(fig_name)
        self.update_plot()

    def update_plot(self, ):
        if self.canvas:
            self.remove_plot()

        self.canvas = FigureCanvas(self.current_figure)
        self.draw_layout.addWidget(self.canvas)
        self.canvas.draw()

    def remove_plot(self):
        self.draw_layout.removeWidget(self.canvas)
        self.canvas.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = CurvesEditor()
    sys.exit(app.exec_())
