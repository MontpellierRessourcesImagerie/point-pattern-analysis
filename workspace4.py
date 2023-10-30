from fr.cnrs.mri.cialib.stats import Histogram 
from ij.measure import ResultsTable
from jarray import array

COLUMN = "V2"
TABLE = "ClosestDistanceCCUnit"

table = ResultsTable.getResultsTable(TABLE)
data = table.getColumn(COLUMN)
data = array(list(data), 'f')

hist = Histogram(data)
hist.calculate()
hist.getPlot().show()

