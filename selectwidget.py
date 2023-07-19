import sys
import csv
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
import json

import GtapHelpers as helpers

class Select(qtw.QWidget):
    """Select sectors, regions, endowment
       Args: 
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
        
        #if tab_type in ('Endowments'): self.tableview.setColumnHidden(2,True)

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
        #Connect the right click to openmenu

        #self.show()

        #Can add with a subclass addtional items to this tab widget
        #self.layout_v1.addWidget(qtw.QTextEdit())
    
    # @property
    # def pick_start(self):
    #     return self._pick_start
    
    # @pick_start.setter
    # def pick_start(self, x):
    #     self._pick_start=x

        print('data address', id(self._data))   

    def prioritem(self, index):
        '''gets item before edit so it can be used for changing table data'''
        
        self.before_edit=self._picker_model.data(index, qtc.Qt.ItemDataRole.DisplayRole)
        
    def openMenu(self, position):
        '''The list of items to pick from with right click - context menu'''
        
        self.editor = qtw.QListView()
        self.editor.setWindowFlags(qtc.Qt.WindowType.WindowStaysOnTopHint)
        self.editor.setSelectionMode(qtw.QAbstractItemView.SelectionMode.MultiSelection)
        self.editor.setModel(self._picker_model)
        #self.editor.setWindowFlags(qtc.Qt.FramelessWindowHint)

        self.editor.setGeometry(400, 100, 100, 100)
        
        self.editor.clicked.connect(self.changemyselection)

        self.editor.show()
        
    def changemyselection(self, item):
        '''based on item selected with right click context menu fills the selection'''
        #list item retrieve text
        text=self._picker_model.data(item,0)        
       
        #Retrieve selction model
        self.myselection = self.tableview.selectionModel()
        indexes= self.myselection.selectedIndexes()

        #Change selection to list pick        
        for i in indexes:
            self.model.setData(i, text, qtc.Qt.ItemDataRole.EditRole)
            
        self.editor.close()
  
    def onetone(self):
        '''changes regions/sectors/endowments to one-to-one'''
        for i in range(0, self._model.rowCount(None)):
            abbrev_index=self._model.index(i,1)
            item_index=self._model.index(i,self._model.columnCount(None)-1)
            self._model.setData(item_index,self._model.data(abbrev_index, qtc.Qt.ItemDataRole.DisplayRole),qtc.Qt.ItemDataRole.EditRole )
    
    def newitem(self):
        '''dialgoue to add new item to list'''

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
        '''logic to add item to edit list see newitem() for dialgoue'''
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
        '''when a item is changed in the list, it is changed in the table'''
        
        for i in range(0, self._model.rowCount(None)):
            item_index=self._model.index(i,self._model.columnCount(None)-1)
            if self._model.data(item_index, qtc.Qt.ItemDataRole.DisplayRole) == self.before_edit:
                self._model.setData(item_index,self._picker_model.data(index, qtc.Qt.ItemDataRole.DisplayRole),qtc.Qt.ItemDataRole.EditRole )

    def remove(self):
        '''remove item in list and from associated table/s'''
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
        '''clears the picker list and associted table entries'''
        num_rows=self._picker_model.rowCount()

        self._picker_model.removeRows(0,num_rows)
        for i in range(0, self._model.rowCount(None)):
            item_index=self._model.index(i,self._model.columnCount(None)-1)
            self._model.setData(item_index,'',qtc.Qt.ItemDataRole.EditRole )

    def checkdup(self):
        '''checks for duplicates before adding or changing picklist'''
        #TBD
        return 0
    

       
    # def updatedata(self):
    #     #self.picker_model = qtc.QStringListModel(self._data_store.sector_pick_start)
        
        
    #     self._pick_start=pick_start
    #     self._headers=headers
    #     self._data=data



    #     self._model=ItemTableModel(self._tab_type, self._data_store._sector_header, self._data_store.sector_all)
    #     self._picker_model.setStringList(self._data_store.sector_pick_start)
    #     self.tableview.setModel(self._model)
        
    #     print('data store')
    #     print(id(self._data_store))

    #     print('DATA')
    #     print('from datastore', id(self._data_store._sector_all))
    #     print('from data', id(self._data))

      
    #     self.tableview.setColumnHidden(0,True)

    
    
    
class ItemTableModel(qtc.QAbstractTableModel):
    """The model for aggregation table"""

    def __init__(self, tab_type, headers, data):
        super().__init__()
        self.start(tab_type, headers, data)
        
    def start(self, tab_type, headers, data):
        ''''__init__ code'''
        self._headers=headers             
        self._newlist = data    
        
        #data=self.load(tab_type)
        

        #for item in data:
        #    self._newlist.append(list(item.values()))
        #    print(self._newlist)
        
       # Minimum necessary methods:
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
        #print(self._newlist)
        #print('number of rows ', len(self._newlist))
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

class ListDelegate(qtw.QStyledItemDelegate):
    '''Custom List Delegate'''
    def __init__(self, picker_model):
        super().__init__()
        self.picker_model=picker_model

    height = 25
    width = 200
    
    def createEditor(self, parent, option, index):
        
        editor = qtw.QListView(parent)
        
        editor.setSelectionMode(qtw.QAbstractItemView.SelectionMode.SingleSelection)
        editor.setModel(self.picker_model)
       
        editor.clicked.connect(self.current_item_changed)
        return editor

    def setEditorData(self,editor,index):
        #z = 0
        #for item in self.editorItems:
        #    ai = qtw.QListWidgetItem(item)
            #editor.addItem(ai)
        #    if item == index):
        #        editor.setCurrentItem(editor.item(z))
        #    z += 1
        editor.setGeometry(0,index.row(),self.width,self.height*self.picker_model.rowCount())

    def setModelData(self, editor, model, index):
        #setup editor to do multiselection
        for item in editor.selectedIndexes():
            text=self.picker_model.data(item,0)        
            model.setData(index, text, qtc.Qt.ItemDataRole.EditRole)
        editor.close()
    
    def current_item_changed(self, current):
        self.commitData.emit(self.sender())
    # Methods for inserting deleting
        #None expected
    #Methods for saving data
        #TBD