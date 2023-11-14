var IS_SCALED = true;
var X_COLUMN = "Centroid.X";
var Y_COLUMN = "Centroid.Y";
var Z_COLUMN = "Centroid.Z";
var CLUSTER_COLUMN = "C";
var TABLE = "clusters"

run("Duplicate...", "duplicate");
run("Select All");
setBackgroundColor(0, 0, 0);
run("Clear", "stack");
run("Select None");

X = Table.getColumn(X_COLUMN, TABLE);
Y = Table.getColumn(Y_COLUMN, TABLE);
Z = Table.getColumn(Z_COLUMN, TABLE);
C = Table.getColumn(CLUSTER_COLUMN, TABLE);
for (i = 0; i < Table.size(TABLE); i++) {
    x = X[i];
    y = Y[i];
    z = Z[i];
    if (IS_SCALED) {
        toUnscaled(x, y, z);
    }
    setSlice(z+1);
    setPixel(x, y, C[i]);
}
setOption("ScaleConversions", false);
run("16-bit");
run("glasbey on dark");
run("Morphological Filters (3D)", "operation=Dilation element=Cube x-radius=2 y-radius=2 z-radius=2");
 setSlice(1);
resetMinAndMax();