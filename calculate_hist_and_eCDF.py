from fr.cnrs.mri.cialib.stats import Histogram 
from ij.measure import ResultsTable
from jarray import array

COLUMN = "V1"
TABLE = "empty space distances"

table = ResultsTable.getResultsTable(TABLE)
data = table.getColumn(COLUMN)
data = array(list(data), 'f')

hist = Histogram(data, start=0, end=8, nBins=100)
hist.autoBinning = False
hist.calculate()
hist.getPlot().show()

hist.cumulate()
hist.getPlot().show()