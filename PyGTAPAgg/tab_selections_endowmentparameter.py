from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
from PyGTAPAgg.tab_selections_itemtablemodel import ItemTableModel

class EndowmentParameter(ItemTableModel):
    """
    Model for managing endowment parameters in a table.

    This model extends ItemTableModel to specifically handle endowment data, 
    such as abbreviations and ETRAE values. It customizes the data roles and 
    provides methods for inserting and removing rows, suitable for use with 
    PyQt6's model/view framework.

    Args:
        etrae (list[list[Any]]): Initial endowment data, where each item is 
            typically a [abbreviation, ETRAE] pair.

    Attributes:
        _newlist (list[list[Any]]): The current list of endowment rows.
        _headers (list[str]): The column headers, defaulting to 
            ['Abbreviation', 'ETRAE'].
    """
    def __init__(self, etrae):
        """
        Initialize the EndowmentParameter model.

        Args:
            etrae (list[list[Any]]): Initial list of endowment entries.
        """
        self._newlist=etrae
        self._headers= ['Abbreviation', 'ETRAE']
        qtc.QAbstractItemModel.__init__(self)
        #self.start(pick_start)
   
    
    def data(self, index, role):
        """
        Return data for a given index and role.

        Args:
            index (QModelIndex): The index in the model.
            role (Qt.ItemDataRole): The data role.

        Returns:
            Any: The data to display or edit, or a background brush if the cell is empty.
        """
        if role in (qtc.Qt.ItemDataRole.DisplayRole, qtc.Qt.ItemDataRole.EditRole):
           return self._newlist[index.row()][index.column()]
        if role == qtc.Qt.ItemDataRole.BackgroundRole:
           if self._newlist[index.row()][index.column()] == '':
               return qtg.QBrush(qtc.Qt.GlobalColor.red)
        '''removed tool tip role'''
    
    def insertRows(self, row=0, rows=1, index=qtc.QModelIndex(), values=['','']):
        """
        Insert one or more new rows into the model.

        Args:
            row (int): The row position to insert at.
            rows (int): Number of rows to insert.
            index (QModelIndex): Required by Qt, not used.
            values (list[Any]): The values for the new row(s), default is ['', ''].

        Returns:
            bool: True if rows were inserted.
        """
       
        self.beginInsertRows(qtc.QModelIndex(), row, row + rows - 1)
        for row in range(rows):
            self._newlist.insert(row, values)
        self.endInsertRows()
        return True

    def removeRow(self, row=0, index=qtc.QModelIndex(), values=[]):
        """
        Remove a row from the model.

        Args:
            row (int): The row index to remove.
            index (QModelIndex): Required by Qt, not used.
            values (list[Any]): Not used.

        Returns:
            bool: True if the row was removed.
        """
        self.beginRemoveRows(qtc.QModelIndex(), row, row)
        self._newlist.pop(row)        
        self.endRemoveRows()
        return True