
#!python 3.8
"""Module creates the overall window

    mw = mw.MainWindow(my_screen)
    where: my_screen=app.primaryScreen().geometry()
"""
import sys


from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc 
from PyQt6 import QtGui as qtg

import DatabaseWidget as dbwidget
import selectwidget as slwidget
import DatabaseStore as store
import outputwidget as outwidget
import json


class MainWindow(qtw.QMainWindow):
    """The Driver for the main window including tabs and menu.

    A container for the tabs and top level menu.

    Attributes:
        menu_bar
        file_menu
        edit_menu
        help_menu
        open_action
        save_action
        quit_action
        about_action
        gtap_central_widget
    """

    def __init__(self, my_screen):
        super().__init__()
                              
        self.initilizeUI(my_screen)

    def initilizeUI(self, my_screen):
        """Sets up the main menu and the tabs.

        Instantiates menues.  Sets the window title.

         Args:
            my_screen:  parameters on screen size and adaptation

         Returns:            
              Void
        """
                
        # Main UI code goes here
        self.setWindowTitle('GTAP Aggregation Program')
            ##Adjust the mainscren to take up fixed percent of desktop
            #This helps with development
        
        #self.setFixedSize(my_screen.width(),my_screen.height())

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

        self.statusBar().showMessage('Welcome to PyGTAPAgg for GTAP')

        self.show()

    def showAboutDialog(self):
        """Shows the company, developer and contact information

        The About dialoque box is standard acroos software developers
        The version of the program, author and contact information is
        presented to the user when they select "about" in the main menu

         Args:
            None

         Returns:
             Void        
        """
        qtw.QMessageBox.about(self, "About PyGTAPAgg", """PyGTAPAgg Aggregates the GTAP Database
                              
                              Developed by Peter Minor, ImpactECON, LLC
                              https://impactecon.com
                              Developed in PyQt for Python""")
        
        
    def exitThisApp(self):
        """Exits ths app when called

        Exit the app when called. Clean up.

         Args:
            None

         Returns:
             Void
        """
        self.close()
        sys.exit()

    def saveFile(self):
        """Save the current app data and state.

        Brings up a dialogue to save to JSON file.
        Write to JSON is called from the data store where all data are stored.
        See datastore for to_JSON_file.

         Args:
            None

         Returns:
             Void

         Raises:
            IOError:  An Error occurred writing the smalltable.
        
        """
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
                 print('IO Error: did not work')

    def openFile(self):
        """Open a new aggrigation file.

        Dialogue to open a new JSON file with new aggrigation.
       
         Args:
            None

         Returns:
             Void

         Raises:
            IOError:  An Error occurred accessing the smalltable.
        
        """

        filename, _ = qtw.QFileDialog.getOpenFileName(self,
                                                       "Select the file to open...",
                                                       "c:\\",
                                                       'JSON Files (*.json);; All Files (*)')
        
        if filename:
              
                   self.gtap_central_widget.dataStore.load_new_agg_file(filename)




class GTAPAggTabs(qtw.QTabWidget):
    '''Subclass of tab widget customized for GTAPAgg app.
       
    This class is used for each of the tabs in the main window.
    Data structures and inputs vary depending on parameters.

    Attributes:
       None
    '''

    def __init__(self, *args, **kargs):
        super(GTAPAggTabs, self).__init__(*args, **kargs)  
        self.initilizeTabs()

    def initilizeTabs(self):
        """Data Store created. All tabs instantiated.

        The datastore, which is utilized by all tabs is created.
        All the tabs are created with the new datastore.
       
         Args:
            None

         Returns:
             Void

         
        
        """
        #setup parameters
        self.setMovable=True
        self.setTabPosition= qtw.QTabWidget.TabPosition.North
        self.setTabShape = qtw.QTabWidget.TabShape.Triangular
        self.setTabBarAutoHide = False
        
        #Initialize dataobject
        self.dataStore = store.DataStore()

        #Our Tabs
        self.databases=dbwidget.Databases()
        self.addTab(self.databases, 'Databases')
        self.sectors=slwidget.Select('Sectors', self.dataStore, self.dataStore.sectors.pick_start, self.dataStore.sectors.headers, self.dataStore.sectors.data)
        self.addTab(self.sectors, 'Sectors')
        self.regions=slwidget.Select('Regions', self.dataStore, self.dataStore.regions.pick_start, self.dataStore.regions.headers, self.dataStore.regions.data)
        self.addTab(self.regions, 'Regions')
        self.endowments=slwidget.EndowmentSelect('Endowments', self.dataStore, self.dataStore.endowments.pick_start, self.dataStore.endowments.headers, self.dataStore.endowments.data, self.dataStore.endowments.etrae)             
        self.addTab(self.endowments, 'Endowments')
        self.output=outwidget.Output(dataStore=self.dataStore)
        self.addTab(self.output, 'Output')


        #Connections
        self.databases.version_label0.gtap_source.connect(self.dataStore.gtapraw_source)
        self.databases.version_label0.gtap_source.connect(self.update_data_tabs)
        self.dataStore.update_tabs.connect(self.update_data_tabs)
    
    def update_picker(self):
        """When a tab changes the data in the picker pain, write it to the datastore.

        The database store maintains a picker element and this is maintained.
       
         Args:
            None

         Returns:
             Void
        
        """
        self.dataStore.sectors.pick_start=self.sectors._picker_model.stringList()
        self.dataStore.regions.pick_start=self.regions._picker_model.stringList()
        self.dataStore.endowments.pick_start=self.endowments._picker_model.stringList()
        
    def update_data_tabs(self):
        """When a new aggrigation is loaded, create new tabs.

        When a new aggrigation is opened, it is more efficient to create new tabs
        then to update the data.
       
         Args:
            None

         Returns:
             Void

         
        
        """
        self.removeTab(1)
        self.removeTab(1)
        self.removeTab(1)
        self.removeTab(1)
        self.sectors=slwidget.Select('Sectors', self.dataStore, self.dataStore.sectors.pick_start, self.dataStore.sectors.headers, self.dataStore.sectors.data)
        self.addTab(self.sectors, 'Sectors')
        self.regions=slwidget.Select('Regions', self.dataStore, self.dataStore.regions.pick_start, self.dataStore.regions.headers, self.dataStore.regions.data)
        self.addTab(self.regions, 'Regions')
        self.endowments=slwidget.EndowmentSelect('Endowments', self.dataStore, self.dataStore.endowments.pick_start, self.dataStore.endowments.headers, self.dataStore.endowments.data, self.dataStore.endowments.etrae)
        self.addTab(self.endowments, 'Endowments')
        self.output=outwidget.Output(dataStore=self.dataStore)
        self.addTab(self.output, 'Output')

            
                #self.tabBar().moveTab(0,1)
                #self.sectors.picker_model.setStringList(self.dataStore.sector_pick_start)
                #self.sectors.headers=self.dataStore.sector_header
                #self.sectors
                #self.sectors.model=slwidget.ItemTableModel("Sectors", self.dataStore.sector_header, self.dataStore.sector_all)
                #self.sectors.tableview.setModel(self.sectors.model)
                #self.sectors.updatedata()



                    

                

        

        

        
        
