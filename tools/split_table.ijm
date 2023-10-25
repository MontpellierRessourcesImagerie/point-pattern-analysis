NAME = "green_spots_clustered-001";
Table.create(NAME);
counter = 0;
for (i = 1; i < nResults; i = i + 2) {
    x = getResult("X", i);
    y = getResult("Y", i);
    z = getResult("Z", i);
    label = getResult("Label", i);
    Table.set("X", counter, x);
    Table.set("Y", counter, y);
    Table.set("Z", counter, z);
    Table.set("Label", counter, label);
    counter++;
}
