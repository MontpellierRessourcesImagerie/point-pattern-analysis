from fr.cnrs.mri.cialib.generator import DispersedRandomNucleiGenerator

gen = DispersedRandomNucleiGenerator()

gen.spotGenerator.numberOfSamples = 300
gen.nonOverlapping = False
gen.spotGenerator.maxDistFromGrid = 0
gen.sample()
gen.createGroundTruthImage()
gen.groundTruthImage.show()
table = gen.getGroundTruthTable()
table.show("nuclei")