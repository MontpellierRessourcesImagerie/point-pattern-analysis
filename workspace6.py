from java.lang import Double
from ij import IJ
from mcib3d.geom2 import Objects3DIntPopulation
from mcib3d.geom2 import Object3DInt
from mcib3d.geom2 import VoxelInt
from mcib3d.geom2.measurementsPopulation import MeasurePopulationClosestDistance
from fr.cnrs.mri.cialib.spatialstats import EmptySpaceEmpiricalCDF
from inra.ijpb.measure.region3d import Centroid3D
from inra.ijpb.label import LabelImages 

image = IJ.getImage()
cal = image.getCalibration()
eCDF = EmptySpaceEmpiricalCDF(image, 1000)


labels = list(LabelImages.findAllLabels(image))
centroids = Centroid3D.centroids(image.getStack(), labels, None)
points = [(c.getX(), c.getY(), c.getZ()) for c in centroids]


refPoints = eCDF.getReferencePoints()

objects = [Object3DInt(VoxelInt(int(x), int(y), int(z), l)) for l,(x,y,z) in enumerate(points, start=1)]
refObjects = [Object3DInt(VoxelInt(int(x), int(y), int(z), l)) for l,(x,y,z) in enumerate(refPoints, start=1)]

for object in objects:
    object.setVoxelSizeXY(cal.pixelWidth)
    object.setVoxelSizeZ(cal.pixelDepth)
for object in refObjects:
    object.setVoxelSizeXY(cal.pixelWidth)
    object.setVoxelSizeZ(cal.pixelDepth)
pop = Objects3DIntPopulation()
pop.addObjects(objects)
refPop = Objects3DIntPopulation()
refPop.addObjects(refObjects)
analyzer = MeasurePopulationClosestDistance(pop, refPop, Double.POSITIVE_INFINITY, MeasurePopulationClosestDistance.CLOSEST_CC1_UNIT)
table = analyzer.getResultsTableOnlyColoc(False)
table.show("empty space distances")
