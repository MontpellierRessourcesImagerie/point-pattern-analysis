from fr.cnrs.mri.cialib.generator import NucleiGenerator

gen = NucleiGenerator()

gen.sampleUniformRandom()
gen.createGroundTruthImage()
gen.groundTruthImage.show()