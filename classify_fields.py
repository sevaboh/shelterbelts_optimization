#!/usr/bin/python
from osgeo import ogr
import sys
import math
import fields
import shelterbelts

# open shapefiles
fields_shp = ogr.Open("fields_36N.shp",update=True)
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
# classify fields according to the direction in which shelterbelts are present
# each bit of the class (ID2) corresponds to the sector of +pi/4 this 0 = -pi (points to the west)
for i in fields:
	feature = fields_sh.GetFeature(i[3])
	geom = feature.GetGeometryRef()
	centroid=geom.Centroid()
	cp=centroid.GetPoint()
	cx=cp[0]
	cy=cp[1]
	cl=0
	for j in i[4]:
		feature2 = belts_sh.GetFeature(j)
		geom2 = feature2.GetGeometryRef()
		is_point=1
		try:
			pc=geom2.GetPointCount()
			p1=geom2.GetPoint(0)
			p2=geom2.GetPoint(pc-1)
			p1x=p1[0]
			p1y=p1[1]
			p2x=p2[0]
			p2y=p2[1]
			# calculate direction from (cx,cy) to (p1x,p1y),(p2x,p2y)
			# (p1x,p1y),(p2x,p2y) in form ax+by+c=0
			a=1
			b=0
			c=-p1x
			if (p2x-p1x)!=0.0:
				a=(p2y-p1y)/(p2x-p1x)
				b=-1
				c=p1y-p1x*a
			nx=(b*(b*cx-a*cy)-a*c)/(a*a+b*b)
			ny=(a*(-b*cx+a*cy)-b*c)/(a*a+b*b)
			# direction angle in radians
			d=math.atan2(ny-cy,nx-cx)
			q=int(4.0*(d+math.pi)/math.pi)
			cl = cl | (1<<q)
			print("("+str(int(cx))+","+str(int(cy))+")<->[("+str(int(p1x))+","+str(int(p1y))+"),("+str(int(p2x))+","+str(int(p2y))+") -> ("+str(int(nx))+","+str(int(ny))+") -> "+str(d)+" rad -> "+str(q)+" quadr -> class "+str(cl))
		except:
			pass
	print("field "+str(i)+" class "+str(cl))
	feature.SetField("ID2",cl)
	fields_sh.SetFeature(feature)
fields_sh=None
fields_shp=None