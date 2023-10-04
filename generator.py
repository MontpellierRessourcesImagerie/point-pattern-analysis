###############################################################################################
##
## generator.py
##
## Create synthetic 3D spots and nuclei with random uniform, clustered or dispersed spatial distribution. 
## 
## (c) 2023 INSERM
##
## written by Volker Baecker at the MRI-Center for Image Analysis (MRI-CIA - https://www.mri.cnrs.fr/en/data-analysis.html)
##
## generator.py is free software under the MIT license.
## 
## MIT License
##
## Copyright (c) 2023 INSERM
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
## 
################################################################################################
from __future__ import division
import random
import math
from ij import IJ
from ij.gui import NewImage
from ij.measure import Calibration
from ij.measure import ResultsTable
from ij.plugin import LutLoader
from ij.plugin import ImageCalculator
from ij.process import LUT 
from ij.process import ImageConverter
from inra.ijpb.label.edit import FindAllLabels
from inra.ijpb.measure.region3d import BoundingBox3D
from inra.ijpb.morphology import Reconstruction3D
from inra.ijpb.morphology.filter import Erosion
from inra.ijpb.morphology.strel import DiskStrel
from inra.ijpb.label import RegionAdjacencyGraph
from mcib3d.geom import Vector3D
from mcib3d.geom import ObjectCreator3D


class SpotGenerator(object):


    def __init__(self):
        super(SpotGenerator, self).__init__()
        self.width = 512
        self.height = 512
        self.depth = 64
        self.calibration = Calibration()
        self.mask = None
        self.bitDepth = 16        
        self.numberOfSamples = 1000      
        self.points = None
        self.scaledPoints = None
        self.image = None
        self.groundTruthImage = None
        self.lutName = "glasbey on dark"
       

    def sample(self):
        if self.mask:
            self.sampleInMask()
        else:
            self.sampleInImage()
            
             
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
        


class UniformRandomSpotGenerator(SpotGenerator):

    
    def __init(self):
        super(UniformRandomSpotGenerator, self).__init__()
        

    def sampleInMask(self):
        points = self.getPointsInMask()       
        self.points = random.sample(points, self.numberOfSamples)
        self.calibration = self.mask.getCalibration()
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " uniformly distributed points from the " + str(len(points)) + " points in the mask.")  


    def sampleInImage(self):
        N = self.width * self.height * self.depth
        sampleIndices = random.sample(xrange(N), self.numberOfSamples)
        self.points = self.indicesToCoordinates(sampleIndices)
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " uniformly distributed points from the " + str(N) + " points in the image.")



class DispersedRandomSpotGenerator(SpotGenerator):


    def __init(self):
        super(DispersedRandomSpotGenerator, self).__init__()
        self.maxDistFromGrid = 0
        

    def sample(self):
        super(DispersedRandomSpotGenerator, self).sample()
        if self.maxDistFromGrid:
            self.addRandomShiftToPoints(self.maxDistFromGrid)
            
            
    def sampleInMask(self):
        pointsInMask = self.getPointsInMask()
        if len(pointsInMask) <= self.numberOfSamples:
            self.points = pointsInMask
        else:
            delta = len(pointsInMask) / self.numberOfSamples
            self.points = [pointsInMask[int(math.floor(i*delta))] for i in range(0, self.numberOfSamples)]
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " dispersed points from the " + str(len(pointsInMask)) + " points in the mask.")    
               
               
    def sampleInImage(self):
        N = self.width * self.height * self.depth
        delta = N / self.numberOfSamples
        sampleIndices = [int(math.floor(i*delta)) for i in range(0, self.numberOfSamples)]
        self.points = self.indicesToCoordinates(sampleIndices)
        IJ.log("Randomly selected " + str(len(self.points)) + " dispersed points from the " + str(N) + " points in the image with max. grid distance = " + str(self.maxDistFromGrid) + ".")               



class ClusteredRandomSpotGenerator(SpotGenerator):


    def __init__(self):
        super(ClusteredRandomSpotGenerator, self).__init__()
        self.numberOfClusters = 50
        self.maxDistFromClusterCenter = 90
        self.clusterCenters = None  
    
    
    def sampleInMask(self):
        points = self.getPointsInMask()
        self.clusterCenters = random.sample(points, self.numberOfClusters)
        self.points = [random.choice(self.clusterCenters) for _ in range(self.numberOfSamples)]
        self.addRandomShiftToPoints(self.maxDistFromClusterCenter)
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " clustered points from the " + str(len(points)) + " points in the mask in " + str(len(self.clusterCenters)) + " clusters.")  
               

    def sampleInImage(self):
        N = self.width * self.height * self.depth
        sampleIndices = random.sample(xrange(N), self.numberOfClusters)
        self.clusterCenters = self.indicesToCoordinates(sampleIndices)
        self.points = [random.choice(self.clusterCenters) for _ in range(self.numberOfSamples)]
        self.addRandomShiftToPoints(self.maxDistFromClusterCenter)
        IJ.log("Randomly selected " + str(len(self.points)) + 
               " clustered points from the " + str(N) + 
               " points in the image in " + str(len(self.clusterCenters)) + " clusters.")



class NucleiGenerator:


    def __init__(self):
        self.spotGenerator = SpotGenerator()
        self.spotGenerator.setScale(0.2, 0.2, 0.7, "micron")
        self.spotGenerator.width = 1024
        self.spotGenerator.height = 1024
        self.spotGenerator.depth = 128
        self.spotGenerator.numberOfSamples = 500
        self.xRadiusMean = 4         
        self.xRadiusStddev = 1
        self.yRadiusMean = 4         
        self.yRadiusStddev = 1
        self.zRadiusMean = 4         
        self.zRadiusStddev = 1
        self.saltAndPepper = 1
        self.erosionRadius = 1
        self.nuclei = []
        self.groundTruthImage = None
        
        
    def sampleUniformRandomNuclei(self):
        self.spotGenerator.sampleUniformRandomPoints()
        self.nuclei = self.sample()
        
        
    def sampleDispersedNuclei(self):
        self.spotGenerator.sampleDispersedPoints()
        self.nuclei = self.sample()
    
    
    def sampleClusteredNuclei(self):
        self.spotGenerator.sampleClusteredPoints()
        self.nuclei = self.sample()
        
           
    def sample(self):
        radii = self.sampleRadii()
        orientations = self.sampleOrientations()
        nuclei = []
        for position, radius, orientation in zip(self.spotGenerator.points, radii, orientations):
            nucleus = Nucleus(self.spotGenerator.getCalibration())
            nucleus.setRawPosition(position[0], position[1], position[2])
            nucleus.setRadius(radius[0], radius[1], radius[2])
            nucleus.orientation = orientation
            nuclei.append(nucleus)
        return nuclei
            
    
    def sampleRadii(self):
        radiusX = [random.normalvariate(self.xRadiusMean, self.xRadiusStddev) for i in range(self.numberOfSamples())]
        radiusY = [random.normalvariate(self.yRadiusMean, self.yRadiusStddev) for i in range(self.numberOfSamples())]
        radiusZ = [random.normalvariate(self.zRadiusMean, self.zRadiusStddev) for i in range(self.numberOfSamples())]
        radii =  zip(radiusX, radiusY, radiusZ)    
        return radii
        
      
    def sampleOrientations(self):
        rx = [random.random() for _ in range(self.numberOfSamples())]
        ry = [random.random() for _ in range(self.numberOfSamples())]
        orientationVectors = [Vector3D(rx[i], ry[i], 0).getNormalizedVector() for i in range(self.numberOfSamples())]   
        return orientationVectors


    def numberOfSamples(self):
        return self.spotGenerator.numberOfSamples


    def createEllipsoidPhantoms(self):
        label = 1
        objectCreator = ObjectCreator3D(self.groundTruthImage.getStack())
        objectCreator.setCalibration(self.spotGenerator.getCalibration())
        for nucleus in self.nuclei:
            nucleus.draw(objectCreator, label)
            label = label + 1
            
            
    def addNuclearPores(self):
        labelImage = self.groundTruthImage.duplicate()        
        IJ.setRawThreshold(self.groundTruthImage, 1, pow(2, self.spotGenerator.bitDepth) - 1)
        IJ.run(self.groundTruthImage, "Convert to Mask", "background=Dark black")
        for i in range(self.saltAndPepper):
            IJ.run(self.groundTruthImage, "Salt and Pepper", "stack")
        IJ.run(self.groundTruthImage, "Remove Outliers...", "radius=2 threshold=50 which=Bright stack");
        stack = Reconstruction3D.fillHoles(self.groundTruthImage.getStack())
        erosion = Erosion(DiskStrel.fromRadius(self.erosionRadius))
        stack = erosion.process(stack)   
        self.groundTruthImage.setStack(stack)
        IJ.run(self.groundTruthImage, "Divide...", "value=255.000 stack")
        self.__convertBackToBitDepth()
        ImageCalculator.run(self.groundTruthImage, labelImage, "Multiply stack")


    def __convertBackToBitDepth(self):
        converter = ImageConverter(self.groundTruthImage)
        if self.spotGenerator.bitDepth in [12, 16]:
            converter.convertToGray16()
        if self.spotGenerator.bitDepth == 8:
            converter.convertToGray8()
        if self.spotGenerator.bitDepth == 32:
            converter.convertToGray32()
    
    
    def createGroundTruthImage(self):
        lut = LUT(LutLoader.getLut( self.spotGenerator.lutName ), 0, 255)
        self.groundTruthImage = self.spotGenerator.getEmptyImage()
        self.createEllipsoidPhantoms()
        self.addNuclearPores()
        self.groundTruthImage.getChannelProcessor().setLut(lut)
        self.groundTruthImage.resetDisplayRange()
        
            
    def getGroundTruthTable(self):
        table = ResultsTable()
        for label, nucleus in  enumerate(self.nuclei, start = 1):
            nucleus.addToTable(table, label)
        return table     


    def removeNuclei(self, indices):
        self.nuclei = [self.nuclei[i] for i in range(len(self.nuclei)) if i not in indices]
    
    
    def makeNonOverlapping(self):
        self.createGroundTruthImage()
        image = self.groundTruthImage
        rag = RegionAdjacencyGraph.computeAdjacencies(image)
        rag = [elem.label1-1 for elem in list(rag)]
        rag = set(rag)
        self.removeNuclei(rag)
        self.createGroundTruthImage()
        missing = self.numberOfSamples() - len(self.nuclei)
        trial = 0
        while missing > 0 and trial < 10:
            IJ.log("resampling overlapping nuclei...: trial=" + str(trial) +" missing="+str(missing))
            gen2 = NucleiGenerator()
            gen2.spotGenerator.numberOfSamples = missing
            # gen2.spotGenerator.points = gen.spotGenerator.points
            # gen2.sampleClusteredNuclei()
            gen2.sampleUniformRandomNuclei()
            self.nuclei = self.nuclei + gen2.nuclei
            self.createGroundTruthImage()
            image = self.groundTruthImage            
            rag = RegionAdjacencyGraph.computeAdjacencies(image)
            rag = [elem.label1-1 for elem in list(rag)]
            rag = set(rag)      
            self.removeNuclei(rag)
            missing = self.numberOfSamples() - len(self.nuclei)
            self.createGroundTruthImage()
            trial = trial + 1

            
            
class Nucleus:

    
    def __init__(self, calibration):        
        self.position = None
        self.radius = None
        self.rawPosition = None
        self.rawRadius = None
        self.orientation = None
        self.calibration = calibration
        
        
    def setPosition(self, x, y, z):
        self.position = x, y, z
        self.rawPosition = self.calibration.getRawX(x), self.calibration.getRawY(y), self.calibration.getRawZ(z)
        
   
    def setRawPosition(self, x, y, z):
        self.rawPosition = x, y, z
        self.position = self.calibration.getX(x), self.calibration.getY(y), self.calibration.getZ(z)
    
    
    def getPosition(self):
        return self.position
        
        
    def getRawPosition(self):
        return self.rawPosition
        
        
    def setRadius(self, xr, yr, zr):
        self.radius = xr, yr, zr
        self.rawRadius = self.calibration.getRawX(xr), self.calibration.getRawY(yr), self.calibration.getRawZ(zr)
        
        
    def getRadius(self):
        return self.radius
       
       
    def getRawRadius(self):
        return self.rawRadius
    
    
    def getOrientation(self):
        return self.orientation
    
    
    def getX(self):
        return self.position[0]
        
        
    def getY(self):
        return self.position[1]


    def getZ(self):
        return self.position[2]
        
        
    def getRadiusX(self):
        return self.radius[0]
        
    
    def getRadiusY(self):
        return self.radius[1]
        
        
    def getRadiusZ(self):
        return self.radius[2]
        
        
    def draw(self, objectCreator, label):
        objectCreator.createEllipsoidAxesUnit(self.position[0],
                                              self.position[1],
                                              self.position[2],
                                              self.radius[0],
                                              self.radius[1], 
                                              self.radius[2],
                                              label, 
                                              self.orientation, 
                                              self.orientation.getRandomPerpendicularVector(), 
                                              False)
    
    
    def addToTable(self, table, label):
        table.addRow()
        table.addValue("X", self.getX())
        table.addValue("Y", self.getY())
        table.addValue("Z", self.getZ())
        table.addValue("Label", label)
        table.addValue("rx", self.getRadiusX())
        table.addValue("ry", self.getRadiusY())
        table.addValue("rz", self.getRadiusZ())
        table.addValue("ox", self.orientation.x)
        table.addValue("oy", self.orientation.y)
        table.addValue("oz", self.orientation.z)
        
    
    def __str__(self):
        return self.__repr__()
    
    
    def __repr__(self):
        roundedRadius = (round(self.radius[0], 2), round(self.radius[1], 2), round(self.radius[2], 2))
        reprString = u"" + self.__class__.__name__ + "(p=" + str(self.position) + ", r="+str(roundedRadius)+", o="+str(self.orientation) +")"
        reprString = reprString.encode('ascii',errors='ignore')
        return reprString
        