import unittest
import sys
from PyQt6.QtTest import QTest
import PyQt6.QtWidgets as qtw
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc 
from PyQt6 import QtGui as qtg

from PyGTAPAgg import MainWindow as MainWindow
#from PyGTAPAgg import DatabaseWidget as dbwidget
#from PyGTAPAgg import selectwidget as slwidget
#from PyGTAPAgg import DatabaseStore as store
#from PyGTAPAgg import outputwidget as outwidget


app = qtw.QApplication(sys.argv)

class TestSetTab(unittest.TestCase):

    def setUp(self):
         my_screen=app.primaryScreen().geometry()
         self.form = MainWindow.MainWindow(my_screen)
    
    def test_tet(self):
        self.assertEqual(3,3, 'Not equal')

    def test_empty(self):
        self.assertEqual(self.form.gtap_central_widget.databases.version_label1.text(), 'NA', "default Databse Text not as expected")
        


    def tearDown(self):
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()