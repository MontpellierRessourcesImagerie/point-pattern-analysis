from ij import IJ
from ij.process import StackStatistics
from ij.measure import ResultsTable
from fr.cnrs.mri.cialib.stats import Histogram


TABLE = "DistCenterCenterUnit"

table = ResultsTable.getResultsTable(TABLE)
image = IJ.getImage()
cal = image.getCalibration()
width, height, _, nSlices, _ = image.getDimensions()
print(width, height, nSlices)
width = cal.getX(width)
height = cal.getY(height)
depth = cal.getZ(nSlices)
print(width, height, depth)
volume = width * height * depth
print("volume", volume)

N = int(StackStatistics(image).max)
distances = []

for i in range(2, N+1):
    dists = list(table.getColumn("V" + str(i)))
    print(i, len(dists))
    distances.extend(dists)

print(max(distances))
print(len(distances))

hist = Histogram(distances, start=0, end=100, nBins=1000)
hist.calculate()
hist.getPlot().show()
hist.cumulate()
hist.normalizeRipley(volume)
hist.getPlot().show()
