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
        self.mywindow=PopUpWindow()
        

    def gettarget(self):
        directory = qtw.QFileDialog.getExistingDirectory()
        self.destination_label.setText(directory.replace('/','\\'))
        
    def makeagg(self, gtap_source, destination_file):
        #self.iesc_source = iesc_source
        #self.destination_file = destination_file

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

        self.buildit = AggThread('agghar.exe', gtap_source+'\\basedata.har', destination_file+'\\basedata.har', destination_file+'\\aggsup.har')
        self.buildit.aggdone.connect(lambda: self.runpostagg(gtap_source, destination_file))
        self.buildit.read_file.connect(lambda x: self.updatestatusread(x, thread='base_data'))
        # #self.buildit.write_file.connect(self.updatestatuswrite)
        # #self.buildit.error_file.connect(self.updatestatuserror)
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
        # #self.vole.write_file.connect(self.updatestatuswrite)
        # #self.vole.error_file.connect(self.updatestatuserror)
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
        if thread == 'gtap_view':
            self.mywindow.gtapView_text.setText(status)
        if thread == 'sam_view':
            self.mywindow.gtapSam_text.setText(status) 

        self.mywindow.status_value+= 1.2
        self.mywindow.bar.setValue(self.mywindow.status_value)

    @qtc.pyqtSlot(str)
    def updatestatuswrite(self,status, thread):
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
        
        self.buildview = AggThread("C:\\Users\\Pedro299\\code\\IESC\\V10a\\2IESCData10\\src\\gtpvew.exe", '-cmf', destination_file+'\\gtpvew.cmf')
        
        
        self.buildview.read_file.connect(lambda x: self.updatestatusread(x, thread='gtap_view'))
        #self.buildview.write_file.connect(self.updatestatuswrite)
        #self.buildview.error_file.connect(self.updatestatuserror)
        self.buildview.start()
        
        self.buildview.finished.connect(self.buildview.quit)
        


        self.buildsam = AggThread("C:\\Users\\Pedro299\\code\\IESC\\V10a\\2IESCData10\\src\\gtpvew.exe", '-cmf', destination_file+'\\samview.cmf')
        self.buildsam.finished.connect(self.buildsam.quit)
        self.buildsam.read_file.connect(lambda x: self.updatestatusread(x, thread='sam_view'))
        #self.buildsam.write_file.connect(self.updatestatuswrite)
        #self.buildsam.error_file.connect(self.updatestatuserror)
        self.buildsam.start()
        
    def buildhar(self, destination_file):

        aggsup= har_file.HarFileObj('{destination}\\aggsup.har'.format(destination=destination_file))
        dset= har_file.HarFileObj('{destination}\\dset.har'.format(destination=destination_file))
        
        self.makeasets(self.datastore.regions.pick_start, "H1", "REG", aggsup)
        self.makeasets(self.datastore.sectors.pick_start, "H2", "TRAD_COMM", aggsup)
        self.makeasets(self.datastore.sectors.pick_start, "H5", "PROD_COMM", aggsup)  #prod_comm is different from TRAD_COMM add CGDS for Trad_comm to get prod_Commm
        self.makeasets(self.datastore.endowments.pick_start, "H6","ENDW_COMM", aggsup)
        self.makeasets(['CGDS'], "H9", "CGDS_COMM", aggsup)

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

        self.makemapping(self.datastore.sectors.data, "DCOM", "TRAD_COMM", aggsup)
        self.makemapping(self.datastore.regions.data, "DREG", "REG", aggsup)
        self.makemapping(self.datastore.endowments.data, "DEND", "ENDW_COMM", aggsup)
        self.makemapping(self.datastore.sectors.data, "MARG", "MARG_COMM", dset)

        self.makeasets(self.datastore.sectors.data, "MARG", "MARG_COMM", aggsup)

        print('just before sets')

        self.mywindow.sets_text.setText('<b>…DONE<\b>')
        
        return 0

    def makemapping(self, target, mapname_sht, mapname_lng, har_file):

        
        data=sorted(target, key=lambda k: k[0])
        
        #Metrics (if longname not provided)
        last_field=len(data[0])-1
        
        agg_map =  [i[last_field] for i in data]

        if mapname_sht == "MARG":
            agg_map = agg_map[51:54]    #Fix this so it pulls otp, atp, wtp

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
        if type(target) is list and setname_sht != 'MARG':
           seta = target
        elif setname_sht == "MARG":
            seta=self.getaggmarg(target)

        #or specify an object in the QtData model, seee select widget
        else:
            seta = target

        self.setstuffer(seta, setname_sht, setname_lng, har_file)

    def makedsets(self, target, setname_sht, setname_lng, har_file):
        '''makes disggregatedsets'''
        
        #Take any list
        if type(target[0]) is str:
           set = target
           
        #or specifiy a QtData Model
        else:
            data=target
            data=sorted(data, key=lambda k: k[0])
            set = [i[1] for i in data]
            

        self.setstuffer(set, setname_sht, setname_lng, har_file)

    def maketrae(self, target, setname_sht, setname_lng, har_file):
        '''makes ETRAE sets'''
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
        data=target
        data=sorted(data, key=lambda k: k[0])
        last_field=len(data[0])-1
         
        my_a_marg =  [i[last_field] for i in data]
        my_a_marg =  list(set(my_a_marg[51:55]))      #This should be otp, wtp, atp not positions in dataset

        return my_a_marg

    @makeaggcmf 
    def paramcmf(self, base_gtap, agg_gtap, file_name):
        '''Make parameter cmf file'''

        insert_1 = 'file  DPARAM =  {base}\\par.har;\n'.format(base=base_gtap)
        insert_2 = 'file  EPARAM =   {agg}\\aggsup.har;\n'.format(agg=agg_gtap)
        insert_3 = 'file  PARAM = {agg}\\{file}.har;\n'.format(agg=agg_gtap, file=file_name)
        insert_4 = 'file  DDATA= {base}\\basedata.har;\n'.format(base=base_gtap)

        return (insert_1, insert_2, insert_3, insert_4)  

    @makeaggcmf
    def emisscmf(self, base_gtap, agg_gtap, file_name):
        '''make emissions cmf'''
        insert_1 = 'file  EMISS = {agg}\\{file}.har;\n'.format(agg=agg_gtap, file=file_name) 
        insert_2 = 'file  DDATA= {base}\\{file}.har;\n'.format(base=base_gtap, file=file_name)

        return (insert_1, insert_2)

    @makeaggcmf
    def gtapvolcmf(self, base_gtap, agg_gtap, file_name):
        '''make energy volume cmf'''
        insert_1 = 'file  EGYVOL = {agg}\\{file}.har;\n'.format(agg=agg_gtap, file=file_name) 
        insert_2 = 'file  DDATA= {base}\\{file}.har;\n'.format(base=base_gtap, file=file_name)

        return (insert_1, insert_2)

    @makeauxcmf
    def gtapviewcmf(self, base_gtap, agg_gtap, file_name):
        '''gtap view'''
        insert_1 = 'file GTAPVIEW = {agg}\\baseview.har;\n'.format(agg=agg_gtap)
        insert_2 = 'file TAXRATES = {agg}\\baserate.har;\n'.format(agg=agg_gtap)

        return (insert_1, insert_2)

    @makeauxcmf
    def gtapsamcmf(self, base_gtap, agg_gtap, file_name):
        '''gtap same'''
        insert_1 = 'file GTAPSAM = {agg}\\GTAPsam.har;\n'.format(agg=agg_gtap)
        
        return (insert_1)
    
class AggThread(qtc.QThread):
    aggdone    = qtc.pyqtSignal()
    read_file  = qtc.pyqtSignal(str, str)
    write_file = qtc.pyqtSignal(str,str)
    error_file = qtc.pyqtSignal(str,str)

    def __init__(self, *args):
        self.args=args
        super().__init__()

    def run(self):
        print("here are the args to run: ", self.args)
        if os.path.exists(self.args[0]):
            p=subprocess.Popen(self.args, 
                            stdout=subprocess.PIPE,
                            encoding='UTF-8')
        else:
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
    aggdone=qtc.pyqtSignal()

    def __init__(self, *args):
        
        self.args=args
        super().__init__()
        

        p=subprocess.Popen(self.args, encoding='UTF-8')
        p.wait()
        

        self.aggdone.emit()
    
class PopUpWindow(qtw.QWidget):
    def __init__(self):
        self.status_value = 0

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
        self.close()