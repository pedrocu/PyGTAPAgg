import sys
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc 
from PyQt6 import QtGui as qtg 
import GtapHelpers as helpers


class Databases(qtw.QWidget):
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
        return self._outputagg
    
    @outputagg.setter
    def outputagg(self, x):
        self._outputagg=x

        
    def getgtapdir(self):
        '''gets location of GTAP database and returns version info'''
        directory = qtw.QFileDialog.getExistingDirectory()
        self.getdbinfo(directory)
        

    def getdbinfo(self, dir):
        
        gtap_info=helpers.getdbversize(dir.replace('/','\\'), '\\basedata.har')  #Can change here to work with flexagg, getdbverssize checks for valid database
        self.splitverinfo(gtap_info)

    def splitverinfo(self, gtap_info):
        '''gets info from premake (input) data and unwraps and updates main version data screen'''
        
        gtap, gtap_ver_info, gtap_num_reg, gtap_num_sect, gtap_num_endow =gtap_info
        gtap_version = str(gtap_ver_info).split("_")
        
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
    gtap_source=qtc.pyqtSignal(str)

    def setText(self, text):
        self.gtap_source.emit(text)
        super().setText(text)    
        
