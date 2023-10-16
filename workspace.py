from fr.cnrs.mri.cialib.detection import SpotDetector
from ij import IJ

detector = SpotDetector()
image = IJ.getImage()
detector.run(image)