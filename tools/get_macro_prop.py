from ij import IJ
img = IJ.getImage()
macro = img.getProp("mri-cia.macro")
print(macro)