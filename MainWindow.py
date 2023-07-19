
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
        
        self.setFixedSize(my_screen.width()*.5,my_screen.height()*.5)

        ##Main Menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')
        help_menu = menubar.addMenu('Help')

        #File Menu
        open_action = file_menu.addAction('Open')
        save_action = file_menu.addAction('Save')
        save_action = file_menu.addAction('Save As', self.saveFile)
        quit_action = file_menu.addAction('Quit', self.exitThisApp)

        #Help Menu
        about_action = help_menu.addAction('About', self.showAboutDialog)

        ##Central Window
        self.iesc_central_widget = GTAPAggTabs()
        self.setCentralWidget(self.iesc_central_widget)

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
        self.iesc_central_widget.update_picker()
        filename, _ = qtw.QFileDialog.getSaveFileName(self,
                                                       "Select the file to save to...",
                                                       "c:\\",
                                                       'JSON Files (*.json);; All Files (*)')
        
        if filename:
            try:

                self.iesc_central_widget.dataStore.to_json_file(filename)

            except Exception as e:
                 print('did not work')



    


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
        print("here is the source", self.dataStore.gtap_source)


        self.sectors=slwidget.Select('Sectors', self.dataStore, self.dataStore._sector_pick_start, self.dataStore._sector_header, self.dataStore._sector_all)
        self.addTab(self.sectors, 'Sectors')

        #headers=['pos', 'GTAP Code', 'GTAP Name', 'Long Description' ,'Sort Group']
        
        #pick_start = ['Agriculture', 'Manufactures', 'Extractive','Services']

        #Connections
        self.databases.version_label0.gtap_source.connect(self.dataStore.gtapraw_source)
        self.databases.version_label0.gtap_source.connect(self.update_data_tabs)
    
    def update_picker(self):
         self.dataStore.sector_pick_start=self.sectors._picker_model.stringList()
        
    def update_data_tabs(self):
                self.sectors=slwidget.Select('Sectors', self.dataStore, self.dataStore._sector_pick_start, self.dataStore._sector_header, self.dataStore._sector_all)
                self.removeTab(1)
                self.addTab(self.sectors, 'Sectors')
                #self.tabBar().moveTab(0,1)
                #self.sectors.picker_model.setStringList(self.dataStore.sector_pick_start)
                #self.sectors.headers=self.dataStore.sector_header
                #self.sectors
                #self.sectors.model=slwidget.ItemTableModel("Sectors", self.dataStore.sector_header, self.dataStore.sector_all)
                #self.sectors.tableview.setModel(self.sectors.model)
                #self.sectors.updatedata()



                    

                

        

        

        
        
