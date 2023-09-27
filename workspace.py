import random
from ij import IJ
from mcib3d.geom import ObjectCreator3D
from mcib3d.geom import Vector3D
from inra.ijpb.morphology import Reconstruction3D
from inra.ijpb.morphology.filter import Erosion
from inra.ijpb.morphology.strel import DiskStrel
from fr.cnrs.mri.cialib.generator import SpotGenerator


MEAN_RADIUS_X = 4         
STDDEV_RADIUS_X = 1
MEAN_RADIUS_Y = 4            
STDDEV_RADIUS_Y = 1
MEAN_RADIUS_Z = 4           
STDDEV_RADIUS_Z = 1
NUMBER_OF_SAMPLES = 500
ROUNDS_OF_SALT_AND_PEPPER = 1
EROSION_RADIUS = 1

meanX = [random.normalvariate(MEAN_RADIUS_X, STDDEV_RADIUS_X) for i in range(NUMBER_OF_SAMPLES)]
meanY = [random.normalvariate(MEAN_RADIUS_Y, STDDEV_RADIUS_Y) for i in range(NUMBER_OF_SAMPLES)]
meanZ = [random.normalvariate(MEAN_RADIUS_Z, STDDEV_RADIUS_Z) for i in range(NUMBER_OF_SAMPLES)]


gen = SpotGenerator()
gen.setScale(0.2, 0.2, 0.7, "micron")
gen.width = 1024
gen.height = 1024
gen.depth = 128
gen.numberOfSamples = NUMBER_OF_SAMPLES
gen.sampleUniformRandomPoints()
image = gen.getEmptyImage()
objectCreator = ObjectCreator3D(image.getStack())

rx = [random.random() for _ in range(NUMBER_OF_SAMPLES)]
ry = [random.random() for _ in range(NUMBER_OF_SAMPLES)]


v1 = [Vector3D(rx[i], ry[i], 0).getNormalizedVector() for i in range(NUMBER_OF_SAMPLES)]


for label, point in enumerate(gen.points, start = 1):
    objectCreator.createEllipsoidAxesUnit(point[0], point[1], point[2], gen.calibration.getRawX(meanX[label-1]), 
                                                                        gen.calibration.getRawY(meanY[label-1]), 
                                                                        gen.calibration.getRawZ(meanZ[label-1]), 
                                                                        label, 
                                                                        v1[label-1], 
                                                                        v1[label-1].getRandomPerpendicularVector(), False)
IJ.setRawThreshold(image, 1, pow(2, gen.bitDepth) - 1)
IJ.run(image, "Convert to Mask", "background=Dark black")                                                  
for i in range(ROUNDS_OF_SALT_AND_PEPPER):
    IJ.run(image, "Salt and Pepper", "stack")
IJ.run(image, "Remove Outliers...", "radius=2 threshold=50 which=Bright stack");
stack = Reconstruction3D.fillHoles(image.getStack())
erosion = Erosion(DiskStrel.fromRadius(EROSION_RADIUS))
for i in range(EROSION_RADIUS):
    stack = erosion.process(stack)
image.setStack(stack)
image.show()