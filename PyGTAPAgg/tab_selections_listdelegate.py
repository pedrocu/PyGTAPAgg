from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc

class ListDelegate(qtw.QStyledItemDelegate):
    """
    Custom delegate for editing table cells with a picker list.

    This delegate provides a QListView editor for table cells, allowing users to select
    an item from a provided picker model (typically a QStringListModel). It is used to
    enable right-click context menus or standard editing for selection columns in
    aggregation tables.

    Args:
        picker_model (QAbstractListModel): The model containing selectable items.

    Attributes:
        picker_model (QAbstractListModel): The model used to populate the editor.
        height (int): The height of each item in the editor (default: 25).
        width (int): The width of the editor widget (default: 200).
    """
    def __init__(self, picker_model):
        """
        Initialize the ListDelegate.

        Args:
            picker_model (QAbstractListModel): The model containing selectable items.
        """
        super().__init__()
        self.picker_model=picker_model

    height = 25
    width = 200
    
    def createEditor(self, parent, option, index):
        """
        Create the QListView editor for the cell.

        Args:
            parent (QWidget): The parent widget.
            option (QStyleOptionViewItem): The style options for the item.
            index (QModelIndex): The index of the item being edited.

        Returns:
            QListView: The editor widget.
        """
        
        editor = qtw.QListView(parent)
        
        editor.setSelectionMode(qtw.QAbstractItemView.SelectionMode.SingleSelection)
        editor.setModel(self.picker_model)
       
        editor.clicked.connect(self.current_item_changed)
        return editor

    def setEditorData(self,editor,index):
        """
        Set the geometry for the editor widget based on the row and picker model size.

        Args:
            editor (QListView): The editor widget.
            index (QModelIndex): The index of the item being edited.
        """
        editor.setGeometry(0,index.row(),self.width,self.height*self.picker_model.rowCount())

    def setModelData(self, editor, model, index):
        """
        Update the model with the selected value from the editor.

        Args:
            editor (QListView): The editor widget.
            model (QAbstractItemModel): The model being edited.
            index (QModelIndex): The index of the item being edited.
        """
        #setup editor to do multiselection
        for item in editor.selectedIndexes():
            text=self.picker_model.data(item,0)        
            model.setData(index, text, qtc.Qt.ItemDataRole.EditRole)
        editor.close()
    
    def current_item_changed(self, current):
        """
        Emit the commitData signal when the selection changes in the editor.

        Args:
            current (QModelIndex): The currently selected index in the editor.
        """
        self.commitData.emit(self.sender())
    # Methods for inserting deleting
        #None expected
    #Methods for saving data
        #TBD



