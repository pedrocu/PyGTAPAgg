def makeaggcmf(aggart):
        """Decorator for wrapping CMF files for final aggregation programs.

    Args:
        aggart (function): The function to decorate.

    Returns:
        function: A wrapper function that creates and writes CMF files.
    """
        def inner(self, base_gtap, agg_gtap, file_name):
            cmf_file = open('{agg}\\{file}.cmf'.format(agg=agg_gtap, file=file_name), 'w+')
            cmf_file.write("check-on-read elements = no; \n")
            cmf_file.write("aux files = \"agg{file}\"; \n".format(file=file_name)) 
            cmf_file.write("file DSETS = \"{base}\\gsdset.har\"; \n".format(base=base_gtap))
            cmf_file.write("file ASETS = \"{agg}\\aggsup.har\"; \n".format(agg=agg_gtap))
            
            add_these=aggart(self, base_gtap, agg_gtap, file_name)

            for i in add_these:
                cmf_file.write(i)

            cmf_file.close()

        return inner

def makeauxcmf(aggart):
    """Decorator for wrapping CMF files for auxiliary programs.

    Args:
        aggart (function): The function to decorate.

    Returns:
        function: A wrapper function that creates and writes CMF files.
    """
    def inner(self, base_gtap, agg_gtap, file_name):
            cmf_file = open('{agg}\\{file}.cmf'.format(agg=agg_gtap, file=file_name), 'w+')
            cmf_file.write('check-on-read elements = no;\n')
            cmf_file.write("aux files = \"{base}\\{file}\";\n".format(base=base_gtap, file=file_name)) 
            cmf_file.write("file GTAPDATA = \"{agg}\\basedata.har\";\n".format(agg=agg_gtap))
            cmf_file.write("file GTAPSETS = \"{agg}\\aggsup.har\";\n".format(agg=agg_gtap))
            cmf_file.write("file GTAPPARM = \"{agg}\\par.har\";\n".format(agg=agg_gtap))
            
            add_these=aggart(self, base_gtap, agg_gtap, file_name)

            for i in add_these:
                cmf_file.write(i)

            cmf_file.close()

    return inner