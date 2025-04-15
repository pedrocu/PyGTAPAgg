import unittest
import sys

import PyQt6.QtWidgets as qtw
from PyQt6 import QtWidgets as qtw


from PyGTAPAgg import MainWindow as MainWindow


app = qtw.QApplication(sys.argv)

class TestdbTab(unittest.TestCase):

    def setUp(self):
         my_screen=app.primaryScreen().geometry()
         self.form = MainWindow.MainWindow(my_screen)

    def test_2_choose_db_lables_read(self):
        self.form.gtap_central_widget.databases.getgtapdir(r".\\tests\\data")
        self.assertEqual(self.form.gtap_central_widget.databases.version_label0.text(), r".\\tests\\data", "Wrong Direcotry displayed")
        self.assertEqual(self.form.gtap_central_widget.databases.version_label2.text(), "v11p3", "Wrong version, experected v11p3")
        self.assertEqual(self.form.gtap_central_widget.databases.version_label3.text(), "Y2017", "Year of Data")
        self.assertEqual(self.form.gtap_central_widget.databases.version_label4.text(), "Jun_2022", "Release Date")
        self.assertEqual(self.form.gtap_central_widget.databases.version_label5.text(), "158", "Wrong number of regions")
        self.assertEqual(self.form.gtap_central_widget.databases.version_label6.text(), "65", "Wrong number of sectors")
        self.assertEqual(self.form.gtap_central_widget.databases.version_label7.text(), "8", "Wrong number of endowments")

    def tearDown(self):
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()