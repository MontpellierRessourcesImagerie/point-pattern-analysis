###############################################################################################
##
## simulate_microscope.py
##
## Answers a number of clustered points in the image or mask with a given number of cluster centers
## and a max. distance of the points from a center
## 
## (c) 2023 INSERM
##
## written by Volker Baecker at the MRI-Center for Image Analysis (MRI-CIA - https://www.mri.cnrs.fr/en/data-analysis.html)
##
## simulate_microscope.py is free software under the MIT license.
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


from ij import IJ
from ij import Prefs
from fr.cnrs.mri.cialib.imaging import Microscope
from fr.cnrs.mri.cialib.options import Options


SAVE_OPTIONS = True


def main():
    mic = Microscope()
    options = getOptions()
    if not options:
        return
    options.transferTo(mic, getOptionsMap())
    if mic.batchProcess:
        mic.runBatchMT(options)
        return
    img = IJ.getImage()    
    mic.run(img, options, display = True)
    
  
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
    optionsPath = pluginsPath + "3D_Synthetic_Spots/simulate_microscope.json"
    return optionsPath
   

def getOptionsMap():
    optionsMap = {'psfSigmaXY': 'sigma_xy', 
                   'psfSigmaZ': 'sigma_z', 
                   'backgroundPhotons': 'background',
                   'xyGradient': 'gradient_xy',
                   'zGradientStdDev': 'gradient_z',
                   'exposureTime': 'exposure',
                   'readStdDev': 'read_noise',
                   'detectorGain': 'gain',
                   'detectorOffset': 'offset',
                   'bitDepth': 'bit',
                   'maxPhotonEmission': 'max._photon',
                   'binning': 'binning',
                   'batchProcess': 'batch',
                   'inputFolder': 'input-folder',
                   'outputFolder': 'output-folder',
                  }
    return optionsMap
   
   
main()