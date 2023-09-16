from ij import IJ
from fr.cnrs.mri.cialib.generator import SpotGenerator
from fr.cnrs.mri.cialib.imaging import Microscope

img = IJ.getImage()
mic = Microscope()
mic.mountSample(img)
mic.acquireImage()
mic.image.show()