"""Database Tab

Typical usage example:

    mdb = mw.MaDatabases(my_screen)

"""

import sys
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc 
from PyQt6 import QtGui as qtg 
import GtapHelpers as helpers


class Databases(qtw.QWidget):
    """Tab displaying the current database and related information.

    All aggrigations start with a database.  The tab wil default to the last opened 
    GTAP database.  Tab displays version number, year, number of countries, regions, and sectors.
    The user has the option to choose another GTAP database.
    If another GTAP database is loaded, and is verified as valid, the display data are updated.

    Attributes:
        outputagg: TBD
        settings: saved organization and porgram name for registry info
        version_label0:  GTAP Directory
        version_label2:  GTAP Data Version
        version_label3:  Base year of data
        version_label4:  Release date
        version_label5:  Number of regions
        version_label6:  Number of sectors
        version_label7:  Number of endowments.
    """

    def __init__(self):
        super().__init__()
        self._outputagg=''
                
        horizontal_layout = qtw.QHBoxLayout()
        
        vertical_layout1 = qtw.QVBoxLayout()
        vertical_layout1.setContentsMargins(10, 20, 200, 11)
        
        info_form = qtw.QFormLayout()
        
        horizontal_layout.addLayout(vertical_layout1)
        horizontal_layout.addLayout(info_form)
         

        #left side buttons      
        self.setLayout(horizontal_layout) 
        choose_GTAP_button = qtw.QPushButton("Choose GTAP Database", clicked=self.getgtapdir)
               
        info_head = qtw.QLabel("<h1>Database Currently Selected:</h1>")
        self.version_label0 = LabelGtap("NA")
        self.version_label1 = qtw.QLabel('NA')
        self.version_label2 = qtw.QLabel('NA')
        self.version_label3 = qtw.QLabel('NA')
        self.version_label4 = qtw.QLabel('NA')
        self.version_label5 = qtw.QLabel('NA')
        self.version_label6 = qtw.QLabel('NA')
        self.version_label7 = qtw.QLabel('NA')
  
        vertical_layout1.addWidget(choose_GTAP_button)
        vertical_layout1.addWidget(qtw.QWidget())
        info_form.addRow(info_head)

        info_form.addRow("GTAP Directory", self.version_label0)
        #info_form.addRow("IESC Version", self.version_label1)
        info_form.addRow("GTAP Data Version", self.version_label2)
        info_form.addRow("Base Year of Data", self.version_label3)
        info_form.addRow("Release Date", self.version_label4)
        info_form.addRow("Number of Regions", self.version_label5)
        info_form.addRow("Number of Sectors", self.version_label6)
        info_form.addRow("Number of Endowments", self.version_label7)
        #Required for savings settings to registry
        qtc.QCoreApplication.setOrganizationName("ImpactECON")
        qtc.QCoreApplication.setOrganizationDomain("impactecon.com")
        qtc.QCoreApplication.setOrganizationName("PyGTAPAgg")

        self.settings=qtc.QSettings()
        

        #Check if directory is in registry
        if self.settings.contains('indir') and self.settings.value('indir') is not None :
           print('Inital Check setting dir :',self.settings.value('indir') )
           #print(self.settings.value('indir'))
           
           self.getdbinfo(self.settings.value('indir') )
 

    @property
    def outputagg(self):
        """TBD        """
        return self._outputagg
    
    @outputagg.setter
    def outputagg(self, x):
        self._outputagg=x

        
    def getgtapdir(self):
        """Gets current GTAP diractory.

        Get the current GTAP directory in the dialgoue box on the database page.

         Args:
            None

         Returns:            
              Void
        """
        directory = qtw.QFileDialog.getExistingDirectory()
        self.getdbinfo(directory)
        
        
    def getdbinfo(self, dir):
        """GTAP version information retieved from current direcotry and set in attributes.

        The version info is retrieved from the header and split into its components. Sets the attribure 
        variables varsion_label0-7. This routine varies for different verisons
        of the GTAP database as the format has changed and the data have been split into
        seperate headers in latter version. Runs every time a new directory with a GTAP
        directoy is set.

         Args:
            dir: GTAP data directory

         Returns:            
            The class attributes are set with the values contained in the GTAP database in the 
            current directory.
        """
        
        gtap_info=helpers.getdbversize(dir.replace('/','\\'), '\\gsddata.har')  #Can change here to work with flexagg, getdbverssize checks for valid database
        self.splitverinfo(gtap_info)

    def splitverinfo(self, gtap_info):
        """Sets the version attributes

        The version information is passed as a list, so it must be split into individual values.
        
           Args:
             gtap_info:  a list with version number, sectors, regions, endowments

           Returns:
              None (Sets the version information)

        
        """
        
        gtap, gtap_ver_info, gtap_num_reg, gtap_num_sect, gtap_num_endow =gtap_info
        gtap_version = gtap_ver_info
        
        self.version_label0.setText(str(gtap))
        self.version_label1.setText(gtap_version[0])
        self.version_label2.setText(gtap_version[0])
        self.version_label3.setText(gtap_version[1])
        self.version_label4.setText(gtap_version[2])
        self.version_label5.setText(str(gtap_num_reg))
        self.version_label6.setText(str(gtap_num_sect))
        self.version_label7.setText(str(gtap_num_endow))
        #label.setText(directory.replace('/','\\'))

class LabelGtap(qtw.QLabel):
    """Polymorh for Label class to include signals and emiters when set.
       
       When labels are changed in the database, such as the GTAP version
       The other tabs are updated to reflect the new regions, sectors
       and endowents.

        Attributes:
            gtap_source: PyQT Signal

        new_label=LabelGTAP()
    """
    gtap_source=qtc.pyqtSignal(str)

    def setText(self, text):
        """Set label text and emit change to slots.
           
        Overide to the standard PyQT setText method to include a signal.

            Args:
                text: text to put into the label

            Returns:
                None (text in label is set)

                
        """
        self.gtap_source.emit(text)
        super().setText(text)    
        
