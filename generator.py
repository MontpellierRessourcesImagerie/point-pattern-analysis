from __future__ import division
import random
import math
from ij import IJ
from ij.gui import NewImage
from ij.measure import Calibration
from ij.measure import ResultsTable
from ij.plugin import LutLoader
from ij.process import LUT 
from inra.ijpb.label.edit import FindAllLabels
from inra.ijpb.measure.region3d import BoundingBox3D


class SpotGenerator:


    def __init__(self):
        self.width = 512
        self.height = 512
        self.depth = 64
        self.calibration = Calibration()
        self.mask = None
        self.bitDepth = 16        
        self.numberOfSamples = 1000
        self.numberOfClusters = 50
        self.maxDistFromClusterCenter = 90
        self.clusterCenters = None        
        self.maxDistFromGrid = 0
        self.points = None
        self.scaledPoints = None
        self.image = None
        self.groundTruthImage = None
        self.lutName = "glasbey on dark"
        
               
    def sampleUniformRandomPoints(self):
        if self.mask:
            self.sampleUniformRandomPointsInMask()
        else:
            self.sampleUniformRandomPointsInImage()
            
            
    def sampleDispersedPoints(self):
        if self.mask:
            self.sampleDispersedPointsInMask()
        else:
            self.sampleDispersedPointsInImage()
        if self.maxDistFromGrid:
            self.addRandomShiftToPoints(self.maxDistFromGrid)
        
    
    def sampleClusteredPoints(self):
        if self.mask:
            self.sampleClusteredPointsInMask()
        else:
            self.sampleClusteredPointsInImage()
        
    
    def sampleUniformRandomPointsInMask(self):
        points = self.getPointsInMask()       
        self.points = random.sample(points, self.numberOfSamples)
        self.calibration = self.mask.getCalibration()
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " uniformly distributed points from the " + str(len(points)) + " points in the mask.")        
        
    
    def sampleDispersedPointsInMask(self):
        pointsInMask = self.getPointsInMask()
        if len(pointsInMask) <= self.numberOfSamples:
            self.points = pointsInMask
        else:
            delta = len(pointsInMask) / self.numberOfSamples
            self.points = [pointsInMask[int(math.floor(i*delta))] for i in range(0, self.numberOfSamples)]
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " dispersed points from the " + str(len(pointsInMask)) + " points in the mask.")          
    
    
    def sampleClusteredPointsInMask(self):
        points = self.getPointsInMask()
        self.clusterCenters = random.sample(points, self.numberOfClusters)
        self.points = [random.choice(self.clusterCenters) for _ in range(self.numberOfSamples)]
        self.addRandomShiftToPoints(self.maxDistFromClusterCenter)
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " clustered points from the " + str(len(points)) + " points in the mask in " + str(len(self.clusterCenters)) + " clusters.")  
               
  
    def sampleUniformRandomPointsInImage(self):
        N = self.width * self.height * self.depth
        sampleIndices = random.sample(xrange(N), self.numberOfSamples)
        self.points = self.indicesToCoordinates(sampleIndices)
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " uniformly distributed points from the " + str(N) + " points in the image.")
    
    
    def sampleDispersedPointsInImage(self):
        N = self.width * self.height * self.depth
        delta = N / self.numberOfSamples
        sampleIndices = [int(math.floor(i*delta)) for i in range(0, self.numberOfSamples)]
        self.points = self.indicesToCoordinates(sampleIndices)
        IJ.log("Randomly selected " + str(len(self.points)) + " dispersed points from the " + str(N) + " points in the image with max. grid distance = " + str(self.maxDistFromGrid) + ".")
               
    
    def sampleClusteredPointsInImage(self):
        N = self.width * self.height * self.depth
        sampleIndices = random.sample(xrange(N), self.numberOfClusters)
        self.clusterCenters = self.indicesToCoordinates(sampleIndices)
        self.points = [random.choice(self.clusterCenters) for _ in range(self.numberOfSamples)]
        self.addRandomShiftToPoints(self.maxDistFromClusterCenter)
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " clustered points from the " + str(N) + 
               " points in the image in " + str(len(self.clusterCenters)) + " clusters.")
  
  
    def addRandomShiftToPoints(self, maxDist):
        newPoints = [0] * len(self.points)
        maxTrials = 1000
        for index, point in enumerate(self.points):
            if self.mask:
                stack = self.mask.getStack()
            shiftedPoint = point
            trial = 0
            while (self.mask and (trial < maxTrials and (trial==0 or shiftedPoint in newPoints or stack.getVoxel(shiftedPoint[0], shiftedPoint[1], shiftedPoint[2]) == 0)) 
               or (not self.mask and (trial < maxTrials and (trial==0 or shiftedPoint in newPoints)))):
                shiftedPoint = self.getShiftedPoint(point, maxDist)                   
                if trial == maxTrials - 1:
                    IJ.log("no new shifted point found!")
                    shiftedPoint = point
                trial = trial + 1
            newPoints[index] = shiftedPoint
        self.points = newPoints
        
    
    def getShiftedPoint(self, point, maxDist):  
        x = random.random()
        y = random.random()
        z = random.random()
        d = random.uniform(0, maxDist)     
        if self.calibration.scaled():
            x = self.calibration.getX(x)
            y = self.calibration.getY(y)
            z = self.calibration.getZ(z)
        l = math.sqrt(x*x + y*y + z*z)
        x = (x / l) * d
        y = (y / l) * d
        z = (z / l) * d
        if self.calibration.scaled():
             x = point[0] + int(self.calibration.getRawX(x))
             y = point[1] + int(self.calibration.getRawY(y))
             z = point[2] + int(self.calibration.getRawZ(z))
        else:
             x = point[0] + int(round(x))
             y = point[1] + int(round(y))
             z = point[2] + int(round(z))
        x, y, z = (x % self.width, y % self.height, z % self.depth)              
        return (x, y, z)
          
    
    def indicesToCoordinates(self, indices):
        coordinates = []
        for index in indices:
            x = index % self.width
            y = (index // self.width) % self.height
            z = index // (self.width * self.height)
            coordinates.append((x, y, z))
        return coordinates
    
    
    def getPointsInMask(self):
        points = []
        bb = BoundingBox3D()
        labels = FindAllLabels().process(self.mask)
        calibration = self.mask.getCalibration()
        boxes = bb.analyzeRegions(self.mask.getStack(), labels, calibration)   
        stack = self.mask.getStack()
        for box in boxes:
            xMin = int(calibration.getRawX(box.getXMin()))
            xMax = int(calibration.getRawX(box.getXMax()))
            yMin = int(calibration.getRawY(box.getYMin()))
            yMax = int(calibration.getRawY(box.getYMax()))
            zMin = int(calibration.getRawZ(box.getZMin()))
            zMax = int(calibration.getRawZ(box.getZMax()))
            for x in range(xMin, xMax + 1):
                for y in range(yMin, yMax + 1):
                    for z in range(zMin, zMax + 1):
                        if stack.getVoxel(x, y, z) > 0:
                            points.append((x, y, z))
        return points
        
    
    def getEmptyImage(self):
        width, height, depth = self.width, self.height, self.depth
        if self.mask:
            width, height, _, depth, _ = self.mask.getDimensions()
        image = NewImage.createImage("Ground Truth Labels", 
                                                     width, 
                                                     height, 
                                                     depth, 
                                                     self.bitDepth, NewImage.FILL_BLACK)
        image.setCalibration(self.calibration)
        return image
        
    
    def createGroundTruthImage(self):
        lut = LUT(LutLoader.getLut( self.lutName ), 0, 255)
        self.groundTruthImage = self.getEmptyImage()
        label = 1
        stack = self.groundTruthImage.getStack()
        for point in self.points:
            stack.setVoxel(point[0], point[1], point[2], label)
            label = label + 1
        self.groundTruthImage.getChannelProcessor().setLut(lut)
        self.groundTruthImage.resetDisplayRange()
        
            
    def getGroundTruthTable(self):
        table = ResultsTable()
        points = self.points
        if self.calibration.scaled():
            points = self.getScaledPoints()
        for label, point in enumerate(points, start=1):
            table.addRow()
            table.addValue("X", point[0])
            table.addValue("Y", point[1])
            table.addValue("Z", point[2])
            table.addValue("Label", label)
        return table            
            
            
    def getCalibration(self):
        return self.calibration
        
        
    def setScale(self, xScale, yScale, zScale, unit):
        self.calibration.pixelWidth = xScale
        self.calibration.pixelHeight = yScale
        self.calibration.pixelDepth = zScale
        self.calibration.unit = unit
        
        
    def getScaledPoints(self):
        scaledPoints = [(self.calibration.getX(x), 
                        self.calibration.getY(y),
                        self.calibration.getZ(z)) for (x, y, z) in self.points]
        return scaledPoints
        
        
    def setMask(self, mask):
        if not mask:
            self.reset()
        else:
            self.mask = mask    
            self.width, self.height, _, self.depth, _ = self.mask.getDimensions()
            self.calibration = mask.getCalibration()
        
        
    def reset(self):
        self.width = 512
        self.height = 512
        self.depth = 64
        self.calibration = Calibration()
        self.mask = None
        
     
            
class NucleiGenerator:


    def __init__(self):
        pass