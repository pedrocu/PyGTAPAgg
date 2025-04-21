from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc

class ListDelegate(qtw.QStyledItemDelegate):
    '''Custom List Delegate - to make the mouse right click menu'''
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



