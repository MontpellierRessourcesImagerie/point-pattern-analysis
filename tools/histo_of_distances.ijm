DISTS = Table.getColumn("dist. to centroid", "Results");
histogram = newArray(225);
for (i = 0; i < DISTS.length; i++) {
    histogram[floor(DISTS[i])] = histogram[floor(DISTS[i])] + 1;
}
for (i = 1; i < histogram.length; i++) {
    histogram[i] = (histogram[i] + histogram[i-1]);
}
for (i = 1; i < histogram.length; i++) {
    histogram[i] = (histogram[i] / histogram[histogram.length-1]);
}
xValues = Array.getSequence(histogram.length);
Plot.create("CFH", "dist.", "sum of counts", xValues, histogram);4
Plot.show();

hist2 = newArray(225/5);
xValues = newArray(225/5);
for (i = 0; i < hist2.length; i++) {
    hist2[i] = (histogram[5*(i+1)-1] - histogram[5*i]) * 156;
    xValues[i] = 5*i;
}
Plot.create("HISTO", "dist.", "count", xValues, hist2);
Plot.show();
