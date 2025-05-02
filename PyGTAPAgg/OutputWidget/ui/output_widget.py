import os
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc

from ..threads import AggThread
from ..data_processing import buildhar
from ..cmf_generators import (
    paramcmf, emisscmf, gtapvolcmf, gtapviewcmf, gtapsamcmf
)

from .popup_window import PopUpWindow


class Output(qtw.QWidget):
    """Main widget class for the GUI.

    Provides functionality for setting directories, running aggregation tasks, 
    and displaying the progress.
    """
    
    def __init__(self, **kargs):
        """Initializes the Output widget.

            Args:
            **kargs: Arbitrary keyword arguments, including `dataStore`.
        """

        self.datastore=kargs.get('dataStore')
        
        super().__init__()
        
        horizontal_layout1 = qtw.QHBoxLayout()

        vertical_layout1 = qtw.QVBoxLayout()
        vertical_layout1.setContentsMargins(10, 20, 50, 11)

        vertical_layout2 = qtw.QVBoxLayout()
        vertical_layout2.setContentsMargins(10, 20, 50, 11)

        vertical_layout3 = qtw.QVBoxLayout()
        vertical_layout3.setContentsMargins(10, 20, 50, 11)

        vertical_layout2 = qtw.QVBoxLayout()
       
        info_form = qtw.QFormLayout()
        
        self.destination_label = qtw.QLabel('<b> N\\A <\b>')
        info_form.addRow("<b>Target Directory for Aggrigation Files:</b>", self.destination_label)
        vertical_layout2.addLayout(info_form)
        
        horizontal_layout1.addLayout(vertical_layout2)
        horizontal_layout1.addLayout(vertical_layout1)
        horizontal_layout1.addLayout(vertical_layout3)
                
        
       
        self.setLayout(horizontal_layout1)
        
        self.getdirectory=qtw.QPushButton("Set Aggregation Directory", clicked=self.gettarget)
        self.startbutton=qtw.QPushButton("Run Aggregation", clicked=(lambda : self.makeagg(self.datastore.gtap_source, self.destination_label.text() )))
        
        
        vertical_layout1.addWidget(self.getdirectory)
        vertical_layout1.addWidget(self.startbutton)
        #vertical_layout1.addWidget(self.newscreenbutton)
        self.new_gtap=self.destination_label.text()


    def gettarget(self):
        """Opens a directory selection dialog and updates the target destination.

        This method displays a QFileDialog to allow the user to select a directory.
        The selected directory is then formatted and set as the text for the 
        `destination_label` attribute.

        Updates:
            self.destination_label (QLabel): Displays the selected directory path, 
            formatted to use backslashes instead of forward slashes.
        """
        
        directory = qtw.QFileDialog.getExistingDirectory()
        self.destination_label.setText(directory.replace('/','\\'))
        
    def makeagg(self, gtap_source, destination_file):
        """Runs the aggregation process and manages execution of sub-tasks.

        Args:
            gtap_source (str): Source directory for GTAP files.
            destination_file (str): Target directory for aggregation files.
        """
                
        if ( (os.path.exists(gtap_source) & os.path.exists(destination_file) != True)):
            execute_problem=qtw.QMessageBox()
            execute_problem.setWindowTitle('Not a valid destination')
            execute_problem.setText('Choose a valid folder')
            execute_problem.setInformativeText("You must choose a valid GTAP database .")
            execute_problem.setDetailedText("Directory or file does not exist")
            execute_problem.setWindowModality(qtc.Qt.WindowModality.WindowModal)
            execute_problem.exec()
            return
        

        #TBD test these for valid directories and files
        self.mywindow=PopUpWindow()
        
        #Make sets files
        buildhar(self, destination_file)

        #Make CMF files
        paramcmf(self, gtap_source, destination_file, 'par')
        emisscmf(self, gtap_source, destination_file, 'emiss')
        gtapvolcmf(self, gtap_source, destination_file, 'vole')
        gtapviewcmf(self, gtap_source, destination_file, 'gtpvew')
        gtapsamcmf(self, gtap_source, destination_file, 'samview')

        #Agghar.exe will not run if a previous file exists
        if os.path.exists(destination_file+"\\basedata.har"):
            os.remove(destination_file+"\\basedata.har")
        if os.path.exists("output.log"):
            os.remove("output.log")

        self.buildit = AggThread(gtap_source+'\\agghar.exe', gtap_source+'\\gsddat.har', destination_file+'\\basedata.har', destination_file+'\\aggsup.har')
        self.buildit.aggdone.connect(lambda: self.runpostagg(gtap_source, destination_file))
        self.buildit.read_file.connect(lambda x: self.updatestatusread(x, thread='base_data'))
        #self.buildit.write_file.connect(self.updatestatuswrite)
        #self.buildit.error_file.connect(self.updatestatuserror)
        
        self.buildit.start()
        

        self.param = AggThread(gtap_source + "\\aggpar.exe", '-cmf', destination_file+'\\par.cmf')
        self.param.read_file.connect(lambda x: self.updatestatusread(x, thread='param'))
        #self.param.write_file.connect(lambda x: self.updatestatuswrite(x, thread='param'))
        #self.param.error_file.connect(self.updatestatuserror)
        self.param.start() 

        self.emiss = AggThread(gtap_source + "\\aggemiss.exe", '-cmf', destination_file+'\\emiss.cmf')
        self.emiss.read_file.connect(lambda x: self.updatestatusread(x, thread='emiss'))
        #self.emiss.write_file.connect(self.updatestatuswrite)
        #self.emiss.error_file.connect(self.updatestatuserror)
        self.emiss.start()

        self.vole = AggThread(gtap_source + '\\aggvole.exe', '-cmf', destination_file+'\\vole.cmf')
        self.vole.read_file.connect(lambda x: self.updatestatusread(x, thread='vole'))
        #self.vole.write_file.connect(self.updatestatuswrite)
        # #self.vole.error_file.connect(self.updatestatuserror)
        self.vole.start()

    
    @qtc.pyqtSlot(str)
    def updatestatusread(self,status, thread):
        """Updates the progress status for reading operations.

        Args:
            status (str): The status message to display.
            thread (str): The thread name associated with the status.
        """
        if thread=='base_data':
            self.mywindow.base_data_text.setText(status)
        if thread=='param':
            self.mywindow.param_text.setText(status)
        if thread=='emiss':
            self.mywindow.emiss_text.setText(status)
        if thread == 'vole':
            self.mywindow.vol_text.setText(status)
        if thread == 'gtap_view':
            self.mywindow.gtapView_text.setText(status)
        if thread == 'sam_view':
            self.mywindow.gtapSam_text.setText(status) 

        self.mywindow.status_value+= 1
        self.mywindow.bar.setValue(self.mywindow.status_value)

    @qtc.pyqtSlot(str)
    def updatestatuswrite(self,status, thread):
        """Updates the progress status for writing operations.

        Args:
            status (str): The status message to display.
            thread (str): The thread name associated with the status.
        """
        
        if thread=='base_data':
            self.mywindow.base_data_text.setText(status)
        if thread=='param':
            self.mywindow.param_text.setText(status)
        if thread=='emiss':
            self.mywindow.emiss_text.setText(status)
        if thread == 'vole':
            self.mywindow.vol_text.setText(status)    
        self.value=self.value + 2
        self.bar.setValue(self.value)
     
    @qtc.pyqtSlot()
    def runpostagg(self, gtap_source, destination_file):
        """Executes post-aggregation tasks.

        Args:
            gtap_source (str): Source directory for GTAP files.
            destination_file (str): Target directory for aggregation files.
        """
        
        self.buildview = AggThread(gtap_source + "\\gtapview.exe", '-cmf', destination_file+'\\gtpvew.cmf')
        
        
        self.buildview.read_file.connect(lambda x: self.updatestatusread(x, thread='gtap_view'))
        #self.buildview.write_file.connect(self.updatestatuswrite)
        #self.buildview.error_file.connect(self.updatestatuserror)
        self.buildview.start()
        
        self.buildview.finished.connect(self.buildview.quit)
        


        self.buildsam = AggThread(gtap_source+"\\samview.exe", '-cmf', destination_file+'\\samview.cmf')
        self.buildsam.finished.connect(self.buildsam.quit)
        self.buildsam.read_file.connect(lambda x: self.updatestatusread(x, thread='sam_view'))
        #self.buildsam.write_file.connect(self.updatestatuswrite)
        #self.buildsam.error_file.connect(self.updatestatuserror)
        self.buildsam.start()