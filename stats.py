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
        self.mode = 0
        self.xLabel =  "distance [micron]"
        self.yLabel = "count"
        self.N = 0
        
        
    def calculate(self):
        if self.autoBinning:
            self.binWidth = 3.49 * self.stats.stdDev * self.stats.count ** (-1.0/3.0)
            self.nBins = int(math.floor(((self.stats.max - self.stats.min) / self.binWidth)) + 0.5)
            self.nBins = max(2, self.nBins)
        else:
            self.binWidth = (self.end - self.start) /  self.nBins
        ip = FloatProcessor(self.stats.count, 1, self.data, None)        
        imp = ImagePlus("", ip)
        stats = StackStatistics(imp, self.nBins, self.start, self.end)
        self.counts = stats.histogram()
        self.binStarts = [self.start + ((i+1) * self.binWidth) for i in range(len(self.counts))]
        self.mode = stats.dmode
        
    
    def cumulate(self):
        if not self.counts:
            self.calculate()
        for i in range(1, len(self.counts)):
            self.counts[i] = self.counts[i] + self.counts[i-1]
        self.N = self.counts[-1]
        print("N", self.N)
        for i in range(0, len(self.counts)):
            self.counts[i] = self.counts[i] / self.N
        self.xLabel = "distance d [micron]"
        self.yLabel = "fraction of distances <= d"
            
   
    def normalizeRipley(self, volume):
        density = self.N / volume
        print('N', self.N)
        print("volume", volume)
        print("density", density)
        for i in range(0, len(self.counts)):
            self.counts[i] = self.counts[i] / density
    
    
    def getPlot(self, title = "data"):
        label = self.xLabel + " (N=" + str(self.stats.count) \
                       + ", min=" + "{:.3f}".format(self.stats.min) \
                       + ", max=" + "{:.3f}".format(self.stats.max) \
                       + ", mean=" + "{:.3f}".format(self.stats.mean) \
                       + ", stdDev=" + "{:.3f}".format(self.stats.stdDev) \
                       + ", mode=" + "{:.3f}".format(self.mode) + ")" 
        plot = Plot("histogram of " + title,  label, self.yLabel, self.binStarts, self.counts, Plot.X_NUMBERS + Plot.Y_NUMBERS + Plot.X_TICKS + Plot.X_MINOR_TICKS)    
        plot.setStyle(0, "black,green,2.0,separated bars")
        plot.setOptions("xdecimals=2")
        plot.setJustification(Plot.RIGHT)        
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
