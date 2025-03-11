import unittest
import sys
from PyQt6.QtTest import QTest
import PyQt6.QtWidgets as qtw
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc 
from PyQt6 import QtGui as qtg

from PyGTAPAgg import MainWindow as MainWindow


app = qtw.QApplication(sys.argv)

class TestdbTab(unittest.TestCase):

    def setUp(self):
         my_screen=app.primaryScreen().geometry()
         self.form = MainWindow.MainWindow(my_screen)
    
    def test_1_default_labels(self):
        self.assertEqual(self.form.gtap_central_widget.databases.version_label1.text(), 'NA', "Default Databse Text not as expected")
        self.assertEqual(self.form.gtap_central_widget.databases.version_label2.text(), 'NA', "Default Databse Text not as expected")

    

    def tearDown(self):
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()