from fr.cnrs.mri.cialib.generator import DispersedRandomNucleiGenerator

gen = DispersedRandomNucleiGenerator()

gen.spotGenerator.numberOfSamples = 300
gen.nonOverlapping = True
gen.spotGenerator.maxDistFromGrid = 90
gen.sample()
gen.createGroundTruthImage()
gen.groundTruthImage.show()
table = gen.getGroundTruthTable()
table.show("nuclei")