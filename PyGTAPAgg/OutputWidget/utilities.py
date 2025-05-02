import numpy as np
from PyQt6 import QtCore as qtc

def getaggsets(self, target):
        """Retrieves aggregated data from the Qt model.

        This method extracts the aggregated data from the Qt model and organizes it
        into a structured format for use in aggregation tasks.

        Args:
            target (QtModel): The Qt model containing the aggregation data.

        Returns:
            list: A list of unique aggregated items extracted from the model.
        """
        myaset=[]
        for i in range(0,target.picker_model.rowCount()):
            item_index=target.picker_model.index(i)
            myaset.append(target.picker_model.data(item_index, qtc.Qt.DisplayRole))
        return myaset
    
def getaggmarg(self, target):
        """Retrieves MARG aggregated data.

        This method extracts MARG (Marginal) data, which is a specific subset of
        aggregated data used for certain aggregation tasks.

        Args:
            target (list): The input list containing the data for extraction.

        Returns:
            list: A list of unique aggregated MARG items extracted from the input data.
        """
        data=target
        data=sorted(data, key=lambda k: k[0])
        last_field=len(data[0])-1
         
        my_a_marg =  list(set([i[-1] for i in data if i[1] in ['otp', 'atp', 'wtp'] ]))
                                             #This should be otp, wtp, atp not positions in dataset

        return my_a_marg