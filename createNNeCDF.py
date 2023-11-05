from ij import IJ
from ij.measure import ResultsTable
from fr.cnrs.mri.cialib.spatialstats import NearestNeighborEmpiricalCDF
from fr.cnrs.mri.cialib.spatialstats import Envelope

COLOR = "green"

image = IJ.getImage()
eCDF = NearestNeighborEmpiricalCDF(image)
hist = eCDF.get()
plot = hist.getPlot(title=image.getTitle()+" (eCDF)")
plot.setStyle(0, COLOR+","+COLOR+",2,line")

maxDist = max(eCDF.distances)
eCDF.histEnd = maxDist
envelope = Envelope(eCDF)
envelope.calculate()
envelopePlot = envelope.getPlot()
envelopePlot.addObjectFromPlot(plot, 0)
envelopePlot.show()
