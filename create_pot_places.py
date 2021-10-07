#!/usr/bin/python
from osgeo import ogr
import os
import sys
import math
import fields
import shelterbelts

outDriver = ogr.GetDriverByName("ESRI Shapefile")
# open shapefile
fields_shp = ogr.Open("fields_36N.shp")
belts = ogr.Open("shelterbelts_36N.shp")
fields_sh = fields_shp.GetLayer(0)
belts_sh = belts.GetLayer(0)
n_fields=fields_sh.GetFeatureCount()
n_belts=belts_sh.GetFeatureCount()
print(str(n_fields)+" fields, "+str(n_belts)+" shelterbelts")
# set list of shelterbelts in fields
fields=fields.gen_fields()
shelterbelts=shelterbelts.gen_shelterbelts()
for i in range(len(fields)):
	fields[i].append([])
for i in range(len(shelterbelts)):
	for j in shelterbelts[i][0]:
		fields[j][4].append(shelterbelts[i][3])
new_belts=[] # [[field id list],x1,y1,x2,y2]
# process fields
for i in fields:
	feature = fields_sh.GetFeature(i[3])
	geom = feature.GetGeometryRef()
	farea= geom.Area()
	ring = geom.GetGeometryRef(0)
	np=ring.GetPointCount()
	centroid=geom.Centroid()
	cp=centroid.GetPoint()
	cx=cp[0]
	cy=cp[1]
	cl=feature.GetField("ID2") # class - each bit mean a shelterbelt in the sector -pi + pi/4 * [bit_number,bit_number+1]
	print("field "+str(i[3])+" center ("+str(int(cx))+","+str(int(cy))+")")
	# get rotated bounding box with minimal area
	mina=0
	minarea=0
	minbb=[[0,0],[0,0],[0,0],[0,0]]
	for ang in range(360):
		a=2.0*ang/math.pi
		s = math.sin(a)
		c = math.cos(a)
		bb=[[0,0],[0,0],[0,0],[0,0]]
		# --- center and rotate the polygon and get its bb
		for j in range(np):
			p=ring.GetPoint(j)
			px = p[0]- cx;
			py = p[1]- cy;
			xnew = px * c - py * s;
			ynew = px * s + py * c;
			if j==0:
				bb[0][0]=bb[1][0]=bb[2][0]=bb[3][0]=xnew
				bb[0][1]=bb[1][1]=bb[2][1]=bb[3][1]=ynew
			else:
				if bb[0][0]>xnew:
					bb[0][0]=bb[1][0]=xnew
				if bb[2][0]<xnew:
					bb[2][0]=bb[3][0]=xnew
				if bb[0][1]>ynew:
					bb[0][1]=bb[3][1]=ynew
				if bb[1][1]<ynew:
					bb[1][1]=bb[2][1]=ynew
		area=(bb[3][0]-bb[0][0])*(bb[1][1]-bb[0][1])
		if ang==0:
			minarea=area
			for ii in range(4):
				minbb[ii][0]=bb[ii][0]
				minbb[ii][1]=bb[ii][1]
		else:
			if area<minarea:
				minarea=area
				mina=a
				for ii in range(4):
					minbb[ii][0]=bb[ii][0]
					minbb[ii][1]=bb[ii][1]
	a=mina
	for ii in range(4):
		bb[ii][0]=minbb[ii][0]
		bb[ii][1]=minbb[ii][1]
	print("minangle "+str(a)+" bb area "+str(minarea)+" f area "+str(farea))
	print("bb in rotated coords [("+str(int(bb[0][0]))+","+str(int(bb[0][1]))+"),("+str(int(bb[1][0]))+","+str(int(bb[1][1]))+"),("+str(int(bb[2][0]))+","+str(int(bb[2][1]))+"),("+str(int(bb[3][0]))+","+str(int(bb[3][1]))+")");
	# --- rotate and move bb back and calculate angles (+pi) of vectors from center to bb corners and the corresponding pi/4 sectors
	s = math.sin(-a)
	c = math.cos(-a)
	print("bs "+str(s)+" bc "+str(c))
	sectors=[0,0,0,0,0]
	for j in range(4):
		xnew=bb[j][0] * c - bb[j][1] * s + cx
		ynew=bb[j][0] * s + bb[j][1] * c + cy
		bb[j][0]=xnew
		bb[j][1]=ynew
		sectors[j]=math.atan2(bb[j][1]-cy,bb[j][0]-cx)+math.pi
		sectors[j]=int(4.0*sectors[j]/math.pi)
	sectors[4]=sectors[0]
	print("bb [("+str(int(bb[0][0]))+","+str(int(bb[0][1]))+"),("+str(int(bb[1][0]))+","+str(int(bb[1][1]))+"),("+str(int(bb[2][0]))+","+str(int(bb[2][1]))+"),("+str(int(bb[3][0]))+","+str(int(bb[3][1]))+")");
	ss=[0,0,0,0,0,0,0,0]
	ss2=[0,0,0,0,0,0,0,0]
	s="sectors - ";
	for j in range(8):
		for k in range(4):
			r0=sectors[k]
			r1=sectors[k+1]
			if r1==7:
				r1=0
				ss[7]=k+1
			if j>=r1 and j<r0:
				ss[j]=k+1
		ss2[j]=(cl>>j)&1
		s=s+"["+str(ss[j])+str(ss2[j])+"]"
	print(s)
	print("sectors for bb sides - "+str(sectors[0])+","+str(sectors[1])+","+str(sectors[2])+","+str(sectors[3]))
	# check if there are shelterbelts on bb sides
	free_sides=[1,1,1,1]
	for j in range(8):
		if ss[j]!=0 and ss2[j]!=0:
			free_sides[ss[j]-1]=0
	print("free sizes - "+str(free_sides[0])+" "+str(free_sides[1])+" "+str(free_sides[2])+" "+str(free_sides[3])+" ")
	# check if there already are potential shelterbelts on bb sides - add the field to their field lists
	for j in range(4):
		if free_sides[j]==1:
			line=ogr.Geometry(ogr.wkbLineString)
			line.AddPoint(bb[j][0],bb[j][1])
			line.AddPoint(bb[(j+1)%4][0],bb[(j+1)%4][1])
			for k in new_belts:
				line2=ogr.Geometry(ogr.wkbLineString)
				line2.AddPoint(k[1],k[2])
				line2.AddPoint(k[3],k[4])
				d=line.Distance(line2)
				if d<=100:
					found=0
					for ii in k[0]:
						if ii==i[3]:
							found=1
							break
					if found==0:
						k[0].append(i[3])
					free_sides[j]=0
					print("place for the side "+str(j)+" - "+str(int(bb[j][0]))+" "+str(int(bb[j][1]))+" "+str(int(bb[(j+1)%4][0]))+" "+str(int(bb[(j+1)%4][1])))
					print("old place "+str(k[1])+" "+str(k[2])+" "+str(k[3])+" "+str(k[4]))
					print("place for the side "+str(j)+" is already present (d="+str(d)+") for field "+str(k[0][0]))
					break
	# create new potential shelterbelt place
	for j in range(4):
		if free_sides[j]==1:
			new_belts.append([[i[3]],bb[j][0],bb[j][1],bb[(j+1)%4][0],bb[(j+1)%4][1]])
			print("new belt "+str(int(bb[j][0]))+" "+str(int(bb[j][1]))+" "+str(int(bb[(j+1)%4][0]))+" "+str(int(bb[(j+1)%4][1])))
# create new potential shelterbelts shapefile
if os.path.exists("pot_shelterbelts.shp"):
    outDriver.DeleteDataSource("pot_shelterbelts.shp")
outDataSource = outDriver.CreateDataSource("pot_shelterbelts.shp")
outLayer = outDataSource.CreateLayer("pot_shelterbelts", geom_type=ogr.wkbLineString)
featureDefn = outLayer.GetLayerDefn()
f=open("pot_shelterbelts.py","wt")
f.write("def gen_pot_shelterbelts():\n\tpot_shelterbelts=[]\n")
for i in new_belts:
	line=ogr.Geometry(ogr.wkbLineString)
	line.AddPoint(i[1],i[2])
	line.AddPoint(i[3],i[4])
	l=line.Length()
	feature2 = ogr.Feature(featureDefn)
	feature2.SetGeometry(line)
	outLayer.CreateFeature(feature2)
	feature2 = None
	f.write("\tpot_shelterbelts.append([[");
	for j in range(len(i[0])):
		f.write(str(i[0][j]))
		if j!=len(i[0])-1:
			f.write(",")
	f.write("], "+str(l)+", 0])\n")
f.write("\treturn pot_shelterbelts\n")
f.close()
featureDefn=None
outLayer=None
outDataSource = None
# create new shapefile with lines between adjacent fields and shelterbelts
if os.path.exists("graph.shp"):
    outDriver.DeleteDataSource("graph.shp")
outDataSource = outDriver.CreateDataSource("graph.shp")
outLayer = outDataSource.CreateLayer("edges", geom_type=ogr.wkbLineString)
featureDefn = outLayer.GetLayerDefn()
for i in fields:
	feature = fields_sh.GetFeature(i[3])
	geom = feature.GetGeometryRef()
	centroid=geom.Centroid()
	cp=centroid.GetPoint()
	cx=cp[0]
	cy=cp[1]
	for j in i[4]:
		feature2 = belts_sh.GetFeature(j)
		geom2 = feature2.GetGeometryRef()
		try:
			pc=geom2.GetPointCount()
			p1=geom2.GetPoint(0)
			p2=geom2.GetPoint(pc-1)
			c2x=(p1[0]+p2[0])/2.0
			c2y=(p1[1]+p2[1])/2.0
			line=ogr.Geometry(ogr.wkbLineString)
			line.AddPoint(cx,cy)
			line.AddPoint(c2x,c2y)
			feature2 = ogr.Feature(featureDefn)
			feature2.SetGeometry(line)
			outLayer.CreateFeature(feature2)
			feature2 = None
		except:
			pass
featureDefn=None
outLayer=None
outDataSource = None
# create new shapefile with lines between adjacent fields and potential shelterbelts
if os.path.exists("graph_pot.shp"):
    outDriver.DeleteDataSource("graph_pot.shp")
outDataSource = outDriver.CreateDataSource("graph_pot.shp")
outLayer = outDataSource.CreateLayer("edges", geom_type=ogr.wkbLineString)
featureDefn = outLayer.GetLayerDefn()
for i in new_belts:
	c2x=(i[1]+i[3])/2.0
	c2y=(i[2]+i[4])/2.0
	for j in i[0]:
		feature = fields_sh.GetFeature(j)
		geom = feature.GetGeometryRef()
		centroid=geom.Centroid()
		cp=centroid.GetPoint()
		cx=cp[0]
		cy=cp[1]
		line=ogr.Geometry(ogr.wkbLineString)
		line.AddPoint(cx,cy)
		line.AddPoint(c2x,c2y)
		feature2 = ogr.Feature(featureDefn)
		feature2.SetGeometry(line)
		outLayer.CreateFeature(feature2)
		feature2 = None
outDataSource = None
