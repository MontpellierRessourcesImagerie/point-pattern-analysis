from __future__ import division
import math
import time
import datetime
from java.lang import Double
from ij import ImagePlus
from ij import IJ
from ij.gui import Plot
from ij.measure import ResultsTable
from ij.measure import Calibration
from ij.process import StackStatistics
from inra.ijpb.measure.region3d import Centroid3D
from inra.ijpb.label import LabelImages 
from mcib3d.geom import Objects3DPopulation
from mcib3d.geom import Point3D
from mcib3d.geom2 import Objects3DIntPopulation
from mcib3d.geom2 import Object3DInt
from mcib3d.geom2 import VoxelInt
from mcib3d.geom2.measurementsPopulation import MeasurePopulationClosestDistance
from fr.cnrs.mri.cialib.stats import Histogram 
from fr.cnrs.mri.cialib.generator import UniformRandomSpotGenerator
from fr.cnrs.mri.cialib.generator import DispersedRandomSpotGenerator


class SpatialStatFunction(object):


    def __init__(self, density):
        self.density = density

    
    def getPlot(self, start, end, n):  
        X = [start + (x * ((end-start)/n)) for x in range(0, n)]
        Y = [self.v(x) for x in X]
        plot = Plot(self.getPlotTitle(), "distance d[micron]", "fraction of distances <= d")
        plot.setLineWidth(2)
        plot.setLimitsToFit(True)
        plot.add("line", X, Y)
        return plot


    def getPlotTitle(self):
        title = self.name() +"(density=" + str(self.density) + ")"        
        return title    
    

class GFunction(SpatialStatFunction):


    def __init__(self, density):
        super(GFunction, self).__init__(density)
        self.factor = -(4/3) * self.density * math.pi 
        
        
    def v(self, r):
        res = 1 - math.exp(self.factor * r**3)
        return res
        
                
    def name(self):
        return "G"
    
    
    
class FFunction(SpatialStatFunction):


    def __init__(self, density):
        super(FFunction, self).__init__(density)
        self.factor = -(4/3) * self.density * math.pi 
        
        
    def v(self, r):
        res = 1 - math.exp(self.factor * r**3)
        return res
        
        
    def name(self):
        return "F"
        
        
        
class KFunction(SpatialStatFunction):


    def __init__(self):
        self.factor = (4 * math.pi) / 3
        
        
    def v(self, r):
        res = self.factor * r**3
        return res
       
    
    def name(self):
        return "K"
        
        
    def getPlotTitle(self):
        title = self.name()  
        return title    



class LFunction(SpatialStatFunction):


    def __init__(self):
        factor = 1
        
        
    def v(self, r):
        return r
       
    
    def name(self):
        return "L"
        
        
    def getPlotTitle(self):
        title = self.name()  
        return title



class HFunction(SpatialStatFunction):


    def __init__(self):
        factor = 0
        
        
    def v(self, r):
        return 0
       
    
    def name(self):
        return "H"
        
        
    def getPlotTitle(self):
        title = self.name()  
        return title



class ECDF(object):


    def __init__(self, source, xCol="X", yCol="Y", zCol="Z"):
        self.points = None
        self.source = source
        self.nBins = 100
        self.histEnd = 0
        self.distances = []
        self.calibration = Calibration()
        self.numberOfSamples = 1000
        if isinstance(source, ResultsTable):
            self.getPointsFromTable(source, xCol, yCol, zCol)
        if isinstance(source, ImagePlus):    
            self.getPointsFromLabels(source)
            self.calibration = source.getCalibration()
            self.numberOfSamples = int(StackStatistics(source).max)
        if isinstance(source, list):
            self.points = source
        
        
    def getPointsFromLabels(self, image):
        labels = list(LabelImages.findAllLabels(image))
        centroids = Centroid3D.centroids(image.getStack(), labels, None)
        self.points = [(c.getX(), c.getY(), c.getZ()) for c in centroids]
    
    
    def getPointsFromTable(self, table, xCol, yCol, zCol):
        X = table.getColumn(xCol)
        Y = table.getColumn(yCol)
        Z = table.getColumn(zCol)
        self.points = zip(X, Y, Z)
        

    def calculateDistances(self):
        raise NotImplementedError("Subclass responsibility")
        
        
    def get(self):
        if not self.distances:
            self.calculateDistances()
        end = self.histEnd
        if not end:
            end = math.ceil(max(self.distances))               
        hist = Histogram(self.distances, 
                         start=0, 
                         end=end,
                         nBins=self.nBins)
        if self.nBins:
            hist.autoBinning = False
        hist.cumulate()
        return hist


    def getGenerator(self, nrOfSamples):
        generator = UniformRandomSpotGenerator()
        width, height, _, nSlices, _ = self.source.getDimensions()
        generator.width = width
        generator.height = height
        generator.depth = nSlices
        generator.calibration = self.source.getCalibration()
        generator.bitDepth = self.source.getBitDepth()        
        generator.numberOfSamples = nrOfSamples      
        return generator
        
        
    
class NearestNeighborEmpiricalCDF(ECDF):


    def __init__(self, source, xCol="X", yCol="Y", zCol="Z"):
        super(NearestNeighborEmpiricalCDF, self).__init__(source, xCol=xCol, yCol=yCol, zCol=zCol)
        
    
    def calculateDistances(self):
        pop = Objects3DPopulation()
        calibration = self.source.getCalibration()
        pop.setScale(calibration.pixelWidth, calibration.pixelDepth, calibration.unit)
        objects = [Point3D(x, y, z) for x, y, z in self.points]
        pop.addPoints(objects)
        self.distances = list(pop.distancesAllClosestCenter().getArray())
        


class EmptySpaceEmpiricalCDF(ECDF):


    def __init__(self, source, nrOfRefPoints, xCol="X", yCol="Y", zCol="Z"):
        super(EmptySpaceEmpiricalCDF, self).__init__(source, xCol=xCol, yCol=yCol, zCol=zCol)
        self.nrOfRefPoints = nrOfRefPoints        
        self.referencePoints = None
        
    
    def getPointsFromLabels(self, image):
        labels = list(LabelImages.findAllLabels(image))
        centroids = Centroid3D.centroids(image.getStack(), labels, None)
        self.points = [(c.getX(), c.getY(), c.getZ()) for c in centroids]
        
        
    def calculateDistances(self):
        refPoints = self.getReferencePoints()
        cal = self.calibration        
        objects = [Object3DInt(VoxelInt(int(x), int(y), int(z), l)) for l,(x,y,z) in enumerate(self.points, start=1)]
        refObjects = [Object3DInt(VoxelInt(int(x), int(y), int(z), l)) for l,(x,y,z) in enumerate(refPoints, start=1)]
        for object in objects:
            object.setVoxelSizeXY(cal.pixelWidth)
            object.setVoxelSizeZ(cal.pixelDepth)
        for object in refObjects:
            object.setVoxelSizeXY(cal.pixelWidth)
            object.setVoxelSizeZ(cal.pixelDepth)
        pop = Objects3DIntPopulation()
        pop.addObjects(objects)
        refPop = Objects3DIntPopulation()
        refPop.addObjects(refObjects)
        analyzer = MeasurePopulationClosestDistance(refPop, pop, Double.POSITIVE_INFINITY, MeasurePopulationClosestDistance.CLOSEST_CC1_UNIT)
        table = analyzer.getResultsTableOnlyColoc(True)
        self.distances = list(table.getColumn("V1"))
        
        
    def getReferencePoints(self):
        if not self.referencePoints:
            generator = self.getGenerator(self.nrOfRefPoints)
            generator.sample()
            self.referencePoints = generator.points
        return self.referencePoints



class Envelope(object):


    def __init__(self, eCDF):
        self.mins = []
        self.means = []
        self.maxs = []
        self.eCDF = eCDF
        self.N = 100
        self.generator = self.eCDF.getGenerator(self.eCDF.numberOfSamples)
        self.binStarts = None
        
        
    def calculate(self):
        eCDFs = []
        self.mins = []
        self.means = []
        self.maxs = []        
        startTime = time.time()
#        self.eCDF.calculateDistances()
#        self.eCDF.histMax = max(self.eCDF.distances)
#        print(self.eCDF.histMax)
        IJ.log("Started sampling " + str(datetime.datetime.fromtimestamp(startTime)))
        hist = None
        for i in range(self.N):
            self.generator.sample()
            self.eCDF.points = self.generator.points         
            self.eCDF.calculateDistances()
            hist = self.eCDF.get()
            eCDFs.append(hist)
        self.binStarts = hist.binStarts
        matrix = []
        for hist in eCDFs:
            matrix.append(hist.counts)
        matrix = zip(*matrix)
        for values in matrix:
            self.mins.append(min(values))
            self.maxs.append(max(values))
            self.means.append(sum(values) / len(values))
        endTime = time.time()
        IJ.log("Finished sampling " + str(datetime.datetime.fromtimestamp(endTime)))
        IJ.log("Duration of calculation: " + str(datetime.timedelta(seconds = endTime - startTime)))
        
        
    def getPlot(self):
        plot = Plot("mean and envelop for" + self.eCDF.source.getTitle(),  "distance d [micron]", "fraction of distances <= d",  Plot.X_NUMBERS + Plot.Y_NUMBERS + Plot.X_TICKS + Plot.X_MINOR_TICKS)    
        plot.setOptions("xdecimals=2")
        plot.setJustification(Plot.RIGHT)
        plot.setColor("gray")
        plot.setLineWidth(2)
        plot.add("line", self.binStarts, self.mins)
        plot.setLabel(-1, "envelope border")
        plot.setLineWidth(2)
        plot.add("line", self.binStarts, self.maxs)
        plot.setLabel(-1, "envelope border")
        plot.setColor("black")
        plot.setLineWidth(2)
        plot.setLabel(-1, "envelope mean")
        plot.add("line", self.binStarts, self.means)
        return plot