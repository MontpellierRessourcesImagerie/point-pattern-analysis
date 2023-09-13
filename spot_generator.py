from __future__ import division
import random
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
        
        
    def sampleUniformRandomPoints(self):
        if mask:
            self.sampleUniformRandomPointsInMask()
        else:
            self.sampleUniformRandomPointsInImage()
            
           
    def sampleUniformRandomPointsInMask(self):
        points = self.getPointsInMask()
        sampleIndices = random.randrange(len(points))
        self.points = [points[i] for i in sampleIndices]
        
        
    def sampleUniformRandomPointsInImage(self):
        sampleIndices = random.randrange(self.width * self.height * self.depth)
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
        label = 65535
        if self.is8Bit():
            label = 255
        boxes = bb.analyzeRegions(self.mask, [label], self.mask.getCalibration())
        for box in boxes:
            for x in range(box.getXMin(), box.getXMax()+1):
                for y in range(box.getYMin(), box.getYMax()+1):
                    for z in range(box.getZMin(), box.getZMax()+1):
                        points.append((x, y, z))
        return points
        
        
    def is8Bit(self):
        return self.bitDepth == 8
        
        
    def is16Bit(self):
        return self.bitDepth == 16