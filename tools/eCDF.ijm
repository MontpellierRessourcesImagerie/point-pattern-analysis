TABLE = "histo";
count = Table.getColumn("count", TABLE);
r = Table.getColumn("bin start", TABLE);
lambda = 1; //(4/3)*PI;
B = lambda * r[r.length-1] * r[r.length-1] * r[r.length-1];
nSquared = count.length*count.length;
for (i = 1; i < count.length; i++) {
    count[i] = count[i] + count[i-1];
}
for (i = 0; i < count.length; i++) {
    count[i] = sqrt((( B / nSquared) * count[i]) / PI) - r[i];
}
Table.setColumn("acc", count);