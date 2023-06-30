
#!python 3.8

import sys


from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc 
from PyQt6 import QtGui as qtg

import DatabaseWidget as dbwidget
import selectwidget as slwidget
import json


class DataStore():
    def __init__(self, gtap_source=None, agg_store='defaults'):
        self.gtap_source=gtap_source
        self.agg_store = agg_store
    
    @property
    def gtap_source(self):
        #In practive, this should only be setby the database widget for validity checking
        return self._gtap_source
    
    @gtap_source.setter
    def gtap_source(self, value):
        self._gtap_source=value
        if value != None :
            

    @property
    def agg_store(self):
        return self._gtap_loc
    
    @agg_store.setter
    def agg_store(self, value):
        self._gtap_loc=value

    @property
    def aggs(self):
        return self._aggs
    
    @aggs.setter
    def aggs(self, value):
       self._aggs = value

    def load_default(self, mydefaults):
        with open(mydefaults + '.json') as f:
            data=json.load(f)
        self.aggs = data
       

     #slot
    def gtapraw_source(self, value):
        value.replace('/','\\')
        self.gtap_source=value
    




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

        if self.databases.version_label0.text() != 'N\A':
            self.dataStore = DataStore(self.databases.version_label0.text(), 'defaults')
        else:
            self.dataStore = DataStore(None, 'defaults')
        

        #Connection

        self.databases.version_label0.gtap_source.connect(self.dataStore.gtapraw_source)
        
