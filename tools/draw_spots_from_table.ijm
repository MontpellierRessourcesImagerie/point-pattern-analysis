
for (i = 1; i < nResults; i++) {
    x = getResult("X", i);
    y = getResult("Y", i);
    z = getResult("Z", i);
    c = getResult("C", i);
    toUnscaled(x, y, z);
    setSlice(z+1);
    setPixel(x, y, c);
}

