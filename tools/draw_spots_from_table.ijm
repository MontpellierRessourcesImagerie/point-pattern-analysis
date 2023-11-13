run("Duplicate...", "duplicate");
run("Select All");
setBackgroundColor(0, 0, 0);
run("Clear", "stack");
run("Select None");
title = Table.title
title = File.getNameWithoutExtension(title);
rename(title);

X = Table.getColumn("axis-2");
Y = Table.getColumn("axis-1");
Z = Table.getColumn("axis-0");

for (i = 0; i < Table.size; i++) {
    x = X[i];
    y = Y[i];
    z = Z[i];
    //toUnscaled(x, y, z);
    setSlice(z+1);
    setPixel(x, y, i+1);
}
setOption("ScaleConversions", false);
run("16-bit");
run("glasbey on dark");
run("Morphological Filters (3D)", "operation=Dilation element=Cube x-radius=2 y-radius=2 z-radius=2");
 setSlice(1);
resetMinAndMax();