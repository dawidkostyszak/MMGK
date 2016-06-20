import sys
import argparse

from PyQt5 import QtWidgets

from src.curves_editor import CurvesEditor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--interface",
        nargs=1,
        choices=["unity", "gnome"],
        help="interface of your system, default=unity",
        default="unity"
    )

    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    CurvesEditor(args.interface[0])
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
