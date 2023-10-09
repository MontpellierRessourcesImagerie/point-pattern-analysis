from __future__ import division
import math
from ij import IJ


N = 1000
width = 1024
height = 1024
depth = 128

dist = (1 / N) ** (1 / 3)

nrPerDim = 1 / dist

print("dist", dist, "nrPerDim", nrPerDim)

iDistX = int(math.floor(dist * width))
iDistY = int(math.floor(dist * height))
iDistZ = int(math.floor(dist * depth))
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

image = IJ.createImage("Untitled", "16-bit black", width, height, depth)
stack = image.getStack()
for i in range(0, nrX):
    x = int(math.floor(iDistX / 2 )) + (i * iDistX)
    for j in range(0, nrY):
        y = int(math.floor(iDistY / 2 )) + (j * iDistY)
        for k in range(0, nrZ):
            z = int(math.floor(iDistZ / 2 )) + (k * iDistZ)    
            stack.setVoxel(x, y, z, 65535)
image.show()           
IJ.run("Morphological Filters (3D)", "operation=Dilation element=Cube x-radius=2 y-radius=2 z-radius=2")
IJ.run("Connected Components Labeling", "connectivity=6 type=[16 bits]");