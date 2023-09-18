from ij import IJ
from fr.cnrs.mri.cialib.generator import SpotGenerator
from fr.cnrs.mri.cialib.imaging import Microscope

mask = IJ.getImage()
gen = SpotGenerator()
gen.mask = None
gen.numberOfSamples = 1000
gen.maxDistFromGrid = 1
gen.sampleDispersedPoints()
gen.createGroundTruthImage()
gen.groundTruthImage.show()