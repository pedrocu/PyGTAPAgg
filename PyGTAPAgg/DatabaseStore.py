"""Module handles both the session and file storage of aggrigation parameters.

   All elements including database verison, sectors, regions, endowments and pick lists
   are stored in a JSON file. The database store has the capability to read JSON files with 
   the same paramenters.
   
   Just some tect to test github actions. Another Test.
  
"""

import json
from typing import Any
from PyQt6 import QtCore as qtc
from PyQt6 import QtWidgets as qtw
from modules.HARPY import *

class GtapSets():
    """Reads in all of the gtap sets
     
    The GTAP sets are read in from a .har file to initialize the various tabs for
    sector, and regions.  Note, endowments never change, so we do not need to read these.

    Attributes:
        gtap_sets_sectors:  sectors
        gtap_regions:  regions 
    """
    def __init__(self) -> None:
        self.gtap_sets_sectors=None
        self.gtap_regions=None
        super().__init__() 

    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)
    
    def __setattr__(self, name: str, value: Any) -> None:    
        return super().__setattr__(name, value)

    def readin_gtap_sets(self, dir, header):
        """Read sectors and regions from har file

        The sectors and regions are read in from a .har file and placed in the 
        class attributes for latter use.

         Args:
           Dir:     Directory of the sets file
           header:  The particular set we wiseh to extra from the har file

         Returns: sector and region list in the format [(1, 'USA')] 
                
        """
        InFile=HarFileObj(dir+"\\gsdset.har")
        DataHead=InFile[header]
        npDataArray = [x.strip(' ') for x in DataHead.array.tolist()]  #Need to strip out spaces - HARPY needs fix
        newlist = []
        for pos, var in enumerate(npDataArray):
            newlist.append([pos+1, var])
        return newlist

    

    
class TabData():
    """An object for tab data elements.
     
    Each tab has a similar structure - picker, headers, data.  This class provides a structure
    and methods for storing and retriving that data in a conistent way across tabs.

    Attributes:
        Pick_start:  Picker window
        header:      The lables for sectors, regions 
        data:        Data for the element stored in header order 
    """

    def __init__(self) -> None:
        self.pick_start = None
        self.headers= None
        self.data=None

        super().__init__()

    def make_pick_start(self, agg_store):
        """Method gets picks from datastore.

        This object standardizes the retrival and storage of the tab data from the datastore.

         Args:
            agg_store: the name of the agg store.

         Returns:            
              pick_list
        """

        return agg_store['picks']
    
    def make_headers(self, agg_store):
        """Method gets header from datastore.

        This object standardizes the retrival and storage of the tab data from the datastore.

         Args:
            agg_store: the name of the agg store.

         Returns:            
              headers
        """
        return agg_store['headers']

    def make_data(self, sets, agg_store):
        """Match merge on sets and aggstore abrev

        We want the long description with the codes.  This method zips them together.

         Args:
            agg_store: the name of the agg store.  Agg Store is the JSON file read into a dict.
                       see JSON format below in load_aggstore() 
            sets: The set to be merged [(1,'pdr'), (2, 'wht')...]
         Returns:            
              matched list
        """
        newdict={x[1]: x for x in agg_store['data']}
        matchlist =  [x+newdict.get(x[1], ['','', '','',''])[2:] for x in sets ]
        return matchlist
     
class TabDataEndow(TabData):
       def __init__(self) -> None:
           self.etrae = None
           super().__init__()
        
       def make_etrae(self, agg_store):
           
           etrae = [x for x in agg_store['etrae'] if x[0] in self.pick_start]


           return etrae
           

   
class DataStore(GtapSets,qtw.QWidget):
    """ Maintains all the state of data for all the tabs

        State of data as well as methods for reading and writing data to files.

        Attributes:
            agg_store_file :
            add_store_data :
            sectors :
            regions : 
            endowments :
            gtap_source

    """


    update_tabs=qtc.pyqtSignal(str)

    def __init__(self, agg_store_file=".\data\defaults.json"):
        """
        
        """
        super().__init__()
        
        'This is where the settings for the program are written to persist across sessions'
        qtc.QCoreApplication.setOrganizationName("ImpactECON")
        qtc.QCoreApplication.setOrganizationDomain("impactecon.com")
        qtc.QCoreApplication.setApplicationName("PyGTAPAgg")
        self.settings=qtc.QSettings("ImpactECON","PyGTAPAgg")
        
           
        self.agg_store_file= agg_store_file
        self.agg_store_data=self.load_aggstore(self.agg_store_file)

        self.sectors=TabData()
        self.regions=TabData()
        self.endowments=TabDataEndow()
        
                              
        if self.settings.contains('indir') and self.settings.value('indir') is not None:
            
            self.gtap_source=self.settings.value('indir')
           
        else:
            self.gtap_source = None
            self.sectors.data =    [["", "", "", "", "", "" ]]
            self.regions.data =    [["", "", "", "", "", "" ]]
            self.endowments.data = [["", "", "", "", "", "" ]]
   
    @property
    def gtap_source(self):
        #In practice, this should only be setby the database widget for validity checking
        return self._gtap_source
    
    @gtap_source.setter
    def gtap_source(self, value):
        self._gtap_source=value
        if value != 'NA' and value is not None:
           
           self.gtap_sectors=self.readin_gtap_sets(value, "H2")
           self.gtap_regions=self.readin_gtap_sets(value, "H1")
           self.gtap_endowments=self.readin_gtap_sets(value, "H6")
           #self.gtap_etrae =self.readin_gtap_sets(value, "")
           self.gtap_TARS=[i[1] for i in self.readin_gtap_sets(value, "TARS")]
           self.gtap_TARL=[i[1][0:11] for i in self.readin_gtap_sets(value, "TARL")]  #Problem, HARPY only allows 12 charecter elements
            
           self.sectors.data=self.sectors.make_data(self.gtap_sectors, self.agg_store_data['sectors'])
          
           self.sectors.pick_start=self.sectors.make_pick_start(self.agg_store_data['sectors'])
           self.sectors.headers = self.sectors.make_headers(self.agg_store_data['sectors']) 

           self.regions.data=self.regions.make_data(self.gtap_regions, self.agg_store_data['regions'])
           self.regions.pick_start=self.regions.make_pick_start(self.agg_store_data['regions'])
           self.regions.headers = self.regions.make_headers(self.agg_store_data['regions']) 

           self.endowments.data=self.endowments.make_data(self.gtap_endowments, self.agg_store_data['endowments'])
           self.endowments.pick_start=self.endowments.make_pick_start(self.agg_store_data['endowments'])
           self.endowments.headers = self.endowments.make_headers(self.agg_store_data['endowments']) 

           self.endowments.etrae=self.endowments.make_etrae(self.agg_store_data['endowments'])
           
        else:
            self.gtap_sets=None
            self.sectors.data = [['', '', '', '', '' ]]
            self.sectors.headers = ['pos', 'GTAP Code', 'GTAP Name', 'Long Name', 'Agg Group' ]
            self.sectors.pick_start = ['Agriculture', 'Manufactures', 'Services']
            self.regions.data = [['', '', '', '', '' ]]
            self.regions.headers = ['pos', 'GTAP Code', 'GTAP Name', 'Long Name', 'Agg Group' ]
            self.regions.pick_start = ['NAFTA', 'EU28', 'Other']
            self.endowments.data = [['', '', '', '', '' ]]
            self.endowments.headers = ['pos', 'GTAP Code', 'GTAP Name', 'Long Name', 'Agg Group' ]
            self.endowments.pick_start = ['Skilled', 'UnSkilled', 'Capital', 'NatlRes']
            self.endowments.etrae=[['', '']]
            
   
    @property
    def agg_store_file(self):
        return self._agg_store_file
    
    @agg_store_file.setter
    def agg_store_file(self, value):
        self._agg_store_file=value

    @property
    def agg_store_data(self):
        return self._agg_store_data

    @agg_store_data.setter
    def agg_store_data(self, value):
        self._agg_store_data=value

    def load_default(self, mydefaults):
        with open(mydefaults) as f:
            data=json.load(f)
        self.aggs = data
       
     #slot
    def gtapraw_source(self, value):
        value.replace('/','\\')
        self.gtap_source=value
  
    def load_aggstore(self, file_name):
        """Loads a json file with header, picks and data
        
        A JSON file with the format:

        Sectors {}
        headers: [
            pos,
            GTAP Code,
            GTAP Name,
            Long Description,
            Sort Group,
            Agg Category]
       picks: [
            Agriculture,
            Manufactures,
            Extraction,
            Services    ]
        data: [   [
        1,
        pdr,
        Paddy rice,
        Rice: seed, paddy (not husked),
        Agriculture,
        Agriculture], ...]}

        Regions {}
        
        Args: 
            file_name :  file file name with path

        Returns:
            A dictionary with key value pairs.  Key: sectors, regions, endowments

        Raises:   
        
        """

        with open(file_name) as f:
           aggstore=json.load(f)
           return aggstore
        
    def to_agg_store(self):
        self.agg_store_data={'sectors': {'picks': self.sectors.pick_start , 'headers': self.sectors.headers,  'data': self.sectors.data }, 
                             'regions' : {'picks': self.regions.pick_start , 'headers': self.regions.headers,  'data': self.regions.data },
                             'endowments' : {'picks': self.endowments.pick_start , 'headers': self.endowments.headers,  'data': self.endowments.data , 'etrae' :self.endowments.etrae}}

    def to_json_file(self, filename):
        self.to_agg_store()
        with open(filename, 'w') as f:
                      json.dump(self.agg_store_data,f, ensure_ascii=False, indent=4)

    def load_new_agg_file(self, filename):
        self.agg_store_file = filename        
        self.agg_store_data=self.load_aggstore(filename)
        self.gtap_source=self.gtap_source
        self.update_tabs.emit('')
