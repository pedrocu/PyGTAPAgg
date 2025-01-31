#!python 3.8


from PyQt6 import QtWidgets as qtw
from PyGTAPAgg import MainWindow as mw 
import sys
from PyGTAPAgg import MainWindow as mw


if __name__ == '__main__':
    

    app = qtw.QApplication(sys.argv)

    #Get screen size and pass it to mainwindow
    my_screen=app.primaryScreen().geometry()


# it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.
    mw = mw.MainWindow(my_screen)

    sys.exit(app.exec())

    

