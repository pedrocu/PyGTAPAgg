
#!python 3.8

import sys


from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc 
from PyQt6 import QtGui as qtg

import DatabaseWidget as dbwidget
import selectwidget as slwidget
import json
from harpy import *


class DataStore():
    def __init__(self, gtap_source=None, agg_store_file="defaults.json"):
        self.gtap_source=gtap_source
        self.agg_store_file= agg_store_file
        self.agg_store_data=self.load_aggstore(self.agg_store_file)
        self.sector_all = self.make_sector_all(self.gtap_sets, self.agg_store_data)
        self.sector_pick_start = self.make_sector_pickstart(self.agg_store_data)
        self.sector_headers = self.make_sector_headers(self.agg_store_data)[0:4]
        print(self.sector_headers)

    @property
    def gtap_source(self):
        #In practive, this should only be setby the database widget for validity checking
        return self._gtap_source
    
    @gtap_source.setter
    def gtap_source(self, value):
        self._gtap_source=value
        if value != None :
            self.load_gtap_sets(value)
   
    @property
    def agg_store_file(self):
        return self._agg_store_file
    
    @agg_store_file.setter
    def agg_store_file(self, value):
        self._agg_store_file=value

    @property
    def agg_store_data(self):
        return self._agg_store_data

    @agg_store_data.setter
    def agg_store_data(self, value):
        self._agg_store_data=value

    @property
    def gtap_sets(self):
        return self._gtap_sets

    @gtap_sets.setter
    def gtap_sets(self, value):
        self._gtap_sets=value
  
    def load_default(self, mydefaults):
        with open(mydefaults + '.json') as f:
            data=json.load(f)
        self.aggs = data
       
     #slot
    def gtapraw_source(self, value):
        value.replace('/','\\')
        
        self.gtap_source=value

    def load_gtap_sets(self, directory):
        InFile=HarFileObj(directory+"\\sets.har")
        DataHead=InFile["H2"]
        npDataArray = [x.strip(' ') for x in DataHead.array.tolist()]  #Need to strip out spaces - HARPY needs fix
        newlist = []
        for pos, value in enumerate(npDataArray):
            newlist.append([pos+1, value])
        
        self.gtap_sets = newlist
    
    def load_aggstore(self, file_name):
        
        with open(file_name) as f:
           aggstore=json.load(f)
           return aggstore
        
    def make_sector_all(self, sets, agg_store):
        '''takes sets and aggstore and does a match merge on sect abrev'''
        newdict={x[1]: x for x in agg_store['sectors']['allsect']}
        matchlist =  [x+newdict.get(x[1], ['','', '','',''])[2:] for x in sets ]
        return matchlist
    
    def make_sector_pickstart(self, agg_store):
        return agg_store['sectors']['picks']
    
    def make_sector_headers(self, agg_store):
        return agg_store['sectors']['headers']




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

        
        #Initialize dataobject
        if self.databases.version_label0.text() != 'N\A':
            self.dataStore = DataStore(self.databases.version_label0.text())
        else:
            self.dataStore = DataStore(None, 'defaults')

        #headers=['pos', 'GTAP Code', 'GTAP Name', 'Long Description' ,'Sort Group']
        
        #pick_start = ['Agriculture', 'Manufactures', 'Extractive','Services']
        
        self.sectors=slwidget.Select('Sectors', self.dataStore)
        self.addTab(self.sectors, 'Sectors')
        

        #Connection

        self.databases.version_label0.gtap_source.connect(self.dataStore.gtapraw_source)
        
