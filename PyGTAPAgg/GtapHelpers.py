
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from modules.HARPY import har_file, header_array
import numpy as np

def getdbversize(gtap, source) -> tuple:

    """
    Takes a directory for the GTAP database and returns descriptive data as a tuple.

    Args:
        gtap (str): The directory path to the GTAP database.
        source (str): The source of the GTAP database.

    Returns:
        tuple: A tuple containing:
            - gtap (str): The input directory path.
            - gtap_ver_num (tuple): The version number of the GTAP database.
            - gtap_num_reg (int): The number of regions in the GTAP database.
            - gtap_num_sect (int): The number of sectors in the GTAP database.
            - gtap_num_endow (int): The number of endowments in the GTAP database.

    Raises:
        Exception: If the provided directory is not a valid GTAP database, a QMessageBox is shown and a default tuple is returned.
    """
    settings=qtc.QSettings("ImpactECON","PyGTAPAgg")

    try:
        gtap_base=har_file.HarFileObj(gtap+'\\gsddat.har')
        gtap_sets=har_file.HarFileObj(gtap+'\\gsdset.har')
        gtap_ver_num=(str(gtap_base['DREL'].array[0]).strip(), str(gtap_base['DREL'].array[1]).strip(), str(gtap_base['DREL'].array[2]).strip())
        gtap_num_reg=gtap_sets['H1'].array.size
        gtap_num_sect=gtap_sets['H2'].array.size
        gtap_num_endow=gtap_sets['H6'].array.size
                        
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
    """
    Extracts and returns display values from a selection list.

    Args:
        self: The object instance containing the picker model.
        selectionlist (list): A list of selected items.

    Returns:
        list: A list of display values corresponding to the selected items.
    """
    values = []
    for item in selectionlist:
        values.append(self._picker_model.data(item, qtc.Qt.ItemDataRole.DisplayRole))
    return values
