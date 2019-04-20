######################################################
######################################################
######################################################
##########                                  ##########         
##########  Station field is numeric        ##########
##########  X field is numeric (Longitude)  ##########  
##########  Y field is numeric (Latitude)   ##########
##########                                  ##########
##########  You may need to:                ##########
##########  pip install shapely geopandas   ##########
##########                                  ##########  
###################################################### 
###################################################### 
######################################################
######################################################

######## run alone ########
#csvFile = "reordertest.csv"
#stationField = "station"
#xField = "X"
#yField = "Y"
#outputFile= "myFile.shp"
## needed for arcgis http://spatialreference.org/
#outputcrs = 4326

######## Run In ArcGIS toolbox ########
##csvFile = arcpy.GetParameterAsText(0)
##stationField = arcpy.GetParameterAsText(1)
##xField = arcpy.GetParameterAsText(2)
##yField = arcpy.GetParameterAsText(3)
#### if shapefile, dont forget the .shp
##outputFile = arcpy.GetParameterAsText(4)
##outputcrs = arcpy.GetParameterAsText(5)

import pandas as pd
import numpy as np
import arcpy
from shapely.geometry import Point
import geopandas

df = pd.read_csv(csvFile)
df = df.replace('NaN', 0)
df['sta'] = df[stationField]
### reorder based on station value
### this line takes care of an unordered table
df.sort_values([stationField, xField], ascending=[True,True], inplace=True)
df['startX']= ''
df['startY']= ''
df['endX']= ''
df['endY']= ''
df['segDistance'] = ''
df['ratio'] = ''
df['segDistance'] = df.where(df[xField].ne(0)).sta.dropna().diff().reindex(df.index).bfill()
df.station-=df.groupby(df[xField].ne(0).cumsum())['station'].transform('first')
df.startX=df.groupby(df[xField].ne(0).cumsum())[xField].transform('first')
df.startY=df.groupby(df[xField].ne(0).cumsum())[yField].transform('first')

df.endX = df.where(df[xField].ne(0)).X.dropna().reindex(df.index).bfill()
df.endY = df.where(df[xField].ne(0)).Y.dropna().reindex(df.index).bfill()

df.ratio = df.station/df.segDistance

df['newX'] = ((1-df.ratio)*df.startX+df.ratio*df.endX).apply(lambda x: '%.5f' % x)
df['newY'] = ((1-df.ratio)*df.startY+df.ratio*df.endY).apply(lambda x: '%.5f' % x)

df = df.replace('nan', 0)

df['geometry'] = df.apply(lambda x: Point((float(x.newX), float(x.newY))), axis=1)
df = geopandas.GeoDataFrame(df, geometry='geometry')
df.crs= "+init=epsg="+ repr(outputcrs)

# outputs
df.to_file(outputFile, driver='ESRI Shapefile')
#df.to_csv('output.csv')
