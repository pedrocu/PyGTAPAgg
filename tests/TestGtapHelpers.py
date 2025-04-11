import unittest
from PyGTAPAgg.GtapHelpers import getdbversize, getvalues
from PyQt6.QtCore import QSettings, Qt
from  PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QListView
from modules.HARPY import har_file  # Import HARPY module
import tempfile
import os

class TestGtapHelpers(unittest.TestCase):
    
    def test_getdbversize_success(self):
        #gtap = self.gtap_dir
        source = "dummy_source"
        gtap = r".\tests\data"
        # Call the function
        result = getdbversize(gtap, source)
        
        # Validate results
        expected_version = ('v11p3', 'Y2017', 'Jun_2022')
        expected_regions = 158  # 158 regions in H1
        expected_sectors = 65  # 65 sectors in H2
        expected_endowments = 8  # 8 endowment in H6
        
        self.assertIsInstance(result, list)
        self.assertEqual(result[0], gtap)  # Directory
        self.assertEqual(result[1], expected_version)
        self.assertEqual(result[2], expected_regions)
        self.assertEqual(result[3], expected_sectors)
        self.assertEqual(result[4], expected_endowments)

    def test_getdbversize_failure(self):
        # Provide a non-existent directory
        gtap = "/non_existent_directory"
        source = "dummy_source"
        
        # Call the function
        result = getdbversize(gtap, source)

        # Validate that it falls back to default values
        self.assertIsInstance(result, list)
        self.assertEqual(result[1], ('NA', 'NA', 'NA'))  # Default version
        self.assertEqual(result[2], 'NA')  # Default regions
        self.assertEqual(result[3], 'NA')  # Default sectors
        self.assertEqual(result[4], 'NA')  # Default endowments
        
    def test_getvalues(self):
        # Set up QApplication instance
        #app = QApplication([])
        
        # Create a dummy model with test data
        model = QStandardItemModel()
        items = ["Item1", "Item2", "Item3"]
        for item in items:
            model.appendRow(QStandardItem(item))

        # Create a dummy selection list
        selection_list = [model.index(i, 0) for i in range(len(items))]

        # Simulate a "self" object with the picker model
        class DummySelf:
            def __init__(self, model):
                self._picker_model = model

        dummy_self = DummySelf(model)

        # Call the function and validate the output
        result = getvalues(dummy_self, selection_list)
        self.assertEqual(result, items)
        

if __name__ == '__main__':
    unittest.main()