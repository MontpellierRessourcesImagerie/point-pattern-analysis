from ij import IJ
from ij.measure import ResultsTable
from ij.process import StackStatistics
from fr.cnrs.mri.cialib.spatialstats import Envelope
from fr.cnrs.mri.cialib.spatialstats import EmptySpaceEmpiricalCDF

COLOR = "red"

image = IJ.getImage()
nrOfRefPoints = int(StackStatistics(image).max)
eCDF = EmptySpaceEmpiricalCDF(image, nrOfRefPoints)
hist = eCDF.get()
plot = hist.getPlot(title=image.getTitle()+" (empty space eCDF)")
plot.setStyle(0, COLOR+","+COLOR+",2,line")

maxDist = max(eCDF.distances)
eCDF.histEnd = maxDist
envelope = Envelope(eCDF)
envelope.calculate()
envelopePlot = envelope.getPlot()
envelopePlot.addObjectFromPlot(plot, 0)
envelopePlot.show()