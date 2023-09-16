from fr.cnrs.mri.cialib.generator import SpotGenerator
from fr.cnrs.mri.cialib.imaging import Microscope

gen = SpotGenerator()
gen.sampleUniformRandomPoints()
gen.createGroundTruthImage()
gen.groundTruthImage.show()