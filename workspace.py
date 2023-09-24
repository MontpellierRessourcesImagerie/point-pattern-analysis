from java.io import StringWriter
from fr.cnrs.mri.cialib.options import Options
from fr.cnrs.mri.cialib.options import FloatOption
import json

options = Options("Simulate Microscope Options")

option = FloatOption("sigma_xy", 1.0)
option.setDefaultValue(1.0)
option.setLabel("sigma_xy of psf")
option.setHelpText("Sigma of the gaussian psf in the xy-plane")

option2 = FloatOption("sigma_z", 1.3)
option2.setDefaultValue(1.3)
option2.setLabel("sigma_z of psf")
option2.setHelpText("Sigma of the gaussian psf in the z-dimension")

options.add(option)
options.add(option2)

options.saveAs("/tmp/smo.json")

newOptions = Options.fromFile("/tmp/smo.json")

print(newOptions.sortedList())

res = newOptions.showDialog()
print(res)

print(newOptions.sortedList())

print(newOptions.get('sigma_xy'))
print(newOptions.value('sigma_xy'))

newOptions.setValue('sigma_xy', 18)
print(newOptions.get('sigma_xy'))