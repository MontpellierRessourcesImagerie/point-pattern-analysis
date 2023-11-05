from __future__ import division
import math
from ij import IJ
from fr.cnrs.mri.cialib.generator import SpotGenerator

gen = SpotGenerator()


cal = IJ.getImage().getCalibration()
gen.calibration = None

N = 3000
width = 1030
height = 1030
depth = 64

gen.width = width
gen.height = height
gen.depth = depth

width = cal.getX(width)
height = cal.getY(height)
depth = cal.getZ(depth)

dist = (1 / N) ** (1 / 3)

nrPerDim = 1 / dist

print("dist", dist, "nrPerDim", nrPerDim)

iDistX = int(math.floor(dist * width))
iDistY = int(math.floor(dist * height))
iDistZ = int(math.floor(dist * width))
print("iDist", iDistX, iDistY, iDistZ)


nrX = int(round(nrPerDim))
nrY = int(round(nrPerDim))
nrZ = int(round(nrPerDim))

print("N2", nrX * nrY * nrZ)

while nrX * nrY * nrZ < N:
    iDistX = iDistX - 1
#    iDistY = iDistY - 1
    nrX = int(round(width / iDistX))
#    nrY = int(round(height / iDistY))
    print("l1", nrX, nrY)
    print("N2", nrX * nrY * nrZ)

delta = 1
if nrX*nrY*nrZ > N:
    delta = -1
    
while nrX * nrY * nrZ > N:
    iDistX = iDistX + 1
#    iDistY = iDistY + 1
    nrX = int(round(width / iDistX))
#    nrY = int(round(height / iDistY))
    print("l2", nrX, nrY)
    print("N2", nrX * nrY * nrZ)


print("iDist", iDistX, iDistY, iDistZ)
print("nr", nrX, nrY, nrZ)

iDistX = int(cal.getRawX(iDistX))
iDistY = int(cal.getRawY(iDistY))
iDistZ = int(cal.getRawZ(iDistZ))

width = int(cal.getRawX(width))
height = int(cal.getRawY(height))
depth = int(cal.getRawZ(depth))

image = IJ.createImage("Untitled", "16-bit black", width, height, depth)
image.setCalibration(cal)
stack = image.getStack()
for i in range(0, nrX):
    x = int(math.floor(iDistX  )) + (i * iDistX)
    for j in range(0, nrY):
        y = int(math.floor(iDistY  )) + (j * iDistY)
        for k in range(0, nrZ):
            z = int(math.floor(iDistZ / 2 )) + (k * iDistZ)    
            point = (x, y, z)
            x, y, z = gen.getShiftedPoint(point, 2)
            stack.setVoxel(x, y, z, 65535)
           
image.show()
IJ.run("Morphological Filters (3D)", "operation=Dilation element=Cube x-radius=2 y-radius=2 z-radius=2")
IJ.run("Connected Components Labeling", "connectivity=6 type=[16 bits]");