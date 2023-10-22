from fr.cnrs.mri.cialib.detection import SpotDetector
from ij import IJ
from ij import ImagePlus
from ij.gui import ImageRoi
from ij.gui import Overlay
from ij.plugin import LutLoader
from ij.process import LUT 
from inra.ijpb.binary.conncomp import FloodFillComponentsLabeling3D
from inra.ijpb.morphology.strel import BallStrel

lutName = "glasbey on dark"
lut = LUT(LutLoader.getLut(lutName ), 0, 255)
detector = SpotDetector()
image = IJ.getImage()
roi = image.getRoi()
detector.run(image)
labels = detector.spotImage.duplicate()
floodFiller = FloodFillComponentsLabeling3D(6, 16)
res = floodFiller.computeResult(labels.getStack())
labelsStack = res.labelMap
strel = BallStrel.fromRadius(2)
labelsStack = strel.dilation(labelsStack)
resImage = ImagePlus("labels", labelsStack)
resImage.getChannelProcessor().setLut(lut)
resImage.setDisplayRange(0, len(detector.spots))
rois = []
x = 0
y = 0
if roi:
    x = roi.getBounds().x
    y = roi.getBounds().y
for i in range(1, resImage.getStack().getSize()+1):
    roi = ImageRoi(x, y, resImage.getStack().getProcessor(i))
    roi.setOpacity(75)
    roi.setZeroTransparent(True)
    rois.append(roi)
overlay = Overlay.createStackOverlay(rois)
overlay.translate(x, y)
image.setOverlay(overlay)

