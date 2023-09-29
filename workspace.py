from ij import IJ
from ij.plugin import ImageCalculator
from inra.ijpb.morphology import Reconstruction3D
from inra.ijpb.morphology.filter import Erosion
from inra.ijpb.morphology.strel import DiskStrel

erosionRadius = 1

image = IJ.getImage()
imp = image.duplicate();
IJ.setRawThreshold(imp, 1, pow(2, 16) - 1)
IJ.run(imp, "Convert to Mask", "background=Dark black")       
IJ.run(imp, "Salt and Pepper", "stack")
IJ.run(imp, "Remove Outliers...", "radius=2 threshold=50 which=Bright stack")
stack = Reconstruction3D.fillHoles(imp.getStack())
erosion = Erosion(DiskStrel.fromRadius(erosionRadius))
stack = erosion.process(stack)   
imp.setStack(stack)
IJ.run(imp, "Divide...", "value=255.000 stack")
IJ.run(imp, "16-bit", "")
ImageCalculator.run(image, imp, "Multiply stack")
