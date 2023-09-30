###############################################################################################
##
## sample_dispersed_nuclei.py
##
## Creates a number of dispersed nuclei in the image or mask.
## 
## (c) 2023 INSERM
##
## written by Volker Baecker at the MRI-Center for Image Analysis (MRI-CIA - https://www.mri.cnrs.fr/en/data-analysis.html)
##
## sample_dispersed_nuclei.py is free software under the MIT license.
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
from ij import IJ
from ij import Prefs
from fr.cnrs.mri.cialib.options import Options
from fr.cnrs.mri.cialib.generator import NucleiGenerator


SAVE_OPTIONS = True


def main():
    gen = NucleiGenerator()
    options = getOptions()
    if not options:
        return
    options.transferTo(gen, getOptionsMap())
    gen.sampleDispersedNuclei()
    gen.createGroundTruthImage()
    gen.groundTruthImage.show()
    table = gen.getGroundTruthTable()
    table.show("Random Nuclei Dispersed Distribution")


def getOptions():
    options = Options.fromFile(getOptionsPath())
    options.autosave = SAVE_OPTIONS
    optionsOnly = Prefs.get("mri.options.only", "false")
    if not options.showDialog():
        return None
    if optionsOnly=="true":
        return None
    return options
 
 
def getOptionsPath():
    pluginsPath = IJ.getDirectory("plugins")
    optionsPath = pluginsPath + "3D_Synthetic_Spots/sample_dispersed_nuclei.json"
    return optionsPath
    
    
def getOptionsMap():        
    optionsMap = {'spotGenerator.width': 'width', 
                   'spotGenerator.height': 'height', 
                   'spotGenerator.depth': 'depth',
                   'spotGenerator.bitDepth': 'type',
                   'spotGenerator.calibration.pixelWidth': 'xy-size',
                   'spotGenerator.calibration.pixelHeight': 'xy-size',
                   'spotGenerator.calibration.pixelDepth': 'z-size',
                   'spotGenerator.calibration.unit': 'unit',
                   'spotGenerator.numberOfSamples': 'number',
                   'spotGenerator.mask': 'mask',
                   'spotGenerator.maxDistFromGrid': 'max.-dist.',
                   'xRadiusMean': 'mean_x_radius',
                   'xRadiusStddev': 'sdtDev_x_radius',
                   'yRadiusMean': 'mean_y_radius',
                   'yRadiusStddev': 'sdtDev_y_radius',
                   'zRadiusMean': 'mean_z_radius',
                   'saltAndPepper': 'pores',
                   'erosionRadius': 'erosion',
                  }
    return optionsMap                          
                          
                          
main()