import sys

from PyQt5 import QtWidgets

from src.curves_editor import CurvesEditor

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    CurvesEditor()
sys.exit(app.exec_())
