from ij import IJ
from fr.cnrs.mri.cialib.generator import SpotGenerator
from fr.cnrs.mri.cialib.imaging import Microscope

mask = IJ.getImage()
gen = SpotGenerator()
gen.setMask(mask)
gen.numberOfSamples = 500
gen.numberOfClusters = 10
gen.maxDistFromClusterCenter = 50
gen.sampleClusteredPoints()
gen.createGroundTruthImage()
gen.groundTruthImage.show()