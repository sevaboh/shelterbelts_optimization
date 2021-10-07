#!/usr/bin/python
from osgeo import ogr
import sys
import math
import fields
import shelterbelts
import pot_shelterbelts

# open shapefiles
fields_shp = ogr.Open("fields_36N.shp",update=True)
belts = ogr.Open("shelterbelts_36N.shp")
pot_belts = ogr.Open("pot_shelterbelts.shp")
fields_sh = fields_shp.GetLayer(0)
belts_sh = belts.GetLayer(0)
pot_belts_sh = pot_belts.GetLayer(0)
n_fields=fields_sh.GetFeatureCount()
n_belts=belts_sh.GetFeatureCount()
n_pot_belts=pot_belts_sh.GetFeatureCount()
print(str(n_fields)+" fields, "+str(n_belts)+" shelterbelts, "+str(n_pot_belts)+" potential shelterbelts places")
# combine lists of shelterbelts and save it
shelterbelts=shelterbelts.gen_shelterbelts()
pot_shelterbelts=pot_shelterbelts.gen_pot_shelterbelts()
all_belts=[]
for i in range(len(shelterbelts)):
	all_belts.append(shelterbelts[i])
for i in range(len(pot_shelterbelts)):
	pot_shelterbelts[i].append(i)
	all_belts.append(pot_shelterbelts[i])
f2=open("all_shelterbelts.py","wt")
f2.write("def gen_shelterbelts():\n\tshelterbelts = []\n") # ([field1,field2],length(m),present)
for i in range(len(all_belts)):
	f2.write("\tshelterbelts.append([[");
	for j in range(len(all_belts[i][0])):
		f2.write(str(all_belts[i][0][j]))
		if j!=len(all_belts[i][0])-1:
			f2.write(",")
	f2.write("], "+str(all_belts[i][1])+", "+str(all_belts[i][2])+","+str(all_belts[i][3])+"])\n")
f2.write("\treturn shelterbelts\n")
f2.close()
# set list of shelterbelts in fields
fields=fields.gen_fields()
for i in range(len(fields)):
	fields[i].append([])
for i in range(len(all_belts)):
	for j in all_belts[i][0]:
		fields[j][4].append(i)
# for each shelterbelts generate a classification bitstring - each bit corresponds to the sector of +pi/4 this 0 = -pi (points to the west)
for i in range(len(fields)):
	fields[i].append([])
	feature = fields_sh.GetFeature(fields[i][3])
	geom = feature.GetGeometryRef()
	centroid=geom.Centroid()
	cp=centroid.GetPoint()
	cx=cp[0]
	cy=cp[1]
	for jj in range(len(fields[i][4])):
		j=fields[i][4][jj]
		if all_belts[j][2]==1:
			feature2 = belts_sh.GetFeature(all_belts[j][3])
		else:
			feature2 = pot_belts_sh.GetFeature(all_belts[j][3])
		geom2 = feature2.GetGeometryRef()
		is_point=1
		cl=0
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
			if q==8:
				q=7
			fields[i]
			cl = (1<<q)
		except:
			pass
		fields[i][5].append(cl)
# save fields
f1=open("all_fields.py","wt")
f1.write("def gen_fields():\n\tfields = []\n") # (area(m^2),avg vtci,irrigation,id)
for i in range(n_fields):
	f1.write("\tfields.append(["+str(fields[i][0])+", "+str(fields[i][1])+", "+str(fields[i][2])+", "+str(fields[i][3])+",[")
	for j in range(len(fields[i][4])):
		f1.write(str(fields[i][4][j]))
		if j!=len(fields[i][4])-1:
			f1.write(",")
	f1.write("],[")
	for j in range(len(fields[i][5])):
		f1.write(str(fields[i][5][j]))
		if j!=len(fields[i][5])-1:
			f1.write(",")
	f1.write("]])\n")
f1.write("\treturn fields\n")
f1.close()