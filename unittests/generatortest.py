import sys
import unittest
from ij.gui import NewImage
from inra.ijpb.label.edit import FindAllLabels
from fr.cnrs.mri.cialib.generator import UniformRandomSpotGenerator
from fr.cnrs.mri.cialib.generator import DispersedRandomSpotGenerator
from fr.cnrs.mri.cialib.generator import ClusteredRandomSpotGenerator

class SpotGeneratorTest(unittest.TestCase):


    def setUp(self):
        unittest.TestCase.setUp(self)
      
      
    def setupGenerator(self, generator):
        generator.width = 16
        generator.height = 16
        generator.depth = 8
        generator.numberOfSamples = 16
        return generator
        
   
    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def testSampleUniformRandomPointsNoMask(self):
        generator = self.setupGenerator(UniformRandomSpotGenerator())
        generator.sample()
        
        # test if the right number of points has been sampled
        self.assertEquals(generator.numberOfSamples, len(generator.points))

        # test if the first sample has 3 coordinates
        self.assertEquals(3, len(generator.points[0]))
        
        # assert that there are no duplicates in the samples
        self.assertEquals(len(set(generator.points)), len(generator.points))
        

    def testSampleUniformRandomPointsWithMask(self):
        generator = self.createMask(self.setupGenerator(UniformRandomSpotGenerator()))
        generator.sample()
        
        # test if the right number of points has been sampled
        self.assertEquals(generator.numberOfSamples, len(generator.points))
        
        # test if the first sample has 3 coordinates
        self.assertEquals(3, len(generator.points[0]))
        
        # assert that there are no duplicates in the samples
        self.assertEquals(len(set(generator.points)), len(generator.points))
        
        # assert all sampled points are inside of the mask
        stack = generator.mask.getStack()
        for point in generator.points:
            self.assertEquals(255, stack.getVoxel(point[0], point[1], point[2]))
        
        # assert no points outside of the mask have been sampled
        count = 0
        for x in range(generator.width):
            for y in range(generator.height):
                for z in range(generator.depth):
                    if stack.getVoxel(x, y, z) == 0:
                        self.assertTrue(not (x, y, z) in generator.points)
                        count = count + 1
        self.assertTrue(count > 0)
                        

    def testSampleDispersedPointsNoMask(self):
        generator = self.setupGenerator(DispersedRandomSpotGenerator())
        generator.numberOfSamples = 100
        generator.sample()
    
        # test if the right number of points has been sampled
        self.assertEquals(generator.numberOfSamples, len(generator.points))
        
        generator.maxDistFromGrid = 3
        generator.sample()
        
        self.assertEquals(generator.numberOfSamples, len(generator.points))
        for x, y, z in generator.points:
            self.assertTrue(x >= 0)
            self.assertTrue(y >= 0)
            self.assertTrue(z >= 0)
            self.assertTrue(x < generator.width)
            self.assertTrue(y < generator.height)
            self.assertTrue(z < generator.depth)
       
        self.assertEquals(generator.numberOfSamples, len(set(generator.points)))
       
       
    def testSampleDispersedPointsWithMask(self):
        generator = self.createMask(self.setupGenerator(DispersedRandomSpotGenerator()))        
        generator.numberOfSamples = 25
        generator.sample()
    
        # test if the right number of points has been sampled
        self.assertEquals(generator.numberOfSamples, len(generator.points))
        for x, y, z in generator.points:
            pixelValue = generator.mask.getStack().getVoxel(x, y, z)
            self.assertTrue(pixelValue > 0)
           
        generator.maxDistFromGrid = 3
        generator.sample()
        for x, y, z in generator.points:
            pixelValue = generator.mask.getStack().getVoxel(x, y, z)
            self.assertTrue(pixelValue > 0)
        
        self.assertEquals(generator.numberOfSamples, len(set(generator.points)))
        
     
    def testSampleClusteredPointsNoMask(self):
        generator = self.setupGenerator(ClusteredRandomSpotGenerator())
        generator.numberOfClusters = 5
        generator.maxDistFromClusterCenter = 10
        generator.sample()
        
        # test if the right number of points has been sampled
        self.assertEquals(generator.numberOfSamples, len(generator.points))
        
        # assert that there are no duplicates in the samples
        self.assertEquals(len(set(generator.points)), len(generator.points))
    
    
    def testSampleClusteredPointsWithMask(self):
        generator = self.createMask(self.setupGenerator(ClusteredRandomSpotGenerator()))
        generator.numberOfSamples = 25
        generator.numberOfClusters = 3
        generator.maxDistFromClusterCenter = 20
        generator.sample()
        
        # test if the right number of points has been sampled
        self.assertEquals(generator.numberOfSamples, len(generator.points))
        
        # assert that there are no duplicates in the samples
        self.assertEquals(len(set(generator.points)), len(generator.points))
    
    
    def testCreateGroundTruthImage(self):
        generator = self.setupGenerator(UniformRandomSpotGenerator())
        generator.sample()
        generator.createGroundTruthImage()
        labels = FindAllLabels().process(generator.groundTruthImage)
        
        # The ground-truth image should contain one label for each point
        self.assertEquals(len(generator.points), len(labels))

        # The label of the first point must be one
        self.assertEquals(1, min(labels))

        # The label of the last point corresponds to the number of points
        self.assertEquals(len(generator.points), max(labels))
        
    
    def testGetGroundTruthTableNoScale(self):
        generator = self.setupGenerator(UniformRandomSpotGenerator())
        generator.sample()
        table = generator.getGroundTruthTable()
        
        # There should be one row per sample
        self.assertEquals(len(generator.points), table.size())
        
        # Coordinates in the table should correspond to the sampled coordinates
        for row, point in enumerate(generator.points):
            self.assertEquals(point, (int(table.getValue("X", row)), 
                                      int(table.getValue("Y", row)),
                                      int(table.getValue("Z", row))))
                                      
                                      
    def testGetGroundTruthTableWithScale(self):
        generator = self.setupGenerator(UniformRandomSpotGenerator())        
        generator.setScale(0.2, 0.2, 0.6, chr(181) + "m")
        generator.sample()
        table = generator.getGroundTruthTable()
        
        # There should be one row per sample
        self.assertEquals(len(generator.points), table.size())
        
        # Coordinates in the table should correspond to the sampled coordinates in physical units
        for row, point in enumerate(generator.getScaledPoints()):
            self.assertEquals(point, (table.getValue("X", row), 
                                      table.getValue("Y", row),
                                      table.getValue("Z", row)))
                                      
    
    def createMask(self, generator):
        generator.mask = NewImage.createByteImage("mask", generator.width, 
                                                          generator.height, 
                                                          generator.depth,
                                                          NewImage.FILL_BLACK)
        xrange = range(4, 12)
        yrange = range(4, 12)
        zrange = range(2, 6)
        stack = generator.mask.getStack()
        for x in xrange:
            for y in yrange:
                for z in zrange:        
                    stack.setVoxel(x, y, z, 255)                                                     
        return generator
        
    
def suite():
    suite = unittest.TestSuite()

    suite.addTest(SpotGeneratorTest('testSampleUniformRandomPointsNoMask'))
    suite.addTest(SpotGeneratorTest('testSampleUniformRandomPointsWithMask'))
    suite.addTest(SpotGeneratorTest('testSampleDispersedPointsNoMask'))
    suite.addTest(SpotGeneratorTest('testSampleDispersedPointsWithMask'))
    suite.addTest(SpotGeneratorTest('testSampleClusteredPointsNoMask'))
    suite.addTest(SpotGeneratorTest('testSampleClusteredPointsWithMask'))
    suite.addTest(SpotGeneratorTest('testCreateGroundTruthImage'))
    suite.addTest(SpotGeneratorTest('testGetGroundTruthTableNoScale'))
    suite.addTest(SpotGeneratorTest('testGetGroundTruthTableWithScale'))
    return suite


def main(): 
    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    runner.run(suite())



if __name__ == "__main__":
    main()