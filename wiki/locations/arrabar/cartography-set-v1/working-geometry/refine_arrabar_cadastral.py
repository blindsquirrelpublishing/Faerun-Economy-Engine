from pathlib import Path
import sys,json,math,copy,shutil,xml.etree.ElementTree as ET,csv,zipfile
sys.path.insert(0,r'C:\Users\localadmin\Documents\Codex\2026-10-14\task')
import render_arrabar_plates as P
import numpy as np,cv2
from PIL import Image,ImageDraw
from shapely.geometry import Polygon,MultiPoint,LineString,Point
from shapely.ops import unary_union
from shapely import voronoi_polygons
R=P.ROOT;G=P.GEO;D=json.loads((G/'arrabar-thematic-geometry-r02.json').read_text(encoding='utf-8'))
im=np.array(Image.open(R/'source-maps/ArrabarIA.webp').convert('RGB'));hsv=cv2.cvtColor(im,cv2.COLOR_RGB2HSV);water=np.array(Image.open(G/'arrabar-water-mask-r01.png'))
seed=((hsv[:,:,0]<32)&(hsv[:,:,1]>120)&(hsv[:,:,2]>100)&(water==0)).astype('uint8')*255
seed[:10]=0;seed[445:]=0;seed[:,:280]=0;seed[:,810:]=0
# Keep neighboring symbols separated. A global closing would merge dense blocks.
mask=seed
count,labels,stats,centroids=cv2.connectedComponentsWithStats(mask)
contours=[]
for label,stat in enumerate(stats[1:],1):
 if stat[4]<9:continue
 cc,_=cv2.findContours((labels==label).astype('uint8')*255,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 contours.extend(cc)
buildings=[]
for c in contours:
 if cv2.contourArea(c)<5:continue
 rect=cv2.minAreaRect(c);area=rect[1][0]*rect[1][1]
 # Fit only clearly rectangular source symbols. Compound silhouettes retain their contour.
 rectangular=area>0 and cv2.contourArea(c)/area>.65
 pts=cv2.boxPoints(rect) if rectangular else cv2.approxPolyDP(c,.65,True).reshape(-1,2)
 p=Polygon(pts).buffer(0)
 if p.is_empty:continue
 for part in ([p] if p.geom_type=='Polygon' else p.geoms):
  if part.geom_type!='Polygon' or part.area<1:continue
  buildings.append({'coordinates':[[round(x,3),round(y,3)] for x,y in list(part.exterior.coords)[:-1]],'area_px2':part.area,'centroid':[part.centroid.x,part.centroid.y],'trace_method':'source-symbol rectangle fit' if rectangular else 'source compound outline; <=0.65 px simplification','max_raster_detail_px':1.5})
buildings.sort(key=lambda b:(round(b['centroid'][1]/20),b['centroid'][0]))
for i,b in enumerate(buildings):b['id']=f'B{i+1:03d}'
overlay=Image.fromarray(im).convert('RGBA');dr=ImageDraw.Draw(overlay)
for b in buildings:dr.line([tuple(p) for p in b['coordinates']+[b['coordinates'][0]]],fill=(10,255,255,255),width=1)
task=Path(__file__).parent;overlay.resize((2000,1184)).save(task/'cadastral-refined-trace-audit.png')
print(json.dumps({'building_symbols':len(buildings),'rectangles':sum(b['trace_method'].endswith('fit') for b in buildings)}))
if '--render' not in sys.argv:sys.exit(0)
# Include manually registered landmark compounds, preserving interior courts.
landmarks=[{'key':6,'name':'The Generon','point':[565,154],'outer':[[540,139],[592,139],[592,178],[540,178]],'court':[[551,148],[580,148],[580,168],[551,168]]},{'key':7,'name':'Temple to Tempus','point':[508,271],'outer':[[488,261],[527,261],[527,280],[488,280]]},{'key':8,'name':'Temple of Silvanus','point':[452,314],'outer':[[433,305],[474,305],[474,326],[433,326]],'court':[[445,311],[463,311],[463,319],[445,319]]},{'key':9,'name':'Temple of Lliira','point':[411,270],'outer':[[395,258],[424,258],[424,281],[395,281]]}]
for l in landmarks:
 l['outer']=next(f['pixel_coordinates'] for f in P.MAN['features'] if f['id']==f'B00{l["key"]}')
 l.pop('court',None)
landmark_polys=[Polygon(l['outer']) for l in landmarks]
# Preserve the actual component traces inside landmark compounds; a compound
# bounding box is a location reference, not a solid invented building footprint.
for b in buildings:
 for l,q in zip(landmarks,landmark_polys):
  if q.contains(Point(b['centroid'])):b['name']=l['name']+' / source component'
bp=[Polygon(b['coordinates']) for b in buildings]
land=Polygon(next(f['pixel_coordinates'] for f in P.MAN['features'] if f['id']=='LW-LAND'))
urban=unary_union([Polygon(d['coordinates']).buffer(0) for d in D['districts']]).intersection(land)
roadcorridors=unary_union([LineString(f['pixel_coordinates']).buffer(4.5 if f['id']=='R01' else 3,join_style=2) for f in D['roads']])
blocks=urban.difference(roadcorridors)
cells=voronoi_polygons(MultiPoint([b['centroid'] for b in buildings]),extend_to=urban.envelope,ordered=True)
parcels=[]
for b,cell in zip(buildings,cells.geoms):
 p=cell.intersection(blocks)
 if p.is_empty:continue
 if p.geom_type=='MultiPolygon':p=max(p.geoms,key=lambda x:x.area)
 if p.geom_type!='Polygon':continue
 parcels.append({'id':'P'+b['id'],'building_id':b['id'],'coordinates':[[round(x,3),round(y,3)] for x,y in p.exterior.coords],'basis':'inferred nearest-building planning parcel, clipped to interpreted blocks and source street corridors; no legal ownership claim'})
theme=P.boundary_layer()
def pg(parent,pts,**attrs):parent.append(P.el('polygon',points=' '.join(f'{x},{y}' for x,y in pts),**attrs))
def ln(parent,pts,**attrs):parent.append(P.el('polyline',points=' '.join(f'{x},{y}' for x,y in pts),fill='none',**attrs))
district_layer=P.el('g',id='district-land-use');theme.append(district_layer)
for d in D['districts']:pg(district_layer,d['coordinates'],id=d['id'],fill=d['color'],stroke='#8e8a80',stroke_width='.45',stroke_dasharray='2 1.5')
parcel_layer=P.el('g',id='inferred-parcels');theme.append(parcel_layer)
for p in parcels:pg(parcel_layer,p['coordinates'],id=p['id'],fill='none',stroke='#8a7f71',stroke_width='.22',stroke_dasharray='.8 .55')
street_layer=P.el('g',id='source-streets');theme.append(street_layer)
for f in D['roads']:ln(street_layer,f['pixel_coordinates'],id=f['id'],stroke='#fffffa',stroke_width=9 if f['id']=='R01' else 6,stroke_linejoin='round',stroke_linecap='round')
building_layer=P.el('g',id='source-building-footprints');theme.append(building_layer)
for b in buildings:
 q=P.el('g',id=b['id']);t=P.el('title');t.text=b.get('name',b['id'])+' | '+b['trace_method'];q.append(t);pg(q,b['coordinates'],fill='#4b5357',stroke='#26383d',stroke_width='.35')
 if b.get('court'):pg(q,b['court'],fill='#e5e9d7',stroke='#26383d',stroke_width='.3')
 building_layer.append(q)
quay=P.el('g',id='source-piers');theme.append(quay)
for p in D['piers']:pg(quay,p['coordinates'],id=p['id'],fill='#b4a68b',stroke='#5b5f57',stroke_width='.5')
wall=P.el('g',id='source-walls');theme.append(wall)
for f in D['walls']:
 ln(wall,f['pixel_coordinates'],id=f['id'],stroke='#28393d',stroke_width=2)
 for x,y in [f['pixel_coordinates'][0],f['pixel_coordinates'][-1]]:wall.append(P.el('circle',cx=x,cy=y,r=3.5,fill='#fefcf0',stroke='#28393d',stroke_width='.8'))
key=P.el('g',id='source-keyed-landmarks');theme.append(key)
for l in landmarks:
 pg(key,l['outer'],fill='none',stroke='#6d5740',stroke_width='.55',stroke_dasharray='1.5 .8')
 x,y=l['point'];key.append(P.el('circle',cx=x,cy=y,r=6.5,fill='#fffbea',stroke='#32454c',stroke_width='.65'));P.txt(key,x,y+2.5,str(l['key']),7.7,True,'middle')
for d in D['districts']:
 x,y=d['anchor'];P.txt(key,x,y,d['id'][-1],10,True,'middle',fill='#273c43',stroke='#fcfaf1',stroke_width='.8',paint_order='stroke')
P.txt(key,130,270,'VILHON REACH',13,True,'middle',fill='#e8f6f9')
P.txt(key,874,200,'Emerald Corridor',8.5,False,'middle',fill='#405e65')
P.txt(key,480,500,'Golden Road',8.5,False,'middle',fill='#405e65',transform='rotate(-58 480 500)')
legend=[('DISTRICT KEY',['1 Port. 2 Warehouse. 3 Merchant.','4 Governor. 5 Living.','Muted fills indicate interpreted district land use.']),('SOURCE LANDMARKS',['6 Generon. 7 Temple to Tempus.','8 Temple of Silvanus. 9 Temple of Lliira.','Sites 10-12 lack readable source anchors. Crying Claw: Warehouse District, exact plot unknown.']),('REGISTERED GEOMETRY',[f'{len(buildings)} traced building/compound symbols, not a building census. Dark gray silhouettes use source roof bounds as footprint proxies.','Original street junctions, walls, piers and shared shoreline remain registered. Fine detail is limited by the source raster.']),('INFERRED PARCELS',['Fine dashed edges allocate planning parcels to nearby source buildings within street-bounded blocks.','Parcel boundaries and district limits are inferred; no legal ownership or survey claim.']),('LIMITS AND DISAGREEMENTS',['Source bar: 500 ft / 150 px; reading uncertainty about 2 px. No enlargement to fit population.','The 61,012 planning estimate does not resolve the city-scale conflict.','Tempus is west of Governor on the source plan; prose says east. Source position retained.'])]
stem='02-cadastral-detailed-v1.8-r02';svg=P.make_plate(stem,'Detailed Cadastral Map',theme,legend,status='Detailed source reconstruction / review copy',subtitle='North-up source geometry | Inferred parcels dashed | No legal survey or ownership claim')
# Full-size 300 dpi output for inspection and print; retain editable SVG and mobile preview.
png=P.OUT/(stem+'.png');png.write_bytes(P.resvg_py.svg_to_bytes(svg_path=str(svg),width=5700,height=3900,dpi=100,font_files=['C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/arialbd.ttf']))
Image.open(png).resize((1900,1300)).save(P.OUT/(stem+'-preview.png'))
meta=json.loads((P.OUT/(stem+'.metadata.json')).read_text(encoding='utf-8'));meta.update({'raster_dimensions':[5700,3900],'print_dpi':300,'trace_revision':'r03','render_status':'completed; structural validation passed; full-resolution visual QA pending','building_symbols':len(buildings),'inferred_parcels':len(parcels),'parcel_override':'User specifically requested sensible inferred parcels; default style prohibition on invented legal parcels remains respected by explicit inferred labels.'});P.writejson(P.OUT/(stem+'.metadata.json'),meta)
geo={'revision':'r03','source':'ArrabarIA.webp','master_id':P.MAN['master_id'],'geometry_sha256':P.MAN['geometry_sha256'],'buildings':buildings,'landmarks':landmarks,'inferred_parcels':parcels,'roads':D['roads'],'walls':D['walls'],'piers':D['piers'],'districts':D['districts'],'uncertainty':'roof symbols, not surveyed ground footprints; no global dilation or closing; rectangle fitting only where source silhouette is strongly rectangular; compound contours retained'}
P.writejson(G/'arrabar-cadastral-geometry-r03.json',geo)
features=[]
for b in buildings:features.append({'type':'Feature','id':b['id'],'properties':{k:v for k,v in b.items() if k not in ['coordinates','court']},'geometry':{'type':'Polygon','coordinates':[b['coordinates']+[b['coordinates'][0]]]+([b['court']+[b['court'][0]]] if b.get('court') else [])}})
P.writejson(G/'arrabar-cadastral-buildings-r03.geojson',{'type':'FeatureCollection','coordinate_system':'LOCAL IMAGE PIXELS, not longitude/latitude','features':features})
with (G/'arrabar-cadastral-building-register-r03.csv').open('w',encoding='utf-8',newline='') as out:
 w=csv.writer(out);w.writerow(['id','name','source_x','source_y','source_symbol_area_px2','trace_method','inferred_parcel_id'])
 for b in buildings:w.writerow([b['id'],b.get('name',''),*b['centroid'],b['area_px2'],b['trace_method'],'P'+b['id']])
overlay.save(P.QA/'cadastral-r03-source-overlay.png');shutil.copy2(__file__,G/Path(__file__).name)
print(json.dumps({'svg':str(svg),'building_symbols':len(buildings),'parcels':len(parcels),'png_dimensions':[5700,3900]}))
