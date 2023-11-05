from ij import IJ
from ij.measure import ResultsTable
from fr.cnrs.mri.cialib.spatialstats import EmptySpaceEmpiricalCDF

COLOR = "red"

image = IJ.getImage()
eCDF = EmptySpaceEmpiricalCDF(image, 1000)

hist = eCDF.get()
plot = hist.getPlot(title=image.getTitle()+" (empty space eCDF)")
plot.setStyle(0, COLOR+","+COLOR+",2,line")
plot.show()