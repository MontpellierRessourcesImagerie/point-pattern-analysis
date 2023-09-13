from __future__ import division
import random
from ij.gui import NewImage
from inra.ijpb.label.edit import FindAllLabels
from inra.ijpb.measure.region3d import BoundingBox3D


class SpotGenerator:


    def __init__(self):
        self.width = 512
        self.height = 512
        self.depth = 64
        self.bitDepth = 16
        self.mask = None
        self.numberOfSamples = 1000
        self.points = None
        self.image = None
        self.mask = None
        self.groundTruthImage = None
        
        
    def sampleUniformRandomPoints(self):
        if self.mask:
            self.sampleUniformRandomPointsInMask()
        else:
            self.sampleUniformRandomPointsInImage()
            
           
    def sampleUniformRandomPointsInMask(self):
        points = self.getPointsInMask()
        self.points = random.sample(points, self.numberOfSamples)
        
        
    def sampleUniformRandomPointsInImage(self):
        sampleIndices = random.sample(xrange(self.width * self.height * self.depth), self.numberOfSamples)
        self.points = self.indicesToCoordinates(sampleIndices)
        
    
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
        
        
    def createGroundTruthImage(self):
        self.groundTruthImage = NewImage.createImage("Ground Truth Labels", 
                                                     self.width, 
                                                     self.height, 
                                                     self.depth, 
                                                     self.bitDepth, NewImage.FILL_BLACK)
        label = 1
        stack = self.groundTruthImage.getStack()
        for point in self.points:
            stack.setVoxel(point[0], point[1], point[2], label)
            label = label + 1