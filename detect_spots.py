from fr.cnrs.mri.cialib.options import Options
from fr.cnrs.mri.cialib.detection import SpotDetectionPlugInFilter
from ij.plugin.filter import PlugInFilterRunner


options = Options.fromFile("/home/baecker/Documents/mri/2023/mifobio/point-pattern-analysis/detect_spots.json");
options.createDialog()
detector = SpotDetectionPlugInFilter()
options.dialog.addDialogListener(detector)
runner = PlugInFilterRunner(detector, "detect spots", str(options))
options.dialog.addPreviewCheckbox(runner) 
print("show dialog")
options.dialog.showDialog()