
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
import json


class ItemTableModel(qtc.QAbstractTableModel):
    """The model for aggregation table - the right hand tile"""

    def __init__(self, tab_type, headers, data):
        super().__init__()
        self.start(tab_type, headers, data)
        
    def start(self, tab_type, headers, data):
        ''''__init__ code'''
        self._headers=headers             
        self._newlist = data

    @property
    def headers(self):
        return self._headers

    @property
    def newlist(self):
        return self._newlist
    
    @headers.setter
    def headers(self,x):
        self._headers=x

    def load(self, tab_type):
        with open(tab_type + '.json') as f:
            data=json.load(f)
        return data
    
    #Required for QTableModel
    def rowCount(self, parent):
        return len(self._newlist)

    #Required for QTableModel
    def columnCount(self, parent):
        #print('number of colums ', len(self._headers))
        return len(self._headers)
    
    #Required for QTAbleModel
    def data(self, index, role):
        if role in (qtc.Qt.ItemDataRole.DisplayRole, qtc.Qt.ItemDataRole.EditRole):
           #print(self._newlist)
           #print(index.row())
           #print(index.column())
           return self._newlist[index.row()][index.column()]
        if role == qtc.Qt.ItemDataRole.BackgroundRole:
            if self._newlist[index.row()][index.column()] == '':
               return qtg.QBrush(qtc.Qt.GlobalColor.red)
        if role == qtc.Qt.ItemDataRole.ToolTipRole:
                return self._newlist[index.row()][3]

    # Additional features methods:
    def headerData(self, section, orientation, role):

        if orientation == qtc.Qt.Orientation.Horizontal and role == qtc.Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        
        else:
            return super().headerData(section, orientation, role)

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()  # needs to be emitted before a sort
        self._newlist = sorted(self._newlist, key=lambda k: k[column]) 
        if order == qtc.Qt.SortOrder.DescendingOrder:
            self._newlist.reverse()
        self.layoutChanged.emit()  # needs to be emitted after a sort

    # Methods for Read/Write

    def flags(self, index):
        if index.column() == self.columnCount(None)-1:
            return super().flags(index) | qtc.Qt.ItemFlag.ItemIsEditable
        else:
            return super().flags(index)
    
    #Qt Required to edit data
    def setData(self, index, value, role):
        if index.isValid():
            if role == qtc.Qt.ItemDataRole.EditRole and index.column()==self.columnCount(None)-1:
                self._newlist[index.row()][index.column()] = value
                self.dataChanged.emit(index, index, [qtc.Qt.ItemDataRole.DisplayRole, qtc.Qt.ItemDataRole.EditRole, qtc.Qt.ItemDataRole.BackgroundRole])
                return True
        else:
            return False