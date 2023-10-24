from ij import IJ
from ij import Prefs
from fr.cnrs.mri.cialib.options import Options
from fr.cnrs.mri.cialib.detection import SpotDetectionPlugInFilter


SAVE_OPTIONS = True


def main():
    img = IJ.getImage()
    if img.getOverlay():
        img.getOverlay().clear()
    plugin = SpotDetectionPlugInFilter()
    options = getOptions(plugin)
    if not options:
        return
    options.transferTo(plugin, getOptionsMap())
    if plugin.spotDetector.batchProcess:
        plugin.spotDetector.runBatch()
        return    
    plugin.spotDetector.run(img)    
    plugin.spotDetector.spotImage.show()
    table = plugin.spotDetector.getSpotsAsResultsTable()
    table.show("spots in image")
    
   
def getOptions(plugin):
    options = Options.fromFile(getOptionsPath())
    options.autosave = SAVE_OPTIONS
    optionsOnly = Prefs.get("mri.options.only", "false")
    options.addPreviewPlugin(plugin, "detect spots")
    options.transferTo(plugin, getOptionsMap())
    options = options.showDialog()
    if not options:
        return None
    if optionsOnly=="true":
        return None
    return options
    

def getOptionsPath():
    pluginsPath = IJ.getDirectory("plugins")
    optionsPath = pluginsPath + "3D_Synthetic_Spots/detect_spots.json"
    return optionsPath
    

def getOptionsMap():        
    optionsMap = {'spotDetector.spotDiameterXY': 'xy-diameter', 
                  'spotDetector.spotDiameterZ': 'z-diameter',   
                  'spotDetector.prominence': 'prominence', 
                  'spotDetector.threshold': 'threshold',
                  'spotDetector.batchProcess': 'batch',
                  'spotDetector.inputFolder': 'input-folder',
                  'spotDetector.outputFolder': 'output-folder',
                  }
    return optionsMap
    
    
main()