import unittest
import PyGTAPAgg.DatabaseStore

class TestSetTab(unittest.TestCase):

    def setUp(self):
        self.setcheck = PyGTAPAgg.DatabaseStore.GtapSets()
        self.setcheck.gtap_regions=self.setcheck.readin_gtap_sets(".\Tests\data", "H1")
        self.setcheck.gtap_sets_sectors=self.setcheck.readin_gtap_sets(".\Tests\data", "H2")

    def test_h1_compare_start_end(self):

        self.regions_test_start=[(1, "aus"), (2,"nzl")]
        self.regions_test_end=[(157, "xsc"), (158,"xtw")]
        self.assertCountEqual(self.regions_test_start, self.setcheck.gtap_regions[0:2], "Start regions did not match")
        self.assertCountEqual(self.regions_test_end, self.setcheck.gtap_regions[-2:], "End regions did not match")

    def test_h2_compare_start_end(self):

        self.sectors_test_start=[(1, "pdr"), (2,"wht")]
        self.sectors_test_end=[(64, "hht"), (65,"dwe")]
        self.assertCountEqual(self.sectors_test_start, self.setcheck.gtap_sets_sectors[0:2], "Start sectors did not match")
        self.assertCountEqual(self.sectors_test_end, self.setcheck.gtap_sets_sectors[-2:], "End sectors did not match")



    def tearDown(self):
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()