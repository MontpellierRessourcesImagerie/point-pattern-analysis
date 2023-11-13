var MAX_DIST = 9999999;

drawNearestNeighborConnections();

function drawNearestNeighborConnections() {
    inputStackID = getImageID();
    title = getTitle();
    Stack.getDimensions(width, height, channels, slices, frames);
    getVoxelSize(voxelWidth, voxelHeight, voxelDepth, unit);
    
    labelRed = Table.getColumn("Label", "red");
    xRed = Table.getColumn("X", "red");
    yRed = Table.getColumn("Y", "red");
    zRed = Table.getColumn("Z", "red");
    
    labelGreen = Table.getColumn("Label", "green");
    xGreen = Table.getColumn("X", "green");
    yGreen = Table.getColumn("Y", "green");
    zGreen = Table.getColumn("Z", "green");
    
    sourceLabel = Table.getColumn("LabelObj", "neighbors");
    destLabel = Table.getColumn("O2", "neighbors");
    distance = Table.getColumn("V2", "neighbors");

    size = sourceLabel.length;
    
    newImage(title + "-neighbors", "16-bit black", width, height, slices);
    setVoxelSize(voxelWidth, voxelHeight, voxelDepth, unit);
    for (row = 0; row < size; row++) {
        if (distance[row] > MAX_DIST) continue;
        sLabel = sourceLabel[row];
        sIndex = getIndexOfValue(labelRed, sLabel);
        dLabel = destLabel[row];
        if (dLabel == 0) continue;
        dIndex = getIndexOfValue(labelGreen, dLabel);
        x1 = xRed[sIndex];
        y1 = yRed[sIndex];
        z1 = zRed[sIndex];
        x2 = xGreen[dIndex];
        y2 = yGreen[dIndex];
        z2 = zGreen[dIndex];
        toUnscaled(x1, y1, z1);
        toUnscaled(x2, y2, z2);
        run("3D Draw Line", "size_x="+width+" size_y="+height+" size_z="+slices+" x0="+x1+" y0="+y1+" z0="+z1+" x1="+x2+" y1="+y2+" z1="+z2+" thickness=1.000 value=65535 display=Overwrite");
    }
    addImageAtEndOfStack(inputStackID, title+"-neighbors"); 
}


function getIndexOfValue(anArray, value) {
    for(i=0; i<anArray.length; i++) {
        if (anArray[i] == value) {
            return i;
        }
    }
    return -1;
}


function addImageAtEndOfStack(stackID, title) {
    selectImage(stackID);
    stackTitle = getTitle();
    Stack.getDimensions(width, height, channels, slices, frames);
    mergeString = "";
    if (channels>1) {
        run("Split Channels");
        for (i = 0; i < channels; i++) {
            mergeString += "c"+(i+1)+"=[C"+(i+1)+"-"+stackTitle+"] ";
        }
        mergeString += "c"+(channels+1)+"=["+title+"] create ";
    } else {
        mergeString = "c1=["+stackTitle+"] c2=["+title+"] create ";
    }
    run("Merge Channels...", mergeString);
}
