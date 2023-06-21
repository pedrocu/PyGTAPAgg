
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from harpy import har_file, header_array
import numpy as np

def getdbversize(gtap, source) -> tuple:
    settings = qtc.QSettings()

    '''takes directory for GTAP and returns a tuple with discriptive data'''
    try:
        gtap_base=har_file.HarFileObj(gtap+source)
        gtap_sets=har_file.HarFileObj(gtap+ '\\sets.har')
        
        gtap_ver_num=str(gtap_base['DREL'].array[0])
        gtap_num_reg=gtap_sets['H1'].array.size
        gtap_num_sect=gtap_sets['H2'].array.size
        gtap_num_endow=gtap_sets['H6'].array.size

        #qtc.QCoreApplication.setOrganizationName("ImpactECON")
        #qtc.QCoreApplication.setOrganizationDomain("impactecon.com")
        #qtc.QCoreApplication.setOrganizationName("PyGTAPAgg")
        
        
        settings.setValue('indir', gtap)

        print(settings.value('indir'))

    except Exception as error:
        execute_problem=qtw.QMessageBox()
        execute_problem.setWindowTitle('Not a valid GTAP Database')
        execute_problem.setText('Choose a Valid GTAP Database')
        execute_problem.setInformativeText("You must choose a valid GTAP database .")
        execute_problem.setDetailedText(str(error))
        execute_problem.setWindowModality(qtc.Qt.WindowModality.WindowModal)
        execute_problem.exec()
        iesc_dat = ['NA']*5
        iesc_dat[1] = 'NA_NA_NA'
        settings.setValue('indir', 'NA')
        return iesc_dat

    gtap_dat = [gtap, gtap_ver_num, gtap_num_reg, gtap_num_sect, gtap_num_endow]

    return gtap_dat


def getvalues(self, selectionlist)-> list:
    values = []
    for item in selectionlist:
        values.append(self.picker_model.data(item, qtc.Qt.ItemDataRole.DisplayRole))
    return values
