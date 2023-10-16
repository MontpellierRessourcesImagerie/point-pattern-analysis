Dialog.create("3D spot detection");
ij_radius = 3;
ij_threshold = 5;
Dialog.addNumber("Sigma of the LoG filter [pixel]: ", ij_radius);
Dialog.addNumber("Threshold: ", ij_threshold);
Dialog.show()
ij_radius = Dialog.getNumber();
ij_threshold = Dialog.getNumber();

run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");
        
// Processing
run("Set Measurements...", "  center stack redirect=None decimal=2");
run("FeatureJ Laplacian", "compute smoothing="+d2s(ij_radius,2));
rename("Flt");
run("Minimum (3D)");
rename("Min");
imageCalculator("Subtract create stack", "Flt","Min");
setThreshold(0, 0);
run("Convert to Mask", "method=Default background=Dark");
rename("Msk");
selectImage("Flt");
setThreshold(-9999, ij_threshold);
run("Convert to Mask", "method=Default background=Dark");
imageCalculator("And stack", "Flt","Msk");
run("Analyze Particles...", "display clear stack");