from fr.cnrs.mri.cialib.detection import SpotDetector
from ij import IJ
from ij import ImagePlus
from ij.gui import ImageRoi
from ij.gui import Overlay
from ij.plugin import LutLoader
from ij.process import LUT 
from ij.process import StackStatistics
from inra.ijpb.binary.conncomp import FloodFillComponentsLabeling3D
from inra.ijpb.morphology.strel import BallStrel

lutName = "glasbey on dark"
lut = LUT(LutLoader.getLut(lutName ), 0, 255)
detector = SpotDetector()
image = IJ.getImage()
roi = image.getRoi()
print(roi)
detector.run(image)
labels = detector.spotImage.duplicate()
floodFiller = FloodFillComponentsLabeling3D(6, 16)
res = floodFiller.computeResult(labels.getStack())
labelsStack = res.labelMap
strel = BallStrel.fromRadius(2)
labelsStack = strel.dilation(labelsStack)
resImage = ImagePlus("labels", labelsStack)
resImage.getChannelProcessor().setLut(lut)
resImage.resetDisplayRange()
rois = []
for i in range(1, labelsStack.getSize()+1):
    roi = ImageRoi(roi.getBounds().x, roi.getBounds().y, labelsStack.getProcessor(i))
    rois.append(roi)
overlay = Overlay.createStackOverlay(rois)
image.setOverlay(overlay)

