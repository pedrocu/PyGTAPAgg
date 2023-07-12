import json
from harpy import *


class DataStore():
    def __init__(self, gtap_source=None, agg_store_file="defaults.json"):
        
        self.agg_store_file= agg_store_file
        self.agg_store_data=self.load_aggstore(self.agg_store_file)
        self.gtap_source=gtap_source

        if self.gtap_source is not None:
            self.sector_all = self.make_sector_all(self.gtap_sets, self.agg_store_data)
        else: 
            self.sector_all = [[
        '',
        "",
        "",
        "",
        "",
        ""
      ]]

        self.sector_pick_start = self.make_sector_pickstart(self.agg_store_data)
        self.sector_headers = self.make_sector_headers(self.agg_store_data)   #change here to make generic
        #print(self.sector_headers)

    @property
    def gtap_source(self):
        #In practive, this should only be setby the database widget for validity checking
        return self._gtap_source
    
    @gtap_source.setter
    def gtap_source(self, value):
        print(value)
        self._gtap_source=value
        if value != 'NA' and value is not None:
           self.load_gtap_sets(value)
           self.sector_all = self.make_sector_all(self.gtap_sets, self.agg_store_data)
        else:
            self.gtap_sets=None
            self.sector_all = [['', '', '', '', '', ]]
   
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

    @property
    def gtap_sets(self):
        return self._gtap_sets

    @gtap_sets.setter
    def gtap_sets(self, value):
        self._gtap_sets=value

    @property
    def sector_all(self):
        return self._sector_all
    
    @sector_all.setter
    def sector_all(self, value):
        self._sector_all=value
  
    def load_default(self, mydefaults):
        with open(mydefaults) as f:
            data=json.load(f)
        self.aggs = data
       
     #slot
    def gtapraw_source(self, value):
        value.replace('/','\\')
        
        self.gtap_source=value

    def load_gtap_sets(self, directory):
        InFile=HarFileObj(directory+"\\sets.har")
        DataHead=InFile["H2"]
        npDataArray = [x.strip(' ') for x in DataHead.array.tolist()]  #Need to strip out spaces - HARPY needs fix
        newlist = []
        for pos, value in enumerate(npDataArray):
            newlist.append([pos+1, value])
        
        self.gtap_sets = newlist
    
    def load_aggstore(self, file_name):
        
        with open(file_name) as f:
           aggstore=json.load(f)
           return aggstore
        
    def make_sector_all(self, sets, agg_store):
        '''takes sets and aggstore and does a match merge on sect abrev'''
        newdict={x[1]: x for x in agg_store['sectors']['allsect']}
        matchlist =  [x+newdict.get(x[1], ['','', '','',''])[2:] for x in sets ]
        return matchlist
    
    def make_sector_pickstart(self, agg_store):
        return agg_store['sectors']['picks']
    
    def make_sector_headers(self, agg_store):
        return agg_store['sectors']['headers']
