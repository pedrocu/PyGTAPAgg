
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
import json


class ItemTableModel(qtc.QAbstractTableModel):
    """
    Model for the aggregation table used in the selection interface.

    This model manages tabular data for sectors, regions, or endowments in the
    right-hand tile of the selection UI. It supports sorting, editing, and
    custom display roles for integration with PyQt6's model/view framework.

    Attributes:
        _headers (list[str]): The column headers for the table.
        _newlist (list[list[Any]]): The data for each row in the table.

    Args:
        tab_type (str): The type of aggregation (e.g., 'Sectors', 'Regions', etc.).
        headers (list[str]): The column headers for the table.
        data (list[list[Any]]): The initial data for the table.
    """

    def __init__(self, tab_type, headers, data):
        """
        Initialize the ItemTableModel.

        Args:
            tab_type (str): The type of aggregation.
            headers (list[str]): The column headers for the table.
            data (list[list[Any]]): The initial data for the table.
        """
        super().__init__()
        self.start(tab_type, headers, data)
        
    def start(self, tab_type, headers, data):
        """
        Set up the model with headers and data.

        Args:
            tab_type (str): The type of aggregation.
            headers (list[str]): The column headers for the table.
            data (list[list[Any]]): The initial data for the table.
        """
        self._headers=headers             
        self._newlist = data

    @property
    def headers(self):
        """
        list[str]: The column headers for the table.
        """
        return self._headers

    @property
    def newlist(self):
        """
        list[list[Any]]: The data for each row in the table.
        """
        return self._newlist
    
    @headers.setter
    def headers(self,x):
        """
        Set the column headers for the table.

        Args:
            x (list[str]): The new headers.
        """
        self._headers=x

    def load(self, tab_type):
        """
        Load table data from a JSON file.

        Args:
            tab_type (str): The type of aggregation (used as filename).

        Returns:
            list[list[Any]]: The loaded data.
        """
        with open(tab_type + '.json') as f:
            data=json.load(f)
        return data
    
    #Required for QTableModel
    def rowCount(self, parent):
        """
        Get the number of rows in the model.

        Args:
            parent (QModelIndex): Required by Qt, not used.

        Returns:
            int: Number of rows.
        """
        return len(self._newlist or [])

    #Required for QTableModel
    def columnCount(self, parent):
        #print('number of colums ', len(self._headers))
        return len(self._headers or [])
    
    #Required for QTAbleModel
    def data(self, index, role):
        """
        Get the number of columns in the model.

        Args:
            parent (QModelIndex): Required by Qt, not used.

        Returns:
            int: Number of columns.
        """
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
        """
        Return data for a given index and role.

        Args:
            index (QModelIndex): The index of the data.
            role (Qt.ItemDataRole): The role for which data is requested.

        Returns:
            Any: The data for the given role and index.
        """

        if orientation == qtc.Qt.Orientation.Horizontal and role == qtc.Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        
        else:
            return super().headerData(section, orientation, role)

    def sort(self, column, order):
        """
        Sort the table by a given column.

        Args:
            column (int): The column index to sort by.
            order (Qt.SortOrder): The sort order (ascending/descending).
        """
        if self._newlist !=None:
            self.layoutAboutToBeChanged.emit()  # needs to be emitted before a sort
            self._newlist = sorted(self._newlist, key=lambda k: k[column]) 
            if order == qtc.Qt.SortOrder.DescendingOrder:
                self._newlist.reverse()
            self.layoutChanged.emit()  # needs to be emitted after a sort

    # Methods for Read/Write

    def flags(self, index):
        """
        Return the item flags for a given index.

        Args:
            index (QModelIndex): The index to return flags for.

        Returns:
            Qt.ItemFlags: The item flags.
        """

        if index.column() == self.columnCount(None)-1:
            return super().flags(index) | qtc.Qt.ItemFlag.ItemIsEditable
        else:
            return super().flags(index)
    
    #Qt Required to edit data
    def setData(self, index, value, role):
        """
        Set the data for a given index and role.

        Args:
            index (QModelIndex): The index to set.
            value (Any): The new value.
            role (Qt.ItemDataRole): The role for which data is being set.

        Returns:
            bool: True if the data was set, False otherwise.
        """
        if index.isValid():
            if role == qtc.Qt.ItemDataRole.EditRole and index.column()==self.columnCount(None)-1:
                self._newlist[index.row()][index.column()] = value
                self.dataChanged.emit(index, index, [qtc.Qt.ItemDataRole.DisplayRole, qtc.Qt.ItemDataRole.EditRole, qtc.Qt.ItemDataRole.BackgroundRole])
                return True
        else:
            return False