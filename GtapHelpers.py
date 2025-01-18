
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from HARPY import har_file, header_array
import numpy as np

def getdbversize(gtap, source) -> tuple:
    settings=qtc.QSettings("ImpactECON","PyGTAPAgg")

    '''takes directory for GTAP and returns a tuple with discriptive data'''
    try:
        gtap_base=har_file.HarFileObj(gtap+'\\gsddat.har')
        gtap_sets=har_file.HarFileObj(gtap+'\\gsdset.har')
        gtap_ver_num=(str(gtap_base['DREL'].array[0]), gtap_base['DREL'].array[1], gtap_base['DREL'].array[2])
        gtap_num_reg=gtap_sets['H1'].array.size
        gtap_num_sect=gtap_sets['H2'].array.size
        gtap_num_endow=gtap_sets['H6'].array.size
        
        
       
        ''' if gtap_base['DREL'].array.size == 3:
            print("stop2")
            #Done this way to be consistent with all versions of GTAP earlier then V11.
            gtap_ver_num = gtap_base['DREL'].array[0] + '_' + gtap_base['DREL'].array[1] + '_' + gtap_base['DREL'].array[2]
        else:
            print("stop3")
            #This is the way all the version before 11 were formatted
            gtap_ver_num=str(gtap_base['DREL'].array[0])    '''
        
        settings.setValue('indir', gtap)
        

       

    except Exception as error:
        execute_problem=qtw.QMessageBox()
        execute_problem.setWindowTitle('Not a valid GTAP Database')
        execute_problem.setText('Choose a Valid GTAP Database')
        execute_problem.setInformativeText("You must choose a valid GTAP database .")
        execute_problem.setDetailedText(str(error))
        execute_problem.setWindowModality(qtc.Qt.WindowModality.WindowModal)
        execute_problem.exec()
        iesc_dat = ['NA']*5
        iesc_dat[1] = ('NA','NA', 'NA')
        settings.setValue('indir', None)
        return iesc_dat

    gtap_dat = [gtap, gtap_ver_num, gtap_num_reg, gtap_num_sect, gtap_num_endow]

    return gtap_dat


def getvalues(self, selectionlist)-> list:
    values = []
    for item in selectionlist:
        values.append(self._picker_model.data(item, qtc.Qt.ItemDataRole.DisplayRole))
    return values
