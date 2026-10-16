from pathlib import Path
import sys,json,math,copy,shutil,xml.etree.ElementTree as ET
sys.path.insert(0,r'C:\Users\localadmin\Documents\Codex\2026-10-14\task\cartography-runtime')
sys.path.insert(0,r'C:\Users\localadmin\Documents\Codex\2026-10-14\task')
import numpy as np,cv2
from PIL import Image
import render_arrabar_plates as P
ROOT=P.ROOT;GEO=P.GEO;QA=P.QA
T=json.loads((GEO/'arrabar-thematic-geometry-r02.json').read_text(encoding='utf-8'))
def polygon(g,pts,**a):g.append(P.el('polygon',points=' '.join(f'{x:.3f},{y:.3f}' for x,y in pts),**a))
def line(g,pts,**a):g.append(P.el('polyline',points=' '.join(f'{x:.3f},{y:.3f}' for x,y in pts),fill='none',**a))
def pts_of(id):return next(f['pixel_coordinates'] for f in P.MAN['features'] if f['id']==id)
coast=np.array(pts_of('LW-SHORE'));xs=np.interp(np.arange(592),coast[:,1],coast[:,0])
water=np.array(Image.open(GEO/'arrabar-water-mask-r01.png'))>0
xx,yy=np.meshgrid(np.arange(1000),np.arange(592))
# Dimensionless monotone relief hypothesis, consistent with hills descending to the bay.
relative=np.maximum(xx-xs[:,None],0)/95.0
relative+=.45*np.exp(-((xx-630)**2+(yy-120)**2)/42000)
relative[water]=0
g=P.boundary_layer();palette=['#eee8c7','#e1ddb1','#d2d19e','#bfc18d','#abad78','#969d66']
contour_records=[]
for i,level in enumerate([.4,1.2,2.0,2.8,3.6,4.4]):
    m=((relative>=level)&~water).astype('uint8')*255
    cc,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for c in cc:
        p=cv2.approxPolyDP(c,1,True).reshape(-1,2)
        if len(p)>2:
            polygon(g,p,fill=palette[i],stroke='none')
            contour_records.append({'band':f'H{i+1}','relative_threshold':level,'coordinates':p.tolist(),'basis':'hypothetical relative relief, no vertical datum or measured interval'})
    # Trace only interior contour line, omit map-edge outlines.
    pts=[]
    for y in range(0,592,5):
        idx=np.flatnonzero((relative[y]>=level)&~water[y])
        if len(idx):pts.append([int(idx[0]),y])
    if pts:
        line(g,pts,stroke='#777354',stroke_width='.8',stroke_dasharray='4 2')
        k=min(len(pts)-1,15+i*10);x,y=pts[k];P.txt(g,x+5,y,'H'+str(i+1),8,True,fill='#4e4a36')
for x,y in [(430,90),(488,211),(520,352),(672,132),(728,329),(650,466)]:
    line(g,[[x,y],[x-44,y+4]],stroke='#6b7892',stroke_width='1.2')
    polygon(g,[[x-44,y+4],[x-36,y-1],[x-36,y+8]],fill='#6b7892')
P.make_plate('03-topographic-concept-v1.8','Conceptual Relief',g,[('EVIDENCE',['Text describes gentle hills descending from the perimeter toward the bay. No surveyed elevations, contours or vertical datum were supplied.']),('RELATIVE BANDS',['H1–H6 run from lower shoreward terrain to higher inland terrain. They are ordered classes, not feet or metres.','Dashed lines are hypothetical contour-like guides. No equal-height interval is claimed.']),('DRAINAGE',['Muted arrows show inferred downslope tendency toward the Reach. They are not mapped streams or engineered drains.']),('TERRAIN-ONLY SHEET',['No buildings, boats, bridges, walls, roads or vegetation are included. Source sea-color bands do not establish bathymetry.']),('REGISTRATION AND SCALE',['Exact same source extent and land-water mask as the boundary master. Horizontal scale follows the source; vertical scale is unknown.','Do not use this sheet for excavation, flood-depth or engineering calculations.'])],status='Hypothetical relief • no surveyed heights',subtitle='Interpretive terrain only • horizontal source scale retained • no numerical elevation claims')
P.writejson(GEO/'conceptual-relief-r01.json',{'master_id':P.MAN['master_id'],'method':'relative shore distance plus a smooth conceptual inland rise','height_units':None,'vertical_datum':None,'measured_elevations':False,'contours':contour_records,'drainage_arrows':'inferred direction only; not waterways'})

basin={'id':'NW-B01','center':[460,282],'radius_x_px':27,'radius_y_px':22,'basis':'explicit reconstruction south of Warehouse District; location and dimensions unverified','waterbody':'open water for maneuvering barges and small vessels, not a rotating platform'}
canals=[
 {'id':'NW-C01','coordinates':[[355,239],[396,252],[430,252],[444,269]],'width_px':7,'role':'proposed harbor-to-basin route'},
 {'id':'NW-C02','coordinates':[[368,124],[392,153],[398,200],[396,252],[380,282],[351,318]],'width_px':5,'role':'proposed Port spine'},
 {'id':'NW-C03','coordinates':[[460,260],[460,252],[460,159],[399,159]],'width_px':5,'role':'proposed Warehouse branch'},
 {'id':'NW-C04','coordinates':[[487,282],[533,282],[533,215]],'width_px':5,'role':'proposed east branch'},
 {'id':'NW-C05','coordinates':[[460,304],[460,329],[538,329]],'width_px':5,'role':'proposed southern branch'}]
ug=P.boundary_layer()
for b in T['source_roof_silhouettes']:polygon(ug,b['coordinates'],fill='#c5c4bd',fill_opacity='.25',stroke='#989d9d',stroke_width='.25')
for f in T['roads']:line(ug,f['pixel_coordinates'],stroke='#b4aba0',stroke_width=2,stroke_dasharray='2 2')
for c in canals:line(ug,c['coordinates'],stroke='#3a86bb',stroke_width=c['width_px'],stroke_opacity='.65',stroke_linejoin='round');line(ug,c['coordinates'],stroke='#12618e',stroke_width='.8',stroke_dasharray='4 2')
ug.append(P.el('ellipse',cx=460,cy=282,rx=27,ry=22,fill='#70b6da',fill_opacity='.75',stroke='#12618e',stroke_width='1.2',stroke_dasharray='4 2'))
ug.append(P.el('ellipse',cx=460,cy=282,rx=8,ry=6,fill='#fff5cc',stroke='#9f8c59',stroke_width='.7'))
# Proposed quay edges, separate from waterbody; no machinery or rotating structure.
line(ug,[[444,263],[455,261]],stroke='#755c45',stroke_width=3)
line(ug,[[465,303],[477,298]],stroke='#755c45',stroke_width=3)
for label,x,y in [('B',460,287),('C1',419,247),('C2',387,212),('C3',466,208),('C4',513,275),('C5',501,324)]:P.txt(ug,x,y,label,8,True,'middle',fill='#174660',stroke='white',stroke_width='.7',paint_order='stroke')
P.txt(ug,474,241,'Warehouse District above',7,False,'middle',fill='#707478')
P.make_plate('06-netherwaters-plan-v1.8','Netherwaters Plan',ug,[('SOURCED DESCRIPTION',['Covered canals honeycomb the Port District and reach neighboring boroughs. A turning basin lies south of Warehouse District; its light well is smaller than the basin.','Goods boats and narrowboat waste barges used the network.']),('RECONSTRUCTION KEY',['B: hypothetical basin footprint; blue is maneuvering water, not a rotating structure.','Pale central opening: proposed light-well location. Brown marks: proposed quay edges.','C1–C5: proposed canal routes. Blue dashed edges distinguish them from surveyed water boundaries.']),('ALIGNMENT',['Gray lines and silhouettes show the exact registered street/building layers above. No surface building is relocated.']),('UNKNOWN GEOMETRY',['All canal alignments, basin dimensions, docks and depths in this plan are conceptual. No original underground floorplan was available.','No secret doors, monsters, hidden rooms or stair connections are invented.']),('SOURCE SCALE',['The horizontal framework uses the source map scale. Proposed widths are planning dimensions, not setting facts.'])],status='Conceptual underground reconstruction',subtitle='Covered canal hypothesis registered to streets above • basin is a body of water')
P.writejson(GEO/'netherwaters-concept-r01.json',{'master_id':P.MAN['master_id'],'source_geometry_known':False,'basis':'README geography / Ed Greenwood canal account; no exact plans','basin':basin,'canals':canals,'lightwell':{'center':[460,282],'radius_x_px':8,'radius_y_px':6,'basis':'smaller than basin is sourced; dimensions and exact position inferred'},'vertical_datum':None,'depths':'unknown','street_alignment':'uses shared image coordinates; does not claim every canal is beneath a street'})
shutil.copy2(__file__,GEO/'render_arrabar_relief_underground.py')
print('Saved conceptual relief and Netherwaters geometry and plates.')
