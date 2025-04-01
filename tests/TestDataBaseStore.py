import unittest
import PyGTAPAgg.DatabaseStore

class TestGTAPSets(unittest.TestCase):
    #Tests the GTAPSets class (this class is inherited by the database widget, but we can test it seperatly)

    def setUp(self):
        #Opens just the GTAPSets object, which is inherited by the databse store
        self.setcheck = PyGTAPAgg.DatabaseStore.GtapSets()
        self.setcheck.gtap_regions=self.setcheck.readin_gtap_sets(".\Tests\data", "H1")
        self.setcheck.gtap_sets_sectors=self.setcheck.readin_gtap_sets(".\Tests\data", "H2")

    def test_h1_compare_start_end(self):
        #Test read the regions from th sets file
        self.regions_test_start=[[1, "aus"], [2,"nzl"]]
        self.regions_test_end=[[157, "xsc"], [158,"xtw"]]
        self.assertCountEqual(self.regions_test_start, self.setcheck.gtap_regions[0:2], "Set Start regions did not match")
        self.assertCountEqual(self.regions_test_end, self.setcheck.gtap_regions[-2:], "Set End regions did not match")

    def test_h2_compare_start_end(self):
        #Test read sectos from the sets file
        self.sectors_test_start=[[1, "pdr"], [2,"wht"]]
        self.sectors_test_end=[[64, "hht"], [65,"dwe"]]
        self.assertCountEqual(self.sectors_test_start, self.setcheck.gtap_sets_sectors[0:2], "Set Start sectors did not match")
        self.assertCountEqual(self.sectors_test_end, self.setcheck.gtap_sets_sectors[-2:], "Set End sectors did not match")
    
    def tearDown(self):
        return super().tearDown()
    
class TestDatabaseStoreJSON(unittest.TestCase):
    #Test the load json method in DatabaseStore class

    def setUp(self):
        self.setcheck = PyGTAPAgg.DatabaseStore.DataStore()

    def test_h3_read_in_regions_json(self):
        #Test read the regions from the json file
        self.regions_test_headers=['pos', 'GTAP Code', 'GTAP Name', 'Long Description', 'Sort Group', 'Agg Category']
        self.regions_test_picks=['NAFTA', 'EU28', 'Other']
        self.regions_test_data_start=['', 'xac', 'South Central Africa', 'Other', 'South Central A', 'Other']
        self.regions_test_data_end=['', 'zwe', 'Zimbabwe', 'Sub-Saharan Africa', 'SADC', 'Other']
        self.assertEqual(self.regions_test_headers, self.setcheck.agg_store_data['regions']['headers'], "JSON Start region headers did not match")
        self.assertEqual(self.regions_test_picks, self.setcheck.agg_store_data['regions']['picks'], "JSON Start region headers did not match")
        self.assertEqual(self.regions_test_data_start, self.setcheck.agg_store_data['regions']['data'][0], "JSON Start region data did not match")
        self.assertEqual(self.regions_test_data_end, self.setcheck.agg_store_data['regions']['data'][-1], "JSON End region data did not match")

    def test_h4_read_in_sectors_json(self):
        #Test read the sectors from the json file
        self.sectors_test_headers=['pos', 'GTAP Code', 'GTAP Name', 'Long Description', 'Sort Group', 'Agg Category']
        self.sectors_test_picks=['Agriculture', 'Manufactures', 'Extraction', 'Services']
        self.sectors_test_data_start=[1, 'pdr', 'Paddy rice', 'Rice: seed, paddy (not husked)', 'Agriculture', 'Agriculture']
        self.sectors_test_data_end=[65, 'dwe', 'Dwellings', 'Dwellings: ownership of dwellings (imputed rents of houses occupied by owners)', 'Services', 'Services']
        self.assertEqual(self.sectors_test_headers, self.setcheck.agg_store_data['sectors']['headers'], "JSON Start region headers did not match")
        self.assertEqual(self.sectors_test_picks, self.setcheck.agg_store_data['sectors']['picks'], "JSON Start region headers did not match")
        self.assertEqual(self.sectors_test_data_start, self.setcheck.agg_store_data['sectors']['data'][0], "JSON Start region data did not match")
        self.assertEqual(self.sectors_test_data_end, self.setcheck.agg_store_data['sectors']['data'][-1], "JSON End region data did not match")

    def test_h5_read_in_endowments_json(self):
        #Test read the sectors from the json file
        self.endow_test_headers=['pos', 'GTAP Code', 'Short Name', 'Long Description', 'Agg Category']
        self.endow_test_picks=['Skilled', 'Unskilled', 'Capital', 'Land', 'NatlRes']
        self.endow_test_data_start=['2', 'off_mgr_pros', 'Managers and professionals', 'Managers, senior officials and Legislators (Major Groups 1), and professionals (Major Group 2)', 'Skilled']
        self.endow_test_data_end=['', 'Unskilled', 'Unskilled labor', 'Skilled labor', 'Unskilled']
        self.assertEqual(self.endow_test_headers, self.setcheck.agg_store_data['endowments']['headers'], "JSON Start region headers did not match")
        self.assertEqual(self.endow_test_picks, self.setcheck.agg_store_data['endowments']['picks'], "JSON Start region headers did not match")
        self.assertEqual(self.endow_test_data_start, self.setcheck.agg_store_data['endowments']['data'][0], "JSON Start region data did not match")
        self.assertEqual(self.endow_test_data_end, self.setcheck.agg_store_data['endowments']['data'][-1], "JSON End region data did not match")


    def tearDown(self):
        return super().tearDown()
    
class TestDatabaseStoreTabDefault(unittest.TestCase):
    #Test the load json method in DatabaseStore class

    def setUp(self):
        self.setcheck = PyGTAPAgg.DatabaseStore.DataStore()
        self.setcheck.gtap_source="NA"

    def test_h6_check_tab_default_blank(self):
        self.sectors_test_headers=[["", "", "", "", "" ]]
        self.assertEqual(self.sectors_test_headers, self.setcheck.sectors.data, "JSON Start region headers did not match")
        


    def tearDown(self):
        return super().tearDown()
        


if __name__ == '__main__':
    unittest.main()