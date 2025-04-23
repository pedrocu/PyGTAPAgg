from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc

from PyGTAPAgg import GtapHelpers
from modules.HARPY import har_file, header_array
import numpy as np
import subprocess 
import os 
import re

def makeaggcmf(aggart):
        """Decorator for wrapping CMF files for final aggregation programs.

    Args:
        aggart (function): The function to decorate.

    Returns:
        function: A wrapper function that creates and writes CMF files.
    """
        def inner(self, base_gtap, agg_gtap, file_name):
            cmf_file = open('{agg}\\{file}.cmf'.format(agg=agg_gtap, file=file_name), 'w+')
            cmf_file.write('check-on-read elements = no;\n')
            cmf_file.write('aux files = agg{file};\n'.format(file=file_name)) 
            cmf_file.write('file DSETS = {base}\\gsdset.har;\n'.format(base=base_gtap))
            cmf_file.write('file ASETS = {agg}\\aggsup.har;\n'.format(agg=agg_gtap))
            
            add_these=aggart(self, base_gtap, agg_gtap, file_name)

            for i in add_these:
                cmf_file.write(i)

            cmf_file.close()

        return inner

def makeauxcmf(aggart):
    """Decorator for wrapping CMF files for auxiliary programs.

    Args:
        aggart (function): The function to decorate.

    Returns:
        function: A wrapper function that creates and writes CMF files.
    """
    def inner(self, base_gtap, agg_gtap, file_name):
            cmf_file = open('{agg}\\{file}.cmf'.format(agg=agg_gtap, file=file_name), 'w+')
            cmf_file.write('check-on-read elements = no;\n')
            cmf_file.write('aux files = {base}\\{file};\n'.format(base=base_gtap, file=file_name)) 
            cmf_file.write('file GTAPDATA = {agg}\\basedata.har;\n'.format(agg=agg_gtap))
            cmf_file.write('file GTAPSETS = {agg}\\aggsup.har;\n'.format(agg=agg_gtap))
            cmf_file.write('file GTAPPARM = {agg}\\par.har;\n'.format(agg=agg_gtap))
            
            add_these=aggart(self, base_gtap, agg_gtap, file_name)

            for i in add_these:
                cmf_file.write(i)

            cmf_file.close()

    return inner


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

    #slot
    def makescreen(self):
        """Creates and initializes a new popup window.

        This method initializes a `PopUpWindow` instance and assigns it to the
        `mywindow` attribute. It is typically used to display additional information
        or user interfaces as a popup.
        """
        self.mywindow=PopUpWindow()
        

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
        self.buildhar(destination_file)

        #Make CMF files
        self.paramcmf(gtap_source, destination_file, 'par')
        self.emisscmf(gtap_source, destination_file, 'emiss')
        self.gtapvolcmf(gtap_source, destination_file, 'vole')
        self.gtapviewcmf(gtap_source, destination_file, 'gtpvew')
        self.gtapsamcmf(gtap_source, destination_file, 'samview')


        if os.path.exists(destination_file+"\\basedata.har"):
            os.remove(destination_file+"\\basedata.har")
        if os.path.exists("output.log"):
            os.remove("output.log")

        self.buildit = AggThread(gtap_source+'\\agghar.exe', gtap_source+'\\gsddat.har', destination_file+'\\basedata.har', destination_file+'\\aggsup.har')
        self.buildit.aggdone.connect(lambda: self.runpostagg(gtap_source, destination_file))
        self.buildit.read_file.connect(lambda x: self.updatestatusread(x, thread='base_data'))
        #self.buildit.write_file.connect(self.updatestatuswrite)
        #elf.buildit.error_file.connect(self.updatestatuserror)
        
        self.buildit.start()
        

        self.param = AggThread(gtap_source + "\\aggpar.exe", '-cmf', destination_file+'\\par.cmf')
        self.param.read_file.connect(lambda x: self.updatestatusread(x, thread='param'))
        #self.param.write_file.connect(self.updatestatuswrite)
        #self.param.error_file.connect(self.updatestatuserror)
        self.param.start() 

        self.emiss = AggThread(gtap_source + "\\aggemiss.exe", '-cmf', destination_file+'\\emiss.cmf')
        self.emiss.read_file.connect(lambda x: self.updatestatusread(x, thread='emiss'))
        #self.emiss.write_file.connect(self.updatestatuswrite)
        #self.emiss.error_file.connect(self.updatestatuserror)
        self.emiss.start()

        self.vole = AggThread(gtap_source + '\\aggvole.exe', '-cmf', destination_file+'\\vole.cmf')
        self.vole.read_file.connect(lambda x: self.updatestatusread(x, thread='vole'))
        # #self.vole.write_file.connect(self.updatestatuswrite)
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
        #self.value=self.value + 2
        #self.bar.setValue(self.value)
     
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
        
    def buildhar(self, destination_file):
        """Builds the HAR files required for aggregation.

        This method creates several HAR files based on the aggregated data,
        such as regions, sectors, and endowments. These files are used as inputs
        for the aggregation process.

        Args:
            destination_file (str): The directory where the HAR files will be created.

        Returns:
            int: Returns 0 upon successful execution.
        """

        aggsup= har_file.HarFileObj('{destination}\\aggsup.har'.format(destination=destination_file))
        dset= har_file.HarFileObj('{destination}\\dset.har'.format(destination=destination_file))
        
        #We want the unique lists of sect, reg, end from the data, not the list. The list can include values not inserted
        #Get thte values from the table so as not to create conflicts latter, consistency is maintained
        regions_x=list(set([i[5] for i in self.datastore.regions.data]))  #TBD Make these relative to the last element not 5
        sectors_x=list(set([i[5] for i in self.datastore.sectors.data]))  #TBD Make these relative to the last element not 5
        endw_x=list(set([i[4] for i in self.datastore.endowments.data]))  #TBD Make these relative to the last element not 4

        self.makeasets(regions_x, "H1", "REG", aggsup)
        self.makeasets(sectors_x, "H2", "TRAD_COMM", aggsup)
        self.makeasets(sectors_x, "H5", "PROD_COMM", aggsup)  #prod_comm is different from TRAD_COMM add CGDS for Trad_comm to get prod_Commm
        self.makeasets(endw_x, "H6","ENDW_COMM", aggsup)
        self.makeasets(['CGDS'], "H9", "CGDS_COMM", aggsup)
        self.makeasets(self.datastore.gtap_TARS, "TARS","Tariff componenets", aggsup)
        self.makeasets(self.datastore.gtap_TARL, "TARL","Long name tariff componenets", aggsup)

        #Need H7-ENDWS, H8-ENDWM
        #default.prm - ETRAE, SLUG

        self.makedsets(self.datastore.regions.data, "DH1", "DREG", aggsup)
        self.makedsets(self.datastore.sectors.data, "DH2", "TRAD_COMM", aggsup)
        self.makedsets(self.datastore.sectors.data, "DH5", "DPROD_COMM", aggsup)
        
        self.maketrae(self.datastore.endowments, "ETRE", "ETRAE", aggsup)
        
        self.makedsets(self.datastore.endowments.data, "DH6","DENDW_COMM", aggsup)
        
        self.makemapping(self.datastore.sectors.data, "MCOM", "TRAD_COMM", aggsup)
        self.makemapping(self.datastore.regions.data, "MREG", "REG", aggsup)
        self.makemapping(self.datastore.endowments.data, "MEND", "ENDW_COMM", aggsup)
        self.makemapping(self.datastore.sectors.data, "MPRD", "PROD_COMM", aggsup)

        #used by flex agg
        self.makedsets(self.datastore.regions.data, "H1", "REG", dset)
        self.makedsets(self.datastore.sectors.data, "H2", "TRAD_COMM", dset)
        self.makedsets(self.datastore.endowments.data, "H6","ENDW_COMM", dset)
        self.makedsets(['CGDS'], "H9", "CGDS_COMM", dset)
        self.makemapping(self.datastore.sectors.data, "MARG", "MARG_COMM", dset)

        self.makemapping(self.datastore.sectors.data, "DCOM", "TRAD_COMM", aggsup)
        self.makemapping(self.datastore.regions.data, "DREG", "REG", aggsup)
        self.makemapping(self.datastore.endowments.data, "DEND", "ENDW_COMM", aggsup)
        

        self.makeasets(self.datastore.sectors.data, "MARG", "MARG_COMM", aggsup)

        self.mywindow.sets_text.setText('<b>…DONE<\b>')
        
        return 0

    def makemapping(self, target, mapname_sht, mapname_lng, har_file):
        """Creates mapping data for aggregation.

        This method generates mapping information to relate items in the dataset
        (e.g., regions, sectors, endowments) to their aggregated counterparts.

        Args:
            target (list): The list of items to map.
            mapname_sht (str): Short name for the mapping variable.
            mapname_lng (str): Long name for the mapping variable.
            har_file (HarFileObj): The HAR file object where the mapping will be written.
        """
        
        data=sorted(target, key=lambda k: k[0])
               
        #Metrics (if longname not provided)
        last_field=len(data[0])-1
        
        
        agg_map =  [i[last_field] for i in data]
       

        if mapname_sht == "MARG":
            agg_map = [i[-1] for i in data if i[1] in ['otp', 'atp', 'wtp'] ]   
            print(agg_map)

        number_agg = len(set(agg_map))

        orig_set = [i[1] for i in data]
        number_items = len(set(orig_set))

        if mapname_sht == "MPRD":
            number_agg = number_agg+1
            number_items = number_items+1
            agg_map.append("CGDS")

        #Harpy 
        my_map=header_array.HeaderArrayObj.HeaderArrayFromData(np.array(agg_map), mapname_sht, 
                        'Mapping {short} from {long}({many}) to {long}({agg})'.format(long=mapname_lng, short=mapname_sht, many=number_items, agg=number_agg) )
        har_file[mapname_sht] = my_map
        
        har_file.writeToDisk() 
    

    def makeasets(self, target, setname_sht, setname_lng, har_file):
        """Creates aggregated sets and stores them in the HAR file.

        Aggregated sets are used to define groups of related items, such as regions,
        sectors, or endowments, for the purpose of aggregation.

        Args:
            target (list): The list of items to aggregate.
            setname_sht (str): The short name for the set variable.
            setname_lng (str): The long name for the set variable.
            har_file (HarFileObj): The HAR file object where the set will be written.
        """
        #Take any list
        if type(target) is list and setname_sht != 'MARG':
           seta = target.copy()
        elif setname_sht == "MARG":
            seta=self.getaggmarg(target)

        #or specify an object in the QtData model, seee select widget
        else:
            seta = target
            
        
        self.setstuffer(seta, setname_sht, setname_lng, har_file)

    def makedsets(self, target, setname_sht, setname_lng, har_file):
        """Creates disaggregated sets and stores them in the HAR file.

        Disaggregated sets are used to define individual items, such as specific
        regions, sectors, or endowments, that are part of a larger aggregated group.

        Args:
            target (list): The list of items to disaggregate.
            setname_sht (str): The short name for the set variable.
            setname_lng (str): The long name for the set variable.
            har_file (HarFileObj): The HAR file object where the set will be written.
        """
        
        #Take any list
        if type(target[0]) is str:
           set = target.copy()
           
        #or specifiy a QtData Model
        else:
            data=target
            data=sorted(data, key=lambda k: k[0])
            set = [i[1] for i in data]
            

        self.setstuffer(set, setname_sht, setname_lng, har_file)

    def maketrae(self, target, setname_sht, setname_lng, har_file):
        """Creates ETRAE sets for aggregation and stores them in the HAR file.

        ETRAE sets are used to define relationships between endowments for specific purposes.

        Args:
            target (object): The endowment data from the datastore.
            setname_sht (str): The short name for the ETRAE variable.
            setname_lng (str): The long name for the ETRAE variable.
            har_file (HarFileObj): The HAR file object where the set will be written.
        """
        #Take any list
        

        if type(target.etrae[0]) is str:
           set = target
        #or specifiy a QtData Model
           
        else:
            data=target.etrae
            sort_list=target.pick_start
            #Make sure the data are sorted by the picklist
            data.sort(key=lambda i: sort_list.index(i[0]))
            set_1 = [0 if i[1] == 'mobile' else i[1] for i in data]
            set_1 = [float(i) for i in set_1]
        
            set = np.array([set_1], dtype=np.float32)
            
            #Create SLUG bases on values given
            slug= [0 if i == 'mobile' else 1 for i in [i[1] for i in data]]
            self.setstuffer(slug, 'SLUG', 'Sluggish Endowments', har_file)
        
        
        self.setstuffer(set, setname_sht, setname_lng, har_file)
     
    def setstuffer(self, set, setname_sht, setname_lng, har_file):
        """Helper method to create and store sets in the HAR file.

        This method is a utility function that creates a set from the provided data
        and writes it into a HAR file.

        Args:
            seta (list or array): The data to be added to the set.
            setname_sht (str): The short name for the set variable.
            setname_lng (str): The long name for the set variable.
            har_file (HarFileObj): The HAR file object where the set will be written.
        """
        if setname_sht in ("DH5", "H5"):
            set.append("CGDS")
        
        my_set=header_array.HeaderArrayObj.HeaderArrayFromData(np.array(set), setname_sht, 
                        'Set {first}'.format(first=setname_lng))

        har_file[setname_sht] = my_set
        har_file.writeToDisk()

    def getaggsets(self, target):
        """Retrieves aggregated data from the Qt model.

        This method extracts the aggregated data from the Qt model and organizes it
        into a structured format for use in aggregation tasks.

        Args:
            target (QtModel): The Qt model containing the aggregation data.

        Returns:
            list: A list of unique aggregated items extracted from the model.
        """
        myaset=[]
        for i in range(0,target.picker_model.rowCount()):
            item_index=target.picker_model.index(i)
            myaset.append(target.picker_model.data(item_index, qtc.Qt.DisplayRole))
        return myaset
    
    def getaggmarg(self, target):
        """Retrieves MARG aggregated data.

        This method extracts MARG (Marginal) data, which is a specific subset of
        aggregated data used for certain aggregation tasks.

        Args:
            target (list): The input list containing the data for extraction.

        Returns:
            list: A list of unique aggregated MARG items extracted from the input data.
        """
        data=target
        data=sorted(data, key=lambda k: k[0])
        last_field=len(data[0])-1
         
        my_a_marg =  list(set([i[-1] for i in data if i[1] in ['otp', 'atp', 'wtp'] ]))
                                             #This should be otp, wtp, atp not positions in dataset

        return my_a_marg

    @makeaggcmf 
    def paramcmf(self, base_gtap, agg_gtap, file_name):
        """Generates the parameter CMF (Command Macro File) for aggregation.

        This method creates the necessary file references for the aggregation process
        and returns them as formatted strings.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the parameter file to be created.

        Returns:
            tuple: A tuple containing the formatted strings for each file reference:
                - DPARAM: Reference to the base parameter file.
                - EPARAM: Reference to the aggregation supplementary file.
                - PARAM: Reference to the parameter file being created.
                - DDATA: Reference to the base data file.
        """

        insert_1 = 'file  DPARAM =  {base}\\gsdpar.har;\n'.format(base=base_gtap)
        insert_2 = 'file  EPARAM =   {agg}\\aggsup.har;\n'.format(agg=agg_gtap)
        insert_3 = 'file  PARAM = {agg}\\{file}.har;\n'.format(agg=agg_gtap, file=file_name)
        insert_4 = 'file  DDATA= {base}\\gsddat.har;\n'.format(base=base_gtap)

        return (insert_1, insert_2, insert_3, insert_4)  

    @makeaggcmf
    def emisscmf(self, base_gtap, agg_gtap, file_name):
        """Generates the emissions CMF (Command Macro File) for aggregation.

        This method creates the necessary file references for the emissions data
        aggregation process and returns them as formatted strings.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the emissions file to be created.

        Returns:
            tuple: A tuple containing the formatted strings for each file reference:
                - EMISS: Reference to the aggregated emissions file.
                - DDATA: Reference to the base emissions data file.
        """
        insert_1 = 'file  EMISS = {agg}\\{file}.har;\n'.format(agg=agg_gtap, file=file_name) 
        insert_2 = 'file  DDATA= {base}\\gsdemiss.har;\n'.format(base=base_gtap, file=file_name)

        return (insert_1, insert_2)

    @makeaggcmf
    def gtapvolcmf(self, base_gtap, agg_gtap, file_name):
        """Generates the energy volume CMF (Command Macro File) for aggregation.

        This method creates the necessary file references for the energy volume 
        data aggregation process and returns them as formatted strings.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the energy volume file to be created.

        Returns:
            tuple: A tuple containing the formatted strings for each file reference:
                - EGYVOL: Reference to the aggregated energy volume file.
                - DDATA: Reference to the base energy volume data file.
        """
        insert_1 = 'file  EGYVOL = {agg}\\{file}.har;\n'.format(agg=agg_gtap, file=file_name) 
        insert_2 = 'file  DDATA= {base}\\gsdvole.har;\n'.format(base=base_gtap, file=file_name)

        return (insert_1, insert_2)

    @makeauxcmf
    def gtapviewcmf(self, base_gtap, agg_gtap, file_name):
        """Generates the GTAP View CMF (Command Macro File) for aggregation.

        This method creates the necessary file references for the GTAP View 
        aggregation process and returns them as formatted strings.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the GTAP View file to be created.

        Returns:
            tuple: A tuple containing the formatted strings for each file reference:
                - GTAPVIEW: Reference to the base view file.
                - TAXRATES: Reference to the base tax rates file.
        """
        insert_1 = 'file GTAPVIEW = {agg}\\baseview.har;\n'.format(agg=agg_gtap)
        insert_2 = 'file TAXRATES = {agg}\\baserate.har;\n'.format(agg=agg_gtap)

        return (insert_1, insert_2)

    @makeauxcmf
    def gtapsamcmf(self, base_gtap, agg_gtap, file_name):
        """Generates the GTAP SAM CMF (Command Macro File) for aggregation.

        This method creates the necessary file reference for the GTAP SAM 
        (Social Accounting Matrix) aggregation process and returns it as a 
        formatted string.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the GTAP SAM file to be created.

        Returns:
            tuple: A tuple containing the formatted string for the GTAP SAM file reference:
                - GTAPSAM: Reference to the aggregated GTAP SAM file.
        """
        insert_1 = 'file GTAPSAM = {agg}\\GTAPsam.har;\n'.format(agg=agg_gtap)
        
        return (insert_1)
    
class AggThread(qtc.QThread):
    """Executes aggregation processes in a separate thread.

    This class is responsible for handling long-running aggregation tasks 
    asynchronously in a separate thread, preventing the main application 
    from freezing during execution. It supports emitting signals for real-time 
    updates and results from the aggregation process.

    Attributes:
        read_file (pyqtSignal): Signal emitted to provide updates on the progress 
            of the aggregation process. This typically contains status messages 
            or logs generated during execution.
        args (list): List of arguments to be passed to the subprocess for the 
            aggregation task.
    """
    aggdone    = qtc.pyqtSignal()
    read_file  = qtc.pyqtSignal(str, str)
    write_file = qtc.pyqtSignal(str,str)
    error_file = qtc.pyqtSignal(str,str)

    def __init__(self, *args):

        """Initializes the AggThread object.

        Args:
            *args: Arguments for the aggregation subprocess. These typically 
                include the path to the aggregation program and any necessary 
                parameters or input files.
        """
        self.args=args
        super().__init__()

    def run(self):
        """Executes the aggregation subprocess and emits a signal upon completion.

        This method starts the subprocess using the provided arguments during
        initialization, waits for the process to complete, and then emits the
        `aggdone` signal to notify that the aggregation process has finished.

        Raises:
            Note this is not done as an exception, it should be recast as one.
            subprocess.SubprocessError: If an error occurs during the execution of the
                subprocess.

                 try:
            # Start the subprocess
            p = subprocess.Popen(self.args, encoding='UTF-8')
            p.wait()  # Wait for the subprocess to complete

            # Emit the signal indicating that the aggregation is done
            self.aggdone.emit()
            except subprocess.SubprocessError as e:
            print(f"Error during subprocess execution: {e}")
            raise
        """
        print("here are the args to run: ", self.args)
        if os.path.exists(self.args[0]):
            p=subprocess.Popen(self.args, 
                            stdout=subprocess.PIPE,
                            encoding='UTF-8')
        else:
            cwd = os.getcwd()
            print(cwd)
            print('file not found:  ' , self.args[0])
        print('my args: ', self.args)
        self.read_file.emit('<b>Initilizing…<\b>', self.args[0])
        self.write_file.emit('<b>Initilizing…<\b>', self.args[0])
        

        #Write to log and to the interface

        with open('output' + '.log', 'a') as log:
        
            while p.poll() is None:
                outdata=p.stdout.readline()
                my_match=re.search(r'(.*)Reading(.*)', outdata, re.M|re.I)
                if my_match:
                    self.read_file.emit(my_match.group(0), self.args[0])
                
                my_match=re.search(r'(.*)Writing(.*)', outdata, re.M|re.I)
                if my_match:
                   self.write_file.emit(my_match.group(0), self.args[0])

                my_match=re.search(r'(.*)Error(.*)', outdata, re.M|re.I)
                if my_match:
                    self.error_file.emit(my_match.group(0), self.args[0])

                my_match=re.search(r'(.*)Warning(.*)', outdata, re.M|re.I)
                if my_match:
                    self.error_file.emit(my_match.group(0), self.args[0])
 
                log.write(outdata)
                
        
        self.read_file.emit('<b>…DONE<\b>', self.args[0])
        self.write_file.emit('<b>…DONE<\b>', self.args[0])
        
        self.aggdone.emit()
class AggHar(qtc.QObject):
    """Executes aggregation processes for HAR files using a subprocess.

    This class runs aggregation tasks synchronously in a separate process and
    emits a signal upon completion. It is primarily used to execute external
    aggregation programs or scripts.

    Attributes:
        aggdone (pyqtSignal): Signal emitted when the aggregation process is completed.
        args (list): List of arguments to be passed to the subprocess.
    """
    aggdone=qtc.pyqtSignal()

    def __init__(self, *args):
        """Initializes the AggHar object and executes the subprocess.

        Args:
            *args: Arguments to be passed to the subprocess for execution. These
                typically include the path to the aggregation program and any
                necessary parameters or input files.
        """
        self.args=args
        super().__init__()

        p=subprocess.Popen(self.args, encoding='UTF-8')
        p.wait()
        
        self.aggdone.emit()
    
class PopUpWindow(qtw.QWidget):
    """Popup window class for displaying progress and status of aggregation tasks.

    This class provides a user interface with a progress bar and labels to show
    the status of various components during the aggregation process. It also
    includes buttons to terminate or close the popup.

    Attributes:
        status_value (int): The current progress value for the progress bar.
        my_grid (QGridLayout): The layout manager for the popup window.
        bar (QProgressBar): The progress bar widget.
        bar_label (QLabel): The label for the progress bar.
        terminate_button (QPushButton): The button to terminate aggregation tasks.
        close_button (QPushButton): The button to close the popup window.
    """

    def __init__(self):
        """Initializes the popup window with a progress bar and status labels."""
        self.status_value = 0

        super().__init__(None, modal=True)

        self.my_grid=qtw.QGridLayout()
        self.setLayout(self.my_grid)
        

        self.bar = qtw.QProgressBar(self)
        self.bar.setGeometry(0, 0, 100, 25)
        self.bar_label=qtw.QLabel('<b>Progress:<\b>')    
        self.bar.setMaximum(100)

        self.first_column_label=qtw.QLabel('<b><u>Databases</b>')
        self.second_column_label=qtw.QLabel('<b></b>')
        self.third_column_label=qtw.QLabel('<b><u>Status</b>')

        self.base_data_label=qtw.QLabel('Basedata.har')
        self.sets_label=qtw.QLabel('Sets.har')
        self.param_label=qtw.QLabel('Param.har')
        self.gtapView_label=qtw.QLabel('gtapView.har')
        self.gtapSam_label=qtw.QLabel('gtapSam.har')
        self.vol_label=qtw.QLabel('vol.har')
        self.emiss_label=qtw.QLabel('emiss.har')

        self.base_data_text=qtw.QLabel('Not executed... ')
        self.sets_text=qtw.QLabel('Not executed...')
        self.param_text=qtw.QLabel('Not executed... ')
        self.gtapView_text=qtw.QLabel('Not executed... ')
        self.gtapSam_text=qtw.QLabel('Not executed... ')
        self.vol_text=qtw.QLabel('Not executed... ')
        self.emiss_text=qtw.QLabel('Not executed... ')

        self.terminate_button=qtw.QPushButton('Terminate', self)
        self.close_button=qtw.QPushButton('Close', self)
    
        self.my_grid.addWidget(self.bar_label,0,0)
        self.my_grid.addWidget(self.bar, 1,0,1,3)

        self.my_grid.addWidget(self.first_column_label,2,0)
        self.my_grid.addWidget(self.second_column_label,2,1)
        self.my_grid.addWidget(self.third_column_label,2,2)

        
        self.my_grid.addWidget(self.base_data_label,3,0)
        self.my_grid.addWidget(self.sets_label,4,0)
        self.my_grid.addWidget(self.param_label,5,0)
        self.my_grid.addWidget(self.gtapView_label,6,0)
        self.my_grid.addWidget(self.gtapSam_label,7,0)
        self.my_grid.addWidget(self.vol_label,8,0)
        self.my_grid.addWidget(self.emiss_label,9,0)

        self.my_grid.addWidget(self.base_data_text,3,2)
        self.my_grid.addWidget(self.sets_text,4,2)
        self.my_grid.addWidget(self.param_text,5,2)
        self.my_grid.addWidget(self.gtapView_text,6,2)
        self.my_grid.addWidget(self.gtapSam_text,7,2)
        self.my_grid.addWidget(self.vol_text,8,2)
        self.my_grid.addWidget(self.emiss_text,9,2)

        self.my_grid.addWidget(self.terminate_button,10,1)
        self.my_grid.addWidget(self.close_button, 10,2)

        self.close_button.clicked.connect(lambda: self.close())

        self.show()

    def shut_me(self):
        """Closes the popup window."""
        self.close()