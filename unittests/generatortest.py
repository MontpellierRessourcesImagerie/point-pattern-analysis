import sys
import unittest
from ij.gui import NewImage
from fr.cnrs.mri.cialib.generator import SpotGenerator


class SpotGeneratorTest(unittest.TestCase):


    def setUp(self):
        unittest.TestCase.setUp(self)
        self.generator = SpotGenerator()
        self.generator.width = 16
        self.generator.height = 16
        self.generator.depth = 8
        self.generator.numberOfSamples = 16
        
   
    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def testSampleUniformRandomPointsNoMask(self):
        self.generator.sampleUniformRandomPoints()
        
        # test if the right number of points has been sampled
        self.assertEquals(self.generator.numberOfSamples, len(self.generator.points))

        # test if the first sample has 3 coordinates
        self.assertEquals(3, len(self.generator.points[0]))
        
        # assert that there are no duplicates in the samples
        self.assertEquals(len(set(self.generator.points)), len(self.generator.points))
        

    def testSampleUniformRandomPointsWithMask(self):
        self.createMask()
        self.generator.sampleUniformRandomPoints()
        
        # test if the right number of points has been sampled
        self.assertEquals(self.generator.numberOfSamples, len(self.generator.points))
        
        # test if the first sample has 3 coordinates
        self.assertEquals(3, len(self.generator.points[0]))
        
        # assert that there are no duplicates in the samples
        self.assertEquals(len(set(self.generator.points)), len(self.generator.points))
        
        # assert all sampled points are inside of the mask
        stack = self.generator.mask.getStack()
        for point in self.generator.points:
            self.assertEquals(255, stack.getVoxel(point[0], point[1], point[2]))
        
        # assert no points outside of the mask have been sampled
        count = 0
        for x in range(self.generator.width):
            for y in range(self.generator.height):
                for z in range(self.generator.depth):
                    if stack.getVoxel(x, y, z) == 0:
                        self.assertTrue(not (x, y, z) in self.generator.points)
                        count = count + 1
        self.assertTrue(count > 0)
                        

    def createMask(self):
        self.generator.mask = NewImage.createByteImage("mask", self.generator.width, 
                                                               self.generator.height, 
                                                               self.generator.depth,
                                                               NewImage.FILL_BLACK)
        xrange = range(4, 12)
        yrange = range(4, 12)
        zrange = range(2, 6)
        stack = self.generator.mask.getStack()
        for x in xrange:
            for y in yrange:
                for z in zrange:        
                    stack.setVoxel(x, y, z, 255)                                                     
        
    
    
def suite():
    suite = unittest.TestSuite()

    suite.addTest(SpotGeneratorTest('testSampleUniformRandomPointsNoMask'))
    suite.addTest(SpotGeneratorTest('testSampleUniformRandomPointsWithMask'))
    return suite


def main(): 
    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    runner.run(suite())



if __name__ == "__main__":
    main()    