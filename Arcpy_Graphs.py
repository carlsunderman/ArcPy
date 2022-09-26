import arcpy,os,glob
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline

mxd = arcpy.mapping.MapDocument(r"<MXD file with Data Driven Pages>")
outputFolder = "C:/<ouput location>/"
# there should be a picture element on your page at the location where you want the graph inserted
pictureElementName = "<Picture Element Name>"
eleFieldFeature = "<Elevation Point Feature Class>"
eleField = "<Elevation Field>"
# distField can be whatever field you want for the X axis
distField = "<Distance Field>"

df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
pict = arcpy.mapping.ListLayoutElements(mxd, "PICTURE_ELEMENT", pictureElementName)[0]
lyr = arcpy.mapping.ListLayers(mxd, eleFieldFeature, df)[0]


for pageNum in range(1, mxd.dataDrivenPages.pageCount + 1):
    mxd.dataDrivenPages.currentPageID = pageNum
    # change this SeqId to match the field name that you have in the DDP featureclass
    # this is redundant, but it works all the same and I didn't feel like changing it. :)
    pageName = mxd.dataDrivenPages.pageRow.getValue("SeqId")
    # change this SeqId to match the field name that you have in the Elevation featureclass
    arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", ' "SeqId" = '+ repr(pageName))
    # create array of selected
    arr = arcpy.da.FeatureClassToNumPyArray(lyr, (eleField, distField))
    # set min and max for the graph from the array 
    mineleField = arr[eleField].min()
    maxeleField = arr[eleField].max()
    minStation = arr[distField].min()
    maxStation = arr[distField].max()
    # matplotlib stuff
    x = []
    y = []

    elevPNG = outputFolder+"\elev"+repr(pageNum)+".png"
    fig = plt.figure(figsize=(32, 2.8))
    
    table = lyr
    fields = [distField, eleField]
    with arcpy.da.SearchCursor(table, fields) as rows:
        for row in rows:
            x.append(row[0])
            y.append(row[1])


    # the next 7 lines generalize, smooth the line in case of missing data
    x_sm = np.array(x)
    y_sm = np.array(y)
    x_smooth = np.linspace(x_sm.min(), x_sm.max(),200)
    y_smooth = spline(x,y,x_smooth)
    # subtract/add 10 to the min max of the graph so elevation fits, can increase or decrease as you need
    plt.ylim((mineleField-10,maxeleField+10))
    plt.xlim((minStation,maxStation))
    plt.plot(x_smooth,y_smooth, color='red', linewidth=3)


    ## the next 3 is your X label, Y Label, and Graph Title
    plt.xlabel('Distance')
    plt.ylabel('Elevation')
    plt.title('Landscape Profile')
    plt.grid(True)
    fig.savefig(elevPNG,  bbox_inches='tight', dpi=(100))
    pict.sourceImage = elevPNG
    # end of matplotlib stuff 


    print "Exporting page {0} of {1}".format(str(mxd.dataDrivenPages.currentPageID), str(mxd.dataDrivenPages.pageCount))
    arcpy.mapping.ExportToPDF(mxd, outputFolder + str(pageName) + "_W_GRAPH.pdf", resolution=150, image_quality="NORMAL")
    plt.clf()
    plt.close()
    del fig
del mxd
