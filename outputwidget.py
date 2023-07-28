from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc

import GtapHelpers
from harpy import har_file, header_array
import numpy as np
import subprocess 
import os 
import re

def makeaggcmf(aggart):
        '''decoraotor for wrapping cmf files for final aggrigation progarm'''
        def inner(self, base_gtap, agg_gtap, file_name):
            cmf_file = open('{agg}\\{file}.cmf'.format(agg=agg_gtap, file=file_name), 'w+')
            cmf_file.write('check-on-read elements = no;\n')
            cmf_file.write('aux files = src\\agg{file};\n'.format(file=file_name)) 
            cmf_file.write('file DSETS = {base}\\sets.har;\n'.format(base=base_gtap))
            cmf_file.write('file ASETS = {agg}\\aggsup.har;\n'.format(agg=agg_gtap))
            
            add_these=aggart(self, base_gtap, agg_gtap, file_name)

            for i in add_these:
                cmf_file.write(i)

            cmf_file.close()

        return inner

def makeauxcmf(aggart):
    '''decoraotor for wrapping cmf files for auxilary progarm'''
    def inner(self, base_gtap, agg_gtap, file_name):
            cmf_file = open('{agg}\\{file}.cmf'.format(agg=agg_gtap, file=file_name), 'w+')
            cmf_file.write('check-on-read elements = no;\n')
            cmf_file.write('aux files = {base}\\src\\{file};\n'.format(base=base_gtap, file=file_name)) 
            cmf_file.write('file GTAPDATA = {agg}\\basedata.har;\n'.format(agg=agg_gtap))
            cmf_file.write('file GTAPSETS = {agg}\\aggsup.har;\n'.format(agg=agg_gtap))
            cmf_file.write('file GTAPPARM = {agg}\\par.har;\n'.format(agg=agg_gtap))
            
            add_these=aggart(self, base_gtap, agg_gtap, file_name)

            for i in add_these:
                cmf_file.write(i)

            cmf_file.close()

    return inner


class Output(qtw.QWidget):
    
    def __init__(self, **kargs):

        self.datastore=kargs.get('dataStore')
        
        super().__init__()
        
        horizontal_layout1 = qtw.QHBoxLayout()

        vertical_layout1 = qtw.QVBoxLayout()
        vertical_layout1.setContentsMargins(10, 20, 200, 11)

        vertical_layout2 = qtw.QVBoxLayout()
       
        info_form = qtw.QFormLayout()
        self.destination_label = qtw.QLabel('N\\A')
        info_form.addRow("Target Directory for Aggrigation Files:", self.destination_label)
        vertical_layout2.addLayout(info_form)
        
        horizontal_layout1.addLayout(vertical_layout1)
                
        
       
        self.setLayout(horizontal_layout1)
        
        self.getdirectory=qtw.QPushButton("Set Aggregation Directory", clicked=self.gettarget)
        self.startbutton=qtw.QPushButton("Run Aggregation", clicked=(lambda : self.makeagg(self.datastore.gtapsource, self.destination_label.text() )))
        self.newscreenbutton=qtw.QPushButton("New Screen", clicked=self.makescreen)
        
        vertical_layout1.addWidget(self.getdirectory)
        vertical_layout1.addWidget(self.startbutton)
        vertical_layout1.addWidget(self.newscreenbutton)
        self.new_gtap=self.destination_label.text()

    #slot
    def makescreen(self):
        self.mywindow=PopUpWindow()
        

    def gettarget(self):
        directory = qtw.QFileDialog.getExistingDirectory()
        self.destination_label.setText(directory.replace('/','\\'))
        
    def makeagg(self, iesc_source, destination_file):
        #self.iesc_source = iesc_source
        #self.destination_file = destination_file

        #TBD test these for valid directories and files
        self.mywindow=PopUpWindow()
        
        #Make sets files
        self.buildhar(destination_file)

        #Make CMF files
        self.paramcmf(iesc_source, destination_file, 'par')
        self.emisscmf(iesc_source, destination_file, 'emiss')
        self.gtapvolcmf(iesc_source, destination_file, 'vole')
        self.gtapviewcmf(iesc_source, destination_file, 'gtpvew')
        self.gtapsamcmf(iesc_source, destination_file, 'samview')


        if os.path.exists(destination_file+"\\basedata.har"):
            os.remove(destination_file+"\\basedata.har")

        if os.path.exists("output.log"):
            os.remove("output.log")

        #self.buildit = AggThread('agghar.exe', iesc_source+'\\basedata.har', destination_file+'\\basedata.har', destination_file+'\\aggsup.har')
        #self.buildit.start()
        
        self.buildit = AggThread('agghar.exe', iesc_source+'\\basedata.har', destination_file+'\\basedata.har', destination_file+'\\aggsup.har')
        self.buildit.aggdone.connect(lambda: self.runpostagg(iesc_source, destination_file))
        self.buildit.read_file.connect(lambda x: self.updatestatusread(x, thread='base_data'))
        #self.buildit.write_file.connect(self.updatestatuswrite)
        #self.buildit.error_file.connect(self.updatestatuserror)
        self.buildit.start()

        self.param = AggThread('.\\flexagg\\aggpar.exe', '-cmf', destination_file+'\\par.cmf')
        self.param.read_file.connect(lambda x: self.updatestatusread(x, thread='param'))
        #self.param.write_file.connect(self.updatestatuswrite)
        #self.param.error_file.connect(self.updatestatuserror)
        self.param.start() 

        self.emiss = AggThread('.\\flexagg\\aggemiss.exe', '-cmf', destination_file+'\\emiss.cmf')
        self.emiss.read_file.connect(lambda x: self.updatestatusread(x, thread='emiss'))
        #self.emiss.write_file.connect(self.updatestatuswrite)
        #self.emiss.error_file.connect(self.updatestatuserror)
        self.emiss.start()

        self.vole = AggThread('.\\flexagg\\aggvole.exe', '-cmf', destination_file+'\\vole.cmf')
        self.vole.read_file.connect(lambda x: self.updatestatusread(x, thread='vole'))
        #self.vole.write_file.connect(self.updatestatuswrite)
        #self.vole.error_file.connect(self.updatestatuserror)
        self.vole.start()
    
    @qtc.pyqtSlot(str)
    def updatestatusread(self,status, thread):
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
    def runpostagg(self, iesc_source, destination_file):
        
        self.buildview = AggThread(iesc_source+'\\src\\gtpvew.exe', '-cmf', destination_file+'\\gtpvew.cmf')
        self.buildview.finished.connect(self.buildview.quit)
        #self.buildview.read_file.connect(self.updatestatusread)
        #self.buildview.write_file.connect(self.updatestatuswrite)
        #self.buildview.error_file.connect(self.updatestatuserror)
        self.buildview.start()


        self.buildsam = AggThread(iesc_source+'\\src\\samview.exe', '-cmf', destination_file+'\\samview.cmf')
        self.buildsam.finished.connect(self.buildsam.quit)
        #self.buildsam.read_file.connect(self.updatestatusread)
        #self.buildsam.write_file.connect(self.updatestatuswrite)
        #self.buildsam.error_file.connect(self.updatestatuserror)
        self.buildsam.start()
        
    def buildhar(self, destination_file):

        aggsup= har_file.HarFileObj('{destination}\\aggsup.har'.format(destination=destination_file))
        dset= har_file.HarFileObj('{destination}\\dset.har'.format(destination=destination_file))
        
        self.makeasets(self.regions, "H1", "REG", aggsup)
        self.makeasets(self.sectors, "H2", "TRAD_COMM", aggsup)
        self.makeasets(self.sectors, "H5", "PROD_COMM", aggsup)
        self.makeasets(self.endowments, "H6","ENDW_COMM", aggsup)
        self.makeasets(['CGDS'], "H9", "CGDS_COMM", aggsup)

        self.makedsets(self.regions, "DH1", "DREG", aggsup)
        self.makedsets(self.sectors, "DH2", "TRAD_COMM", aggsup)
        self.makedsets(self.sectors, "DH5", "DPROD_COMM", aggsup)
        self.maketrae(self.endowments, "ETRE", "ETRAE", aggsup)
        self.makedsets(self.endowments, "DH6","DENDW_COMM", aggsup)
        
        self.makemapping(self.sectors, "MCOM", "TRAD_COMM", aggsup)
        self.makemapping(self.regions, "MREG", "REG", aggsup)
        self.makemapping(self.endowments, "MEND", "ENDW_COMM", aggsup)
        self.makemapping(self.sectors, "MPRD", "PROD_COMM", aggsup)

        #used by flex agg
        self.makedsets(self.regions, "H1", "REG", dset)
        self.makedsets(self.sectors, "H2", "TRAD_COMM", dset)
        self.makedsets(self.endowments, "H6","ENDW_COMM", dset)
        self.makedsets(['CGDS'], "H9", "CGDS_COMM", dset)

        self.makemapping(self.sectors, "DCOM", "TRAD_COMM", aggsup)
        self.makemapping(self.regions, "DREG", "REG", aggsup)
        self.makemapping(self.endowments, "DEND", "ENDW_COMM", aggsup)
        self.makemapping(self.sectors, "MARG", "MARG_COMM", dset)

        self.makeasets(self.sectors, "MARG", "MARG_COMM", aggsup)
        
        return 0

    def makemapping(self, target, mapname_sht, mapname_lng, har_file):

        data=target.model.newlist
        data=sorted(data, key=lambda k: k[0])
        
        #Metrics (if longname not provided)
        last_field=len(data[0])-1
        
        agg_map =  [i[last_field] for i in data]

        if mapname_sht == "MARG":
            agg_map = agg_map[51:54]

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
        '''makes aggregated sets'''

        #Take any list
        if type(target) is list:
           seta = target
        elif setname_sht == "MARG":
            seta=self.getaggmarg(target)

        #or specify an object in the QtData model, seee select widget
        else:
            seta = self.getaggsets(target)

        self.setstuffer(seta, setname_sht, setname_lng, har_file)

    def makedsets(self, target, setname_sht, setname_lng, har_file):
        '''makes disggregatedsets'''
        #Take any list
        if type(target) is list:
           set = target
        #or specifiy a QtData Model
        else:
            data=target.model.newlist
            data=sorted(data, key=lambda k: k[0])
            set = [i[1] for i in data]

        self.setstuffer(set, setname_sht, setname_lng, har_file)

    def maketrae(self, target, setname_sht, setname_lng, har_file):
        '''makes ETRAE sets'''
        #Take any list
        if type(target) is list:
           set = target
        #or specifiy a QtData Model
        else:
            data=target.parameter_model.newlist
            sort_list=self.getaggsets(target)
            #Mmale sure the data are sorted by the picklist
            data.sort(key=lambda i: sort_list.index(i[0]))
            set_1 = [0 if i[1] == 'mobile' else i[1] for i in data]
            set_1 = [float(i) for i in set_1]
            set = np.array([set_1], dtype=np.float32)
            
            #Create SLUG bases on values given
            slug= [0 if i == 'mobile' else 1 for i in [i[1] for i in data]]
            self.setstuffer(slug, 'SLUG', 'Sluggish Endowments', har_file)
        
        self.setstuffer(set, setname_sht, setname_lng, har_file)
     
    def setstuffer(self, set, setname_sht, setname_lng, har_file):
        'helper supports make sets'
        if setname_sht in ("DH5", "H5"):
            set.append("CGDS")
        
        my_set=header_array.HeaderArrayObj.HeaderArrayFromData(np.array(set), setname_sht, 
                        'Set {first}'.format(first=setname_lng))

        har_file[setname_sht] = my_set
        har_file.writeToDisk()

    def getaggsets(self, target):
        'helper gets data from the qtextlistmodel'
        myaset=[]
        for i in range(0,target.picker_model.rowCount()):
            item_index=target.picker_model.index(i)
            myaset.append(target.picker_model.data(item_index, qtc.Qt.DisplayRole))
        return myaset
    
    def getaggmarg(self, target):
        data=target.model.newlist
        data=sorted(data, key=lambda k: k[0])
        last_field=len(data[0])-1
         
        my_a_marg =  [i[last_field] for i in data]
        my_a_marg =  list(set(my_a_marg[51:55]))

        return my_a_marg

    @makeaggcmf 
    def paramcmf(self, base_iesc, agg_iesc, file_name):
        '''Make parameter cmf file'''

        insert_1 = 'file  DPARAM =  {base}\\default.prm;\n'.format(base=base_iesc)
        insert_2 = 'file  EPARAM =   {agg}\\aggsup.har;\n'.format(agg=agg_iesc)
        insert_3 = 'file  PARAM = {agg}\\{file}.har;\n'.format(agg=agg_iesc, file=file_name)
        insert_4 = 'file  DDATA= {base}\\basedata.har;\n'.format(base=base_iesc)

        return (insert_1, insert_2, insert_3, insert_4)  

    @makeaggcmf
    def emisscmf(self, base_iesc, agg_iesc, file_name):
        '''make emissions cmf'''
        insert_1 = 'file  EMISS = {agg}\\{file}.har;\n'.format(agg=agg_iesc, file=file_name) 
        insert_2 = 'file  DDATA= {base}\\{file}.har;\n'.format(base=base_iesc, file=file_name)

        return (insert_1, insert_2)

    @makeaggcmf
    def gtapvolcmf(self, base_iesc, agg_iesc, file_name):
        '''make energy volume cmf'''
        insert_1 = 'file  EGYVOL = {agg}\\{file}.har;\n'.format(agg=agg_iesc, file=file_name) 
        insert_2 = 'file  DDATA= {base}\\{file}.har;\n'.format(base=base_iesc, file=file_name)

        return (insert_1, insert_2)

    @makeauxcmf
    def gtapviewcmf(self, base_iesc, agg_iesc, file_name):
        '''gtap view'''
        insert_1 = 'file GTAPVIEW = {agg}\\baseview.har;\n'.format(agg=agg_iesc)
        insert_2 = 'file TAXRATES = {agg}\\baserate.har;\n'.format(agg=agg_iesc)

        return (insert_1, insert_2)

    @makeauxcmf
    def gtapsamcmf(self, base_iesc, agg_iesc, file_name):
        '''gtap same'''
        insert_1 = 'file GTAPSAM = {agg}\\GTAPsam.har;\n'.format(agg=agg_iesc)
        
        return (insert_1)
    
class PopUpWindow(qtw.QWidget):
    def __init__(self):
        super().__init__(None, modal=True)

        self.my_grid=qtw.QGridLayout()
        self.setLayout(self.my_grid)
        

        self.bar = qtw.QProgressBar(self)
        self.bar.setGeometry(0, 0, 100, 25)
        self.bar_label=qtw.QLabel('<b>Progress:<\b>')    
        self.bar.setMaximum(100)

        self.first_column_label=qtw.QLabel('<b><u>Databases</b>')
        self.second_column_label=qtw.QLabel('<b><u>Progress</b>')
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

        self.terminate_button=qtw.QPushButton('Terminate')
        self.close_button=qtw.QPushButton('Close')
    
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

        self.show()