from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
from PyGTAPAgg.tab_selections_itemtablemodel import ItemTableModel

class EndowmentParameter(ItemTableModel):
    def __init__(self, etrae):
        self._newlist=etrae
        self._headers= ['Abbreviation', 'ETRAE']
        qtc.QAbstractItemModel.__init__(self)
        #self.start(pick_start)
   
    
    def data(self, index, role):
        '''reimplemented to remove tooltip role'''
        if role in (qtc.Qt.ItemDataRole.DisplayRole, qtc.Qt.ItemDataRole.EditRole):
           return self._newlist[index.row()][index.column()]
        if role == qtc.Qt.ItemDataRole.BackgroundRole:
           if self._newlist[index.row()][index.column()] == '':
               return qtg.QBrush(qtc.Qt.GlobalColor.red)
        '''removed tool tip role'''
    
    def insertRows(self, row=0, rows=1, index=qtc.QModelIndex(), values=['','']):
       
        self.beginInsertRows(qtc.QModelIndex(), row, row + rows - 1)
        for row in range(rows):
            self._newlist.insert(row, values)
        self.endInsertRows()
        return True

    def removeRow(self, row=0, index=qtc.QModelIndex(), values=[]):
        self.beginRemoveRows(qtc.QModelIndex(), row, row)
        self._newlist.pop(row)        
        self.endRemoveRows()
        return True