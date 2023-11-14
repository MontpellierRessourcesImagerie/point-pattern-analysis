var IS_SCALED = false;
var X_COLUMN = "axis-2";
var Y_COLUMN = "axis-1";
var Z_COLUMN = "axis-0";

run("Duplicate...", "duplicate");
run("Select All");
setBackgroundColor(0, 0, 0);
run("Clear", "stack");
run("Select None");
title = Table.title
title = File.getNameWithoutExtension(title);
rename(title);

X = Table.getColumn(X_COLUMN);
Y = Table.getColumn(Y_COLUMN);
Z = Table.getColumn(Z_COLUMN);

for (i = 0; i < Table.size; i++) {
    x = X[i];
    y = Y[i];
    z = Z[i];
    if (IS_SCALED) {
        toUnscaled(x, y, z);
    }
    setSlice(z+1);
    setPixel(x, y, i+1);
}
setOption("ScaleConversions", false);
run("16-bit");
run("glasbey on dark");
run("Morphological Filters (3D)", "operation=Dilation element=Cube x-radius=2 y-radius=2 z-radius=2");
 setSlice(1);
resetMinAndMax();