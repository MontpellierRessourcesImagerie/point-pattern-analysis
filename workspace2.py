from fr.cnrs.mri.cialib.generator import NucleiGenerator

gen = NucleiGenerator()

gen.spotGenerator.numberOfSamples = 300
gen.sampleClusteredNuclei()
gen.createGroundTruthImage()
gen.groundTruthImage.show()
table = gen.getGroundTruthTable()
table.show("nuclei")