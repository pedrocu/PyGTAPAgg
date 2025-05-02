import numpy as np
from modules.HARPY import har_file, header_array
from .utilities import getaggmarg

def buildhar(self, destination_file):
        """Builds the HAR files required for aggregation.

        This method creates several HAR files based on the aggregated data,
        such as regions, sectors, and endowments. These files are used as inputs
        for the aggregation process.

        Args:
            destination_file (str): The directory where the HAR files will be created.

        Returns:
            int: Returns 0 upon successful execution.
        """

        aggsup= har_file.HarFileObj('{destination}\\aggsup.har'.format(destination=destination_file))
        dset= har_file.HarFileObj('{destination}\\dset.har'.format(destination=destination_file))
        
        #We want the unique lists of sect, reg, end from the data, not the list. The list can include values not inserted
        #Get thte values from the table so as not to create conflicts latter, consistency is maintained
        regions_x=list(set([i[5] for i in self.datastore.regions.data]))  #TBD Make these relative to the last element not 5
        sectors_x=list(set([i[5] for i in self.datastore.sectors.data]))  #TBD Make these relative to the last element not 5
        endw_x=list(set([i[4] for i in self.datastore.endowments.data]))  #TBD Make these relative to the last element not 4

        makeasets(self, regions_x, "H1", "REG", aggsup)
        makeasets(self, sectors_x, "H2", "TRAD_COMM", aggsup)
        makeasets(self, sectors_x, "H5", "PROD_COMM", aggsup)  #prod_comm is different from TRAD_COMM add CGDS for Trad_comm to get prod_Commm
        makeasets(self, endw_x, "H6","ENDW_COMM", aggsup)
        makeasets(self, ['CGDS'], "H9", "CGDS_COMM", aggsup)
        makeasets(self, self.datastore.gtap_TARS, "TARS","Tariff componenets", aggsup)
        makeasets(self, self.datastore.gtap_TARL, "TARL","Long name tariff componenets", aggsup)

        #Need H7-ENDWS, H8-ENDWM
        #default.prm - ETRAE, SLUG

        makedsets(self, self.datastore.regions.data, "DH1", "DREG", aggsup)
        makedsets(self, self.datastore.sectors.data, "DH2", "TRAD_COMM", aggsup)
        makedsets(self, self.datastore.sectors.data, "DH5", "DPROD_COMM", aggsup)
        maketrae(self, self.datastore.endowments, "ETRE", "ETRAE", aggsup)
        
        makedsets(self, self.datastore.endowments.data, "DH6","DENDW_COMM", aggsup)
        
        makemapping(self, self.datastore.sectors.data, "MCOM", "TRAD_COMM", aggsup)
        makemapping(self, self.datastore.regions.data, "MREG", "REG", aggsup)
        makemapping(self, self.datastore.endowments.data, "MEND", "ENDW_COMM", aggsup)
        makemapping(self, self.datastore.sectors.data, "MPRD", "PROD_COMM", aggsup)

        #used by flex agg
        makedsets(self, self.datastore.regions.data, "H1", "REG", dset)
        makedsets(self, self.datastore.sectors.data, "H2", "TRAD_COMM", dset)
        makedsets(self, self.datastore.endowments.data, "H6","ENDW_COMM", dset)
        makedsets(self, ['CGDS'], "H9", "CGDS_COMM", dset)
        makemapping(self, self.datastore.sectors.data, "MARG", "MARG_COMM", dset)
        makemapping(self, self.datastore.sectors.data, "DCOM", "TRAD_COMM", aggsup)
        makemapping(self, self.datastore.regions.data, "DREG", "REG", aggsup)
        makemapping(self, self.datastore.endowments.data, "DEND", "ENDW_COMM", aggsup)
        

        makeasets(self, self.datastore.sectors.data, "MARG", "MARG_COMM", aggsup)

        self.mywindow.sets_text.setText('<b>…DONE<\b>')
        
        return 0

def makeasets(self, target, setname_sht, setname_lng, har_file):
        """Creates aggregated sets and stores them in the HAR file.

        Aggregated sets are used to define groups of related items, such as regions,
        sectors, or endowments, for the purpose of aggregation.

        Args:
            target (list): The list of items to aggregate.
            setname_sht (str): The short name for the set variable.
            setname_lng (str): The long name for the set variable.
            har_file (HarFileObj): The HAR file object where the set will be written.
        """
        #Take any list
        if type(target) is list and setname_sht != 'MARG':
           seta = target.copy()
        elif setname_sht == "MARG":
            seta=getaggmarg(self, target)

        #or specify an object in the QtData model, seee select widget
        else:
            seta = target
            
        
        setstuffer(self, seta, setname_sht, setname_lng, har_file)

def makedsets(self, target, setname_sht, setname_lng, har_file):
        """Creates disaggregated sets and stores them in the HAR file.

        Disaggregated sets are used to define individual items, such as specific
        regions, sectors, or endowments, that are part of a larger aggregated group.

        Args:
            target (list): The list of items to disaggregate.
            setname_sht (str): The short name for the set variable.
            setname_lng (str): The long name for the set variable.
            har_file (HarFileObj): The HAR file object where the set will be written.
        """
        
        #Take any list
        if type(target[0]) is str:
           set = target.copy()
           
        #or specifiy a QtData Model
        else:
            data=target
            data=sorted(data, key=lambda k: k[0])
            set = [i[1] for i in data]
            

        setstuffer(self, set, setname_sht, setname_lng, har_file)

def maketrae(self, target, setname_sht, setname_lng, har_file):
        """Creates ETRAE sets for aggregation and stores them in the HAR file.

        ETRAE sets are used to define relationships between endowments for specific purposes.

        Args:
            target (object): The endowment data from the datastore.
            setname_sht (str): The short name for the ETRAE variable.
            setname_lng (str): The long name for the ETRAE variable.
            har_file (HarFileObj): The HAR file object where the set will be written.
        """
        #Take any list
        

        if type(target.etrae[0]) is str:
           set = target
        #or specifiy a QtData Model
           
        else:
            data=target.etrae
            sort_list=target.pick_start
            #Make sure the data are sorted by the picklist
            data.sort(key=lambda i: sort_list.index(i[0]))
            set_1 = [0 if i[1] == 'mobile' else i[1] for i in data]
            set_1 = [float(i) for i in set_1]
        
            set = np.array([set_1], dtype=np.float32)
            
            #Create SLUG bases on values given
            slug= [0 if i == 'mobile' else 1 for i in [i[1] for i in data]]
            setstuffer(self, slug, 'SLUG', 'Sluggish Endowments', har_file)
        
        
            setstuffer(self, set, setname_sht, setname_lng, har_file)
     
def setstuffer(self, set, setname_sht, setname_lng, har_file):
        """Helper method to create and store sets in the HAR file.

        This method is a utility function that creates a set from the provided data
        and writes it into a HAR file.

        Args:
            seta (list or array): The data to be added to the set.
            setname_sht (str): The short name for the set variable.
            setname_lng (str): The long name for the set variable.
            har_file (HarFileObj): The HAR file object where the set will be written.
        """
        if setname_sht in ("DH5", "H5"):
            set.append("CGDS")
        
        my_set=header_array.HeaderArrayObj.HeaderArrayFromData(np.array(set), setname_sht, 
                        'Set {first}'.format(first=setname_lng))

        har_file[setname_sht] = my_set
        har_file.writeToDisk()

def makemapping(self, target, mapname_sht, mapname_lng, har_file):
        """Creates mapping data for aggregation.

        This method generates mapping information to relate items in the dataset
        (e.g., regions, sectors, endowments) to their aggregated counterparts.

        Args:
            target (list): The list of items to map.
            mapname_sht (str): Short name for the mapping variable.
            mapname_lng (str): Long name for the mapping variable.
            har_file (HarFileObj): The HAR file object where the mapping will be written.
        """
        
        data=sorted(target, key=lambda k: k[0])
               
        #Metrics (if longname not provided)
        last_field=len(data[0])-1
        
        
        agg_map =  [i[last_field] for i in data]
       

        if mapname_sht == "MARG":
            agg_map = [i[-1] for i in data if i[1] in ['otp', 'atp', 'wtp'] ]   
            print(agg_map)

        number_agg = len(set(agg_map))

        orig_set = [i[1] for i in data]
        number_items = len(set(orig_set))

        if mapname_sht == "MPRD":
            number_agg = number_agg+1
            number_items = number_items+1
            agg_map.append("CGDS")

        #Harpy 
        my_map=header_array.HeaderArrayObj.HeaderArrayFromData(np.array(agg_map), mapname_sht, 
                        'Mapping {short} from {long}({many}) to {long}({agg})'.format(long=mapname_lng, short=mapname_sht, many=number_items, agg=number_agg) )
        har_file[mapname_sht] = my_map
        
        har_file.writeToDisk() 

