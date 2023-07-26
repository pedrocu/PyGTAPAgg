
#!python 3.8

import sys


from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc 
from PyQt6 import QtGui as qtg

import DatabaseWidget as dbwidget
import selectwidget as slwidget
import DatabaseStore as store
import json


class MainWindow(qtw.QMainWindow):
    def __init__(self, my_screen):
        super().__init__()
                              
        self.initilizeUI(my_screen)

    def initilizeUI(self, my_screen):
                
        # Main UI code goes here
        self.setWindowTitle('GTAP Aggregation Program')
            ##Adjust the mainscren to take up fixed percent of desktop
        
        self.setFixedSize(my_screen.width()*.7,my_screen.height()*.7)

        ##Main Menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')
        help_menu = menubar.addMenu('Help')

        #File Menu
        open_action = file_menu.addAction('Open', self.openFile)
        save_action = file_menu.addAction('Save', self.saveFile)
        save_action = file_menu.addAction('Save As', self.saveFile)
        quit_action = file_menu.addAction('Quit', self.exitThisApp)

        #Help Menu
        about_action = help_menu.addAction('About', self.showAboutDialog)

        ##Central Window
        self.gtap_central_widget = GTAPAggTabs()
        self.setCentralWidget(self.gtap_central_widget)

        self.statusBar().showMessage('Welcome to PyQtAgg for GTAP')

        self.show()

    def showAboutDialog(self):
        qtw.QMessageBox.about(self, "About PyQt GTAPAgg", """PyQtAgg Aggregates the GTAP Database
                              
                              Developed by Peter Minor, ImpactECON, LLC
                              https://impactecon.com
                              Developed in PyQt for Python""")
        
    def exitThisApp(self):
         self.close()
         sys.exit()

    def saveFile(self):
        self.gtap_central_widget.update_picker()
        filename, _ = qtw.QFileDialog.getSaveFileName(self,
                                                       "Select the file to save to...",
                                                       "c:\\",
                                                       'JSON Files (*.json);; All Files (*)')
        
        if filename:
            try:

                self.gtap_central_widget.dataStore.to_json_file(filename)

            except Exception as e:
                 #TBD this should be a valid exception
                 print('did not work')

    def openFile(self):
         filename, _ = qtw.QFileDialog.getOpenFileName(self,
                                                       "Select the file to open...",
                                                       "c:\\",
                                                       'JSON Files (*.json);; All Files (*)')
        
         if filename:
              
                   self.gtap_central_widget.dataStore.load_new_agg_file(filename)




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
        
        #Initialize dataobject
        #print(self.databases.version_label0.text() )
        self.dataStore = store.DataStore()

        #Our Tabs
        self.databases=dbwidget.Databases()
        self.addTab(self.databases, 'Databases')
        


        self.sectors=slwidget.Select('Sectors', self.dataStore, self.dataStore.sectors.pick_start, self.dataStore.sectors.headers, self.dataStore.sectors.data)
        self.addTab(self.sectors, 'Sectors')
        self.regions=slwidget.Select('Regions', self.dataStore, self.dataStore.regions.pick_start, self.dataStore.regions.headers, self.dataStore.regions.data)
        self.addTab(self.regions, 'Regions')
        self.endowments=slwidget.EndowmentSelect('Endowments', self.dataStore, self.dataStore.endowments.pick_start, self.dataStore.endowments.headers, self.dataStore.endowments.data)
        self.addTab(self.endowments, 'Endowments')


        #headers=['pos', 'GTAP Code', 'GTAP Name', 'Long Description' ,'Sort Group']
        
        #pick_start = ['Agriculture', 'Manufactures', 'Extractive','Services']

        #Connections
        self.databases.version_label0.gtap_source.connect(self.dataStore.gtapraw_source)
        self.databases.version_label0.gtap_source.connect(self.update_data_tabs)
        self.dataStore.update_tabs.connect(self.update_data_tabs)
    
    def update_picker(self):
         self.dataStore.sectors.pick_start=self.sectors._picker_model.stringList()
         self.dataStore.regions.pick_start=self.regions._picker_model.stringList()
         self.dataStore.endowments.pick_start=self.endowments._picker_model.stringList()
        
    def update_data_tabs(self):
                self.removeTab(1)
                self.removeTab(1)
                self.removeTab(1)
                self.sectors=slwidget.Select('Sectors', self.dataStore, self.dataStore.sectors.pick_start, self.dataStore.sectors.headers, self.dataStore.sectors.data)
                self.addTab(self.sectors, 'Sectors')
                self.regions=slwidget.Select('Regions', self.dataStore, self.dataStore.regions.pick_start, self.dataStore.regions.headers, self.dataStore.regions.data)
                self.addTab(self.regions, 'Regions')
                self.endowments=slwidget.EndowmentSelect('Endowments', self.dataStore, self.dataStore.endowments.pick_start, self.dataStore.endowments.headers, self.dataStore.endowments.data)
                self.addTab(self.endowments, 'Endowments')
                #self.tabBar().moveTab(0,1)
                #self.sectors.picker_model.setStringList(self.dataStore.sector_pick_start)
                #self.sectors.headers=self.dataStore.sector_header
                #self.sectors
                #self.sectors.model=slwidget.ItemTableModel("Sectors", self.dataStore.sector_header, self.dataStore.sector_all)
                #self.sectors.tableview.setModel(self.sectors.model)
                #self.sectors.updatedata()



                    

                

        

        

        
        
