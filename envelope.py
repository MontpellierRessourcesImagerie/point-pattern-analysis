import time
import datetime
from ij import IJ
from ij.gui import Plot
from ij.process import StackStatistics
from mcib3d.geom import Point3D
from mcib3d.geom import Objects3DPopulation
from fr.cnrs.mri.cialib.stats import Histogram 
from fr.cnrs.mri.cialib.generator import UniformRandomSpotGenerator

N = 100

image = IJ.getImage()
title = image.getTitle()
width, height, _, nSlices, _ = image.getDimensions()
bitDepth = image.getBitDepth()
calibration = image.getCalibration()


gen = UniformRandomSpotGenerator()
gen.width = width
gen.height = height
gen.depth = nSlices
gen.calibration = calibration
gen.bitDepth = bitDepth
gen.numberOfSamples = int(StackStatistics(image).max)


print(gen.numberOfSamples )

startTime = time.time()
IJ.log("Started sampling " + str(datetime.datetime.fromtimestamp(startTime)))
eCDFs = []
hist = None
for i in range(N):
    gen.sample()
    points = gen.points
    pop = Objects3DPopulation()
    pop.setScale(calibration.pixelWidth, calibration.pixelDepth, calibration.unit)
    objects = [Point3D(x, y, z) for x, y, z in points]
    pop.addPoints(objects)
    distances = list(pop.distancesAllClosestCenter().getArray())
    hist = Histogram(distances, start=0, end=8, nBins=100)
    hist.autoBinning = False
    hist.cumulate()
    eCDFs.append(hist)
if not hist:
    exit(1)
matrix = []
for histo in eCDFs:
    matrix.append(histo.counts)
matrix = zip(*matrix)
MINS = []
MAXS = []
MEANS = []
for values in matrix:
    MINS.append(min(values))
    MAXS.append(max(values))
    MEANS.append(sum(values) / len(values))

print(MINS)
print(MEANS)
print(MAXS)
plot = Plot("mean and envelop for" + title,  "distance d [micron]", "fraction of distances <= d",  Plot.X_NUMBERS + Plot.Y_NUMBERS + Plot.X_TICKS + Plot.X_MINOR_TICKS)    
plot.setOptions("xdecimals=2")
plot.setJustification(Plot.RIGHT)
plot.setColor("gray")
plot.setLineWidth(2)
plot.add("line", hist.binStarts, MINS)
plot.setLabel(-1, "envelope border")
plot.setLineWidth(2)
plot.add("line", hist.binStarts, MAXS)
plot.setLabel(-1, "envelope border")
plot.setColor("black")
plot.setLineWidth(2)
plot.setLabel(-1, "envelope mean")
plot.add("line", hist.binStarts, MEANS)
plot.show()

endTime = time.time()
IJ.log("Finished sampling " + str(datetime.datetime.fromtimestamp(endTime)))
IJ.log("Duration of calculation: " + str(datetime.timedelta(seconds = endTime - startTime)))

print(distances[0])