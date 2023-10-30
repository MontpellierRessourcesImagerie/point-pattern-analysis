from __future__ import division
from java.lang import Float
import math
from ij import ImagePlus
from ij.gui import Plot
from ij.process import FloatProcessor
from ij.process import StackStatistics



class Histogram:


    def __init__(self, data, start=0, end=0, nBins=0):
        self.data = data
        self.stats = Statistics(data)
        self.autoBinning = True
        self.start = start
        self.end = end
        self.binWidth = 0
        self.nBins = nBins
        self.binStarts = []
        self.counts = []
        
        
    def calculate(self):
        if self.autoBinning:
            self.binWidth = 3.49 * self.stats.stdDev * self.stats.count ** (-1.0/3.0)
            self.nBins = int(math.floor(((self.stats.max - self.stats.min) / self.binWidth)) + 0.5)
            self.nBins = max(2, self.nBins)
        ip = FloatProcessor(self.stats.count, 1, self.data, None)
        imp = ImagePlus("", ip)
        stats = StackStatistics(imp, self.nBins, self.start, self.end)
        self.counts = stats.histogram()
        self.binStarts = [self.start + ((i+1) * self.binWidth) for i in range(len(self.counts))]
        
        
    def getPlot(self, title = "data", xLabel = "distance [micron]", yLabel = "count"):
        plot = Plot("histogram of " + title,  xLabel, yLabel, self.binStarts, self.counts)    
        plot.setStyle(0, "black,green,2.0,separated bars")
        return plot
    


class Statistics:
    
    
    def __init__(self, data):
        self.data = data
        self.count = len(data)
        self.total = 0
        self.min = Float.MAX_VALUE
        self.max = -Float.MAX_VALUE
        self.mean = 0
        self.absDev = 0
        self.stdDev = 0
        self.variance = 0
        self.skewness = 0
        self.kurtosis = 0
        self.calculate()
        
        
    def calculate(self):
        for value in self.data:
            self.total = self.total + value
            if value < self.min:
                self.min = value
            if value > self.max:
                self.max = value
        self.mean = self.total / self.count
        for value in self.data:
            s = value - self.mean
            self.absDev = self.absDev + abs(s)
            p = s * s  
            self.variance = self.variance + p
            p = p * s
            self.skewness = self.skewness + p
            p = p * s
            self.kurtosis = self.kurtosis + p 
        self.absDev = self.absDev / self.count
        self.variance = self.variance / (self.count - 1)
        self.stdDev = math.sqrt(self.variance)
        if self.variance > 0:
            self.skewness = self.skewness / (self.count * self.stdDev**3)
            self.kurtosis = (self.kurtosis / (self.count * self.variance**2)) - 3
        
        
    def __str__(self):
        res = "Statistics[mean=" + str(self.mean) + ", stdDev=" + str(self.stdDev) + ", min=" + str(self.min) + ", max=" + str(self.max) + "]";
        return res        
