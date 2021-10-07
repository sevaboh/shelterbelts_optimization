#!/usr/bin/python
from osgeo import ogr
import sys

process_belts=0
process_fields=1
if len(sys.argv)>=2:
	process_belts=int(sys.argv[1])
if len(sys.argv)>=3:
	process_fields=int(sys.argv[2])

fields_shp = ogr.Open("fields_36N.shp")
belts = ogr.Open("shelterbelts_36N.shp")
fields_sh = fields_shp.GetLayer(0)
belts_sh = belts.GetLayer(0)
n_fields=fields_sh.GetFeatureCount()
n_belts=belts_sh.GetFeatureCount()
print(str(n_fields)+" fields, "+str(n_belts)+" shelterbelts")
# fields-shelterbelts graph
if process_fields==1:
	f1=open("fields.py","wt")
	f1.write("def gen_fields():\n\tfields = []\n") # (area(m^2),avg vtci,irrigation,id)
	for i in range(n_fields):
		feature = fields_sh.GetFeature(i)
		geom = feature.GetGeometryRef()
		try:
			area = geom.GetArea() 
			cl=feature.GetField("ID")
			vtci=feature.GetField("VTCI")
			irr=0
			if cl<=4:
				irr=1
			f1.write("\tfields.append(["+str(area)+", "+str(vtci)+", "+str(irr)+", "+str(i)+"])\n")
			print("field "+str(i)+" area "+str(area)+" vtci "+str(vtci)+" irrigation "+str(irr))
		
		except:
			pass
	f1.write("\treturn fields\n")
	f1.close()
if process_belts==0:
	exit(0)
f2=open("shelterbelts.py","wt")
f2.write("def get_shelterbelts():\n\tshelterbelts = []\n") # ([field1,field2],length(m),present)
for i in range(n_belts):
	feature = belts_sh.GetFeature(i)
	geom = feature.GetGeometryRef()
	try:
		l=geom.Length()
		fls=[]
		# find adjacent fields - distance should be less that 100m
		for j in range(n_fields):
			feature2 = fields_sh.GetFeature(j)
			geom2 = feature2.GetGeometryRef()
			d=geom.Distance(geom2)
			if d<=100:
				fls.append(j)
		# save and output
		if len(fls)>=1:
			f2.write("\tshelterbelts.append([[");
			for j in range(len(fls)):
				f2.write(str(fls[j]))
				if j!=len(fls)-1:
					f2.write(",")
			f2.write("], "+str(l)+", 1,"+str(i)+"])\n")
			s="shelterbelt "+str(i)+" length "+str(l)+" adjacent fields:["
			for j in fls:
				s=s+str(j)+" "
			s=s+"]"
			print(s)
	except:
		pass
f2.write("\treturn shelterbelts\n")
f2.close()