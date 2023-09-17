from __future__ import division
import sys
import unittest
from fr.cnrs.mri.cialib.imaging import Gaussian
from fr.cnrs.mri.cialib.imaging import Microscope



class GaussianTest(unittest.TestCase):


    def setUp(self):
        unittest.TestCase.setUp(self)
    
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
        
    def testGaussian(self):
        offset = 1
        height = 10
        mean = 0
        stdDev = 5
        gaussian = Gaussian(offset, height, mean, stdDev)
        self.assertEquals(offset, gaussian.offset)
        self.assertEquals(height, gaussian.height)
        self.assertEquals(mean, gaussian.mean)
        self.assertEquals(stdDev, gaussian.stdDev)
        

    def testF(self):
        # Test if the value at mean equals the height for offset 0
        gaussian = Gaussian(0, 1, 0, 1)         
        self.assertEquals(1, gaussian.f(0))
        
        # Test if the value at mean equals the height for offset different from 0
        gaussian = Gaussian(0.5, 1, 0, 1)
        self.assertEquals(1, gaussian.f(0))
    
        # Test if value left of the mean is smaller than height
        self.assertTrue(gaussian.f(-1) < 1)
        
        # Test if value right of the mean is smaller than height
        self.assertTrue(gaussian.f(1) < 1)
        
        # Test that the maximal height is at the mean with mean different from 0
        gaussian = Gaussian(0, 1, 5, 1)         
        self.assertEquals(1, gaussian.f(5))
        
        # Test that the gaussian for a bif value is still not below the offset
        gaussian = Gaussian(0.5, 1, 5, 1)   
        self.assertTrue(gaussian.f(10000000) >= 0.5)
        
        
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(GaussianTest('testGaussian'))
    suite.addTest(GaussianTest('testF'))
    return suite


def main(): 
    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    runner.run(suite())



if __name__ == "__main__":
    main()    