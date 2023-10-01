from inra.ijpb.label import RegionAdjacencyGraph
from fr.cnrs.mri.cialib.generator import NucleiGenerator

gen = NucleiGenerator()

numberOfSamples = 300
gen.spotGenerator.numberOfSamples = numberOfSamples
# gen.sampleClusteredNuclei()
gen.sampleUniformRandomNuclei()
gen.createGroundTruthImage()
image = gen.groundTruthImage

rag = RegionAdjacencyGraph.computeAdjacencies(image)

rag = [elem.label1-1 for elem in list(rag)]
rag = set(rag)


gen.removeNuclei(rag)
gen.createGroundTruthImage()

missing = numberOfSamples - len(gen.nuclei)

trial = 0
while missing > 0 and trial < 10:
    print(trial, missing)
    gen2 = NucleiGenerator()
    gen2.spotGenerator.numberOfSamples = missing
    # gen2.spotGenerator.points = gen.spotGenerator.points
    # gen2.sampleClusteredNuclei()
    gen2.sampleUniformRandomNuclei()
    gen.nuclei = gen.nuclei + gen2.nuclei
    gen.createGroundTruthImage()
    image = gen.groundTruthImage
    
    rag = RegionAdjacencyGraph.computeAdjacencies(image)
    
    rag = [elem.label1-1 for elem in list(rag)]
    rag = set(rag)
    
    
    gen.removeNuclei(rag)
    missing = numberOfSamples - len(gen.nuclei)
    gen.createGroundTruthImage()
    trial = trial + 1
gen.groundTruthImage.show()