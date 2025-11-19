import PyQt5.QtWidgets as QtWidgets
import sys


from ui import MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
