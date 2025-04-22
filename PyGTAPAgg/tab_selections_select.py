from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
import json

from PyGTAPAgg import GtapHelpers as helpers
from PyGTAPAgg.tab_selections_itemtablemodel import ItemTableModel
from PyGTAPAgg.tab_selections_listdelegate import ListDelegate
from PyGTAPAgg.tab_selections_endowmentparameter import EndowmentParameter

class Select(qtw.QWidget):
    """
    Widget for selecting and managing lists of sectors, regions, or endowments.

    Provides an interface for users to:
      - Add, remove, or clear items from a selection list (picker).
      - Edit selections and propagate changes to an associated table.
      - Use context menus and delegates for flexible editing.

    Args:
        tab_type (str): The type of aggregation (e.g., 'Sectors', 'Regions', etc.).
        data_store (Any): Data store object for persistence or data access.
        pick_start (list[str]): Initial list of items for the picker.
        headers (list[str]): Column headers for the main table.
        data (list[list[Any]]): Data for the main table.

    Attributes:
        _tab_type (str): Type of aggregation.
        _data_store (Any): Data store reference.
        _pick_start (list[str]): Initial picker items.
        _headers (list[str]): Table headers.
        _data (list[list[Any]]): Table data.
        _model (ItemTableModel): Model for the main table.
        _picker_model (qtc.QStringListModel): Model for picker list.
        tableview (qtw.QTableView): Main table view.
        picker_view (qtw.QListView): Picker list view.
        before_edit (str): Stores item value before editing.
        delegate (ListDelegate): Delegate for custom editing.
        one_to_one_button (qtw.QPushButton): Button to set one-to-one mapping.
        add_button (qtw.QPushButton): Button to add new item.
        remove_button (qtw.QPushButton): Button to remove selected item(s).
        clear_button (qtw.QPushButton): Button to clear all items.
        select_box (qtw.QGroupBox): Group box containing the main table.
    """
    def __init__(self, tab_type, data_store, pick_start, headers, data):

        super().__init__()
        
        self._tab_type=tab_type
        self._data_store=data_store
        self._pick_start=pick_start
        self._headers=headers
        self._data=data
        self._model=ItemTableModel(tab_type, self._headers, self._data)
        self._picker_model = qtc.QStringListModel(self._pick_start)

        self.tableview = qtw.QTableView()
        self.tableview.setModel(self._model)
    
        #layout  
        self.layout_h=qtw.QHBoxLayout()
        self.widget1=qtw.QWidget()
        self.widget2=qtw.QWidget()
        self.layout_v1 = qtw.QVBoxLayout()
        self.layout_v2 = qtw.QVBoxLayout()
        self.widget1.setLayout(self.layout_v1)
        self.widget2.setLayout(self.layout_v2)

        #Add vertical boxes to initial horizaontals
        self.layout_h.addWidget(self.widget1)
        self.layout_h.addWidget(self.widget2)

        #add the vertical with horizontals
        self.setLayout(self.layout_h)
        
        #LEFT side - buttons
        self.one_to_one_button = qtw.QPushButton('One-to-One', self)
        self.layout_v1.addWidget(self.one_to_one_button)

        #groupbox
        mod_item_layout = qtw.QGroupBox(tab_type)
        mod_item_layout.setLayout(qtw.QVBoxLayout())
              
        widget3=qtw.QWidget()
        widget3.setLayout(qtw.QHBoxLayout())
        mod_item_layout.layout().addWidget(widget3)
        
        self.add_button = qtw.QPushButton('Add', self)
        self.remove_button = qtw.QPushButton('Remove', self)
        self.clear_button = qtw.QPushButton('Clear All', self)

        widget3.layout().addWidget(self.add_button)
        widget3.layout().addWidget(self.remove_button)
        widget3.layout().addWidget(self.clear_button)
        
        #picker
        self.picker_view = qtw.QListView()
        self.picker_view.setModel(self._picker_model)
        self.picker_view.setSelectionMode(qtw.QAbstractItemView.SelectionMode.MultiSelection)
        self.picker_view.setDragDropMode(qtw.QAbstractItemView.DragDropMode.InternalMove)
        self.picker_view.doubleClicked.connect(self.prioritem)
        self.before_edit = ''
        
        mod_item_layout.layout().addWidget(self.picker_view)

        self.layout_v1.addWidget(mod_item_layout)

        #connections
        self.one_to_one_button.clicked.connect(self.onetone)
        self.add_button.clicked.connect(self.newitem)
        self.remove_button.clicked.connect(self.remove)
        self.clear_button.clicked.connect(self.clearall)
        self._picker_model.dataChanged.connect(self.edititem)
        
        #RIGHT side - table
        
        self.tableview.setSortingEnabled(True)
        self.setGeometry(200, 200, 600, 600)
        
        #Hide GEMPACK position number
        self.tableview.setColumnHidden(0,True)
        #Hide long description sectors
        
        style_sheet=("""QHeaderView::section {background-color:rgb(215, 214, 213)}
                        QTableCornerButton::section { background-color:rgb(215, 214, 213)}""")

        self.tableview.setStyleSheet(style_sheet)
        table_header_h=self.tableview.horizontalHeader()
        table_header_h.setSectionsMovable(1)
        
        self.set_Selection = self.tableview.selectionModel()
        
        self.select_box = qtw.QGroupBox('Aggregation')
        self.select_box.setLayout(qtw.QVBoxLayout())

        self.select_box.layout().addWidget(self.tableview)
        self.layout_v2.addWidget(self.select_box)
        
        #Delgate for standard editing
        self.delegate = ListDelegate(self._picker_model)
        self.tableview.setItemDelegateForColumn(self._model.columnCount(None)-1,self.delegate)

        #Set contextmenu (right click)
        self.tableview.setContextMenuPolicy(qtc.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableview.customContextMenuRequested.connect(self.openMenu)
                
    def prioritem(self, index):
        """
        Store the item value before editing for later reference.

        Args:
            index (QModelIndex): Index of the item to be edited.
        """
        
        self.before_edit=self._picker_model.data(index, qtc.Qt.ItemDataRole.DisplayRole)
        
    def openMenu(self, position):
        """
        Open a context menu for selecting items via right-click.

        Args:
            position (QPoint): Position where the menu is requested.
        """
        
        self.editor = qtw.QListView()
        self.editor.setWindowFlags(qtc.Qt.WindowType.WindowStaysOnTopHint)
        self.editor.setSelectionMode(qtw.QAbstractItemView.SelectionMode.MultiSelection)
        self.editor.setModel(self._picker_model)
        #self.editor.setWindowFlags(qtc.Qt.FramelessWindowHint)

        self.editor.setGeometry(400, 100, 100, 100)
        
        self.editor.clicked.connect(self.changemyselection)

        self.editor.show()
        
    def changemyselection(self, item):
        """
        Update the selection in the table based on context menu choice.

        Args:
            item (QModelIndex): Selected item from the context menu.
        """
        #list item retrieve text
        text=self._picker_model.data(item,0)        
       
        #Retrieve selction model
        self.myselection = self.tableview.selectionModel()
        indexes= self.myselection.selectedIndexes()

        #Change selection to list pick        
        for i in indexes:
            self._model.setData(i, text, qtc.Qt.ItemDataRole.EditRole)
            
        self.editor.close()
  
    def onetone(self):
        """
        Set all entries in the table to a one-to-one mapping with their abbreviations.
        """
        for i in range(0, self._model.rowCount(None)):
            abbrev_index=self._model.index(i,1)
            item_index=self._model.index(i,self._model.columnCount(None)-1)
            self._model.setData(item_index,self._model.data(abbrev_index, qtc.Qt.ItemDataRole.DisplayRole),qtc.Qt.ItemDataRole.EditRole )
    
    def newitem(self):
        """
        Open a dialog to add a new item to the picker list.
        """

        self.dialog_add = qtw.QWidget(modal=False)
        self.dialog_add.setWindowFlags(qtc.Qt.WindowType.WindowStaysOnTopHint)

        self.line_edit = qtw.QLineEdit('', 
                                self,
                                placeholderText='New Entry', 
                                clearButtonEnabled=True, 
                                maxLength=20)
        self.line_edit.show()
        self.line_edit.returnPressed.connect(self.additem) 

        edit_buttons=qtw.QDialogButtonBox()
        edit_add = qtw.QPushButton('Add', clicked=self.additem)
        edit_close = qtw.QPushButton('Close', clicked=self.dialog_add.close)
        
        edit_buttons.addButton(edit_close, qtw.QDialogButtonBox.ButtonRole.DestructiveRole)
        edit_buttons.addButton(edit_add, qtw.QDialogButtonBox.ButtonRole.ActionRole)
     
        vlayout = qtw.QVBoxLayout()
        vlayout.addWidget(self.line_edit)
        vlayout.addWidget(edit_buttons)

        self.dialog_add.setLayout(vlayout)
        self.dialog_add.show()

    def additem(self):
        """
        Add the new item from the dialog to the picker list and update the model.
        """
        num_rows=self._picker_model.rowCount()
        self.line_edit_text = [self.line_edit.text()]

        selection = self.picker_view.selectionModel()
        self.selected_indexes=selection.selectedIndexes()

        if len(self.selected_indexes) ==0: 
            self.selected_indexes=[self._picker_model.index(num_rows-1)]
        if num_rows == 0:
           self._picker_model.setStringList(self.line_edit_text) 
                
        self._picker_model.insertRows(self.selected_indexes[0].row(),1)
        self.newthing = self._picker_model.index(self.selected_indexes[0].row())
        self._picker_model.setData(self.newthing, self.line_edit.text(), qtc.Qt.ItemDataRole.EditRole)
    
    def edititem(self, index):     
        """
        Propagate changes in the picker list to the associated table.

        Args:
            index (QModelIndex): Index of the edited item.
        """
        
        for i in range(0, self._model.rowCount(None)):
            item_index=self._model.index(i,self._model.columnCount(None)-1)
            if self._model.data(item_index, qtc.Qt.ItemDataRole.DisplayRole) == self.before_edit:
                self._model.setData(item_index,self._picker_model.data(index, qtc.Qt.ItemDataRole.DisplayRole),qtc.Qt.ItemDataRole.EditRole )

    def remove(self):
        """
        Remove selected items from the picker list and clear them in the table.
        """
        self.selection=self.picker_view.selectionModel()
        self.selected_indexes=self.selection.selectedIndexes()
        self.selected_indexes = sorted(self.selected_indexes, key=lambda k: k.row(), reverse=True) 

        self.values=helpers.getvalues(self, self.selected_indexes)
       
        if len(self.values) == 0:
            return

        'remove from picker'
        for item in self.selected_indexes:
            self._picker_model.removeRow(item.row())
            

        'remove from main table'       
        for item in self.values:
            for i in range(0, self._model.rowCount(None)):
                item_index=self._model.index(i,self._model.columnCount(None)-1)
                if self._model.data(item_index, qtc.Qt.ItemDataRole.DisplayRole) == item:
                    #self.model.data(item_index,qtc.Qt.BackgroundRole)
                    self._model.setData(item_index,'',qtc.Qt.ItemDataRole.EditRole)
        
        'see EndowSelect for subclass on endowments'

    def clearall(self):
        """
        Clear all items from the picker list and associated table entries.
        """
        num_rows=self._picker_model.rowCount()

        self._picker_model.removeRows(0,num_rows)
        for i in range(0, self._model.rowCount(None)):
            item_index=self._model.index(i,self._model.columnCount(None)-1)
            self._model.setData(item_index,'',qtc.Qt.ItemDataRole.EditRole )

    def checkdup(self):
        """
        Check for duplicates before adding or changing the picker list.

        Returns:
            int: 0 if no duplicates found (stub).
        """
        #TBD
        return 0
    
class EndowmentSelect(Select):
    """
    Specialized Select widget for endowments, with additional parameter management.

    Extends:
        Select

    Args:
        tab_type (str): The type of aggregation.
        data_store (Any): Data store object.
        pick_start (list[str]): Initial picker items.
        headers (list[str]): Table headers.
        data (list[list[Any]]): Table data.
        etrae (list[list[Any]]): Endowment parameters.

    Attributes:
        parameter_model (EndowmentParameter): Model for endowment parameters.
        parameter_view (qtw.QTableView): Table view for parameters.
        param_box (qtw.QGroupBox): Group box for parameter table.
    """

    def __init__(self,tab_type, data_store, pick_start, headers, data, etrae):
        super().__init__(tab_type, data_store, pick_start, headers, data)
        
        self.parameter_model = EndowmentParameter(etrae)

        
        self.parameter_view = qtw.QTableView()
        self.tableview.setSortingEnabled(True)

        self.parameter_view.setModel(self.parameter_model)

        self.param_box = qtw.QGroupBox('Parameters')
        self.param_box.setLayout(qtw.QVBoxLayout())

        self.param_box.layout().addWidget(self.parameter_view)
        self.layout_v1.addWidget(self.param_box)
        
        style_sheet=("""QHeaderView::section {background-color:rgb(215, 214, 213)}
                        QTableCornerButton::section { background-color:rgb(215, 214, 213)}""")

        self.parameter_view.setStyleSheet(style_sheet)

    def additem(self):
        """
        Add a new item to both the picker list and the parameter model.
        """
        super().additem()
        self.line_edit_text.append('')
        self.parameter_model.insertRows(values=self.line_edit_text)
    
    def remove(self):
        """
        Remove selected items from both the main table and the parameter list.
        """
        super().remove()
        for item in self.values:
            for counter, endow in enumerate(self.parameter_model._newlist):
                if item == endow[0]: 
                    to_remove_index=counter
                    self.parameter_model.removeRow(row=to_remove_index)

    def onetone(self):
        """
        Synchronize one-to-one mapping between main table and parameter list.
        """
        super().onetone()
        all_main = set()
        all_para = set()
        
        for i in range(0, self._model.rowCount(None)):
            abbrev_index=self._model.index(i,1)
            all_main.add(self._model.data(abbrev_index, qtc.Qt.ItemDataRole.DisplayRole))

        for j in range(0, self.parameter_model.rowCount(None)):
            abbrev_index=self.parameter_model.index(j,0)
            all_para.add(self.parameter_model.data(abbrev_index, qtc.Qt.ItemDataRole.DisplayRole))

        'preserve any existing parameters'
        items_to_add = all_main.difference(all_para)
        items_to_remove = all_para.difference(all_main)
        
        for item in items_to_remove:
            for counter, endow in enumerate(self.parameter_model._newlist):
                if item == endow[0]: 
                    to_remove_index=counter
                    self.parameter_model.removeRow(row=to_remove_index)
        
        for item in items_to_add:
            self.line_edit_text=[item, '']
            self.parameter_model.insertRows(values=self.line_edit_text)

    def clearall(self):
        """
        Clear all items from both the picker list and the parameter list.
        """
        super().clearall()
        for counter in range(0,self.parameter_model.rowCount(None)):
            self.parameter_model.removeRow(row=0)