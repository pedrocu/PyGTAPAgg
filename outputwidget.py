from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc

import GtapHelpers
from harpy import har_file, header_array
import numpy as np
import subprocess 
import os 
import re

def makeaggcmf(aggart):
        '''decoraotor for wrapping cmf files for final aggrigation progarm'''
        def inner(self, base_gtap, agg_gtap, file_name):
            cmf_file = open('{agg}\\{file}.cmf'.format(agg=agg_gtap, file=file_name), 'w+')
            cmf_file.write('check-on-read elements = no;\n')
            cmf_file.write('aux files = src\\agg{file};\n'.format(file=file_name)) 
            cmf_file.write('file DSETS = {base}\\sets.har;\n'.format(base=base_gtap))
            cmf_file.write('file ASETS = {agg}\\aggsup.har;\n'.format(agg=agg_gtap))
            
            add_these=aggart(self, base_gtap, agg_gtap, file_name)

            for i in add_these:
                cmf_file.write(i)

            cmf_file.close()

        return inner

def makeauxcmf(aggart):
    '''decoraotor for wrapping cmf files for auxilary progarm'''
    def inner(self, base_gtap, agg_gtap, file_name):
            cmf_file = open('{agg}\\{file}.cmf'.format(agg=agg_gtap, file=file_name), 'w+')
            cmf_file.write('check-on-read elements = no;\n')
            cmf_file.write('aux files = {base}\\src\\{file};\n'.format(base=base_gtap, file=file_name)) 
            cmf_file.write('file GTAPDATA = {agg}\\basedata.har;\n'.format(agg=agg_gtap))
            cmf_file.write('file GTAPSETS = {agg}\\aggsup.har;\n'.format(agg=agg_gtap))
            cmf_file.write('file GTAPPARM = {agg}\\par.har;\n'.format(agg=agg_gtap))
            
            add_these=aggart(self, base_gtap, agg_gtap, file_name)

            for i in add_these:
                cmf_file.write(i)

            cmf_file.close()

    return inner