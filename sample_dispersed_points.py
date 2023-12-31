###############################################################################################
##
## sample_dispersed_points.py
##
## Answers a number of dispersed points in the image or mask with a given maximal distance of
## each point from the grid points.
## 
## (c) 2023 INSERM
##
## written by Volker Baecker at the MRI-Center for Image Analysis (MRI-CIA - https://www.mri.cnrs.fr/en/data-analysis.html)
##
## sample_dispersed_points.py is free software under the MIT license.
## 
## MIT License
##
## Copyright (c) 2023 INSERM
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
## 
################################################################################################

import os
import time
import datetime
from ij import IJ
from ij import Prefs
from fr.cnrs.mri.cialib.generator import DispersedRandomSpotGenerator
from fr.cnrs.mri.cialib.options import Options


SAVE_OPTIONS = True


def main():
    gen = DispersedRandomSpotGenerator()
    options = getOptions()
    if not options:
        return
    options.transferTo(gen, getOptionsMap())
    gen.run()
    
  
def getOptionsPath():
    pluginsPath = IJ.getDirectory("plugins")
    optionsPath = pluginsPath + "point_pattern_analysis/sample_dispersed_points.json"
    return optionsPath


def getOptions():
    options = Options.fromFile(getOptionsPath())
    options.autosave = SAVE_OPTIONS
    optionsOnly = Prefs.get("mri.options.only", "false")
    if not options.showDialog():
        return None
    if optionsOnly=="true":
        return None
    return options
    
 
def getOptionsMap():        
    optionsMap = {'width': 'width', 
                   'height': 'height', 
                   'depth': 'depth',
                   'bitDepth': 'type',
                   'calibration.pixelWidth': 'xy-size',
                   'calibration.pixelHeight': 'xy-size',
                   'calibration.pixelDepth': 'z-size',
                   'calibration.unit': 'unit',
                   'numberOfSamples': 'number',
                   'mask': 'mask',
                   'maxDistFromGrid': 'max.-dist.',
                   'batchProcess': 'batch',
                   'outputFolder': 'output-folder',
                   'numberOfImages': 'number-of-images',
                  }
    return optionsMap  
    
    
main()