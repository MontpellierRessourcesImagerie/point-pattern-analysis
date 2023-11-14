from ij import IJ
from fr.cnrs.mri.cialib.stats import Histogram 
from fr.cnrs.mri.cialib.spatialstats import NearestNeighborEmpiricalCDF
from ij.measure import ResultsTable
from jarray import array

image = IJ.getImage()
nn = NearestNeighborEmpiricalCDF(image)
nn.calculateDistances()

hist = Histogram(nn.distances, start=0, end=max(nn.distances) + 1, nBins=12)
hist.autoBinning = False
hist.calculate()
hist.getPlot().show()

hist.cumulate()
hist.getPlot().show()