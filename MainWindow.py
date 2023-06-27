
#!python 3.8

import sys


from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc 
from PyQt6 import QtGui as qtg

import DatabaseWidget as dbwidget
import selectwidget as slwidget


class MainWindow(qtw.QMainWindow):
    def __init__(self, my_screen):
        super().__init__()
        self.initilizeUI(my_screen)

    def initilizeUI(self, my_screen):
                
        # Main UI code goes here
        self.setWindowTitle('GTAP Aggregation Program')
            ##Adjust the mainscren to take up fixed percent of desktop
        
        self.setFixedSize(my_screen.width()*.5,my_screen.height()*.5)

        ##Main Menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')
        help_menu = menubar.addMenu('Help')

        ##Central Window
        self.iesc_central_widget = GTAPAggTabs()
        self.setCentralWidget(self.iesc_central_widget)

    


        

        self.show()


class GTAPAggTabs(qtw.QTabWidget):
    '''subclass of tab widget customized for GTAPAgg app'''

    def __init__(self, *args, **kargs):
        super(GTAPAggTabs, self).__init__(*args, **kargs)

        self.initilizeTabs()

    def initilizeTabs(self):

        #setup parameters
        self.setMovable=True
        self.setTabPosition= qtw.QTabWidget.TabPosition.North
        self.setTabShape = qtw.QTabWidget.TabShape.Triangular
        self.setTabBarAutoHide = False
        
        
        
        
        #Our Tabs
        self.databases=dbwidget.Databases()
        self.addTab(self.databases, 'Databases')

        headers=['pos', 'GTAP Code', 'GTAP Name', 'Long Description' ,'Sort Group']
        pick_start = ['Agriculture', 'Manufactures', 'Extractive','Services']
        self.sectors=slwidget.Select('Sectors', headers, pick_start)
        self.addTab(self.sectors, 'Sectors')



