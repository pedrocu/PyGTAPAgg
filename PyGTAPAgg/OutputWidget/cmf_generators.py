from .decorators import makeaggcmf, makeauxcmf

@makeaggcmf 
def paramcmf(self, base_gtap, agg_gtap, file_name):
        """Generates the parameter CMF (Command Macro File) for aggregation.

        This method creates the necessary file references for the aggregation process
        and returns them as formatted strings.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the parameter file to be created.

        Returns:
            tuple: A tuple containing the formatted strings for each file reference:
                - DPARAM: Reference to the base parameter file.
                - EPARAM: Reference to the aggregation supplementary file.
                - PARAM: Reference to the parameter file being created.
                - DDATA: Reference to the base data file.
        """

        insert_1 = "file  DPARAM =  \"{base}\\gsdpar.har\";\n".format(base=base_gtap)
        insert_2 = "file  EPARAM =   \"{agg}\\aggsup.har\";\n".format(agg=agg_gtap)
        insert_3 = "file  PARAM = \"{agg}\\{file}.har\";\n".format(agg=agg_gtap, file=file_name)
        insert_4 = "file  DDATA= \"{base}\\gsddat.har\";\n".format(base=base_gtap)

        return (insert_1, insert_2, insert_3, insert_4)

@makeaggcmf
def emisscmf(self, base_gtap, agg_gtap, file_name):
        """Generates the emissions CMF (Command Macro File) for aggregation.

        This method creates the necessary file references for the emissions data
        aggregation process and returns them as formatted strings.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the emissions file to be created.

        Returns:
            tuple: A tuple containing the formatted strings for each file reference:
                - EMISS: Reference to the aggregated emissions file.
                - DDATA: Reference to the base emissions data file.
        """
        insert_1 = "file  EMISS = \"{agg}\\{file}.har\";\n".format(agg=agg_gtap, file=file_name) 
        insert_2 = "file  DDATA= \"{base}\\gsdemiss.har\";\n".format(base=base_gtap, file=file_name)

        return (insert_1, insert_2)

@makeaggcmf
def gtapvolcmf(self, base_gtap, agg_gtap, file_name):
        """Generates the energy volume CMF (Command Macro File) for aggregation.

        This method creates the necessary file references for the energy volume 
        data aggregation process and returns them as formatted strings.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the energy volume file to be created.

        Returns:
            tuple: A tuple containing the formatted strings for each file reference:
                - EGYVOL: Reference to the aggregated energy volume file.
                - DDATA: Reference to the base energy volume data file.
        """
        insert_1 = "file  EGYVOL = \"{agg}\\{file}.har\";\n".format(agg=agg_gtap, file=file_name) 
        insert_2 = "file  DDATA= \"{base}\\gsdvole.har\";\n".format(base=base_gtap, file=file_name)

        return (insert_1, insert_2) 

@makeauxcmf
def gtapviewcmf(self, base_gtap, agg_gtap, file_name):
        """Generates the GTAP View CMF (Command Macro File) for aggregation.

        This method creates the necessary file references for the GTAP View 
        aggregation process and returns them as formatted strings.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the GTAP View file to be created.

        Returns:
            tuple: A tuple containing the formatted strings for each file reference:
                - GTAPVIEW: Reference to the base view file.
                - TAXRATES: Reference to the base tax rates file.
        """
        insert_1 = "file GTAPVIEW = \"{agg}\\baseview.har\";\n".format(agg=agg_gtap)
        insert_2 = "file TAXRATES = \"{agg}\\baserate.har\";\n".format(agg=agg_gtap)

        return (insert_1, insert_2)

@makeauxcmf
def gtapsamcmf(self, base_gtap, agg_gtap, file_name):
        """Generates the GTAP SAM CMF (Command Macro File) for aggregation.

        This method creates the necessary file reference for the GTAP SAM 
        (Social Accounting Matrix) aggregation process and returns it as a 
        formatted string.

        Args:
            base_gtap (str): The base GTAP directory containing the source HAR files.
            agg_gtap (str): The aggregation GTAP directory where the aggregated HAR files are stored.
            file_name (str): The name of the GTAP SAM file to be created.

        Returns:
            tuple: A tuple containing the formatted string for the GTAP SAM file reference:
                - GTAPSAM: Reference to the aggregated GTAP SAM file.
        """
        insert_1 = "file GTAPSAM = \"{agg}\\GTAPsam.har\";\n".format(agg=agg_gtap)
        
        return (insert_1)
