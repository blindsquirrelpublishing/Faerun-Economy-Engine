from pathlib import Path
import sys,json,hashlib,math,copy,shutil
sys.path.insert(0,r'C:\Users\localadmin\Documents\Codex\2026-10-14\task\cartography-runtime')
sys.path.insert(0,r'C:\Users\localadmin\Documents\Codex\2026-10-14\task')
import numpy as np,cv2
from PIL import Image,ImageDraw
from shapely.geometry import Polygon,LineString,Point
import render_arrabar_plates as P
ROOT=P.ROOT;GEO=P.GEO;QA=P.QA
im=np.array(Image.open(ROOT/'source-maps/ArrabarIA.webp').convert('RGB'));hsv=cv2.cvtColor(im,cv2.COLOR_RGB2HSV)
water=np.array(Image.open(GEO/'arrabar-water-mask-r01.png'))
# Source-color segmentation stays in source coordinates. No generated building locations.
roof=((hsv[:,:,0]<32)&(hsv[:,:,1]>120)&(hsv[:,:,2]>100)&(water==0)).astype('uint8')*255
roof[:10]=0;roof[445:]=0;roof[:,:280]=0;roof[:,810:]=0
n,lab,stats,cents=cv2.connectedComponentsWithStats(roof)
buildings=[];buildingmask=np.zeros_like(roof)
for i,s in enumerate(stats[1:],1):
    if s[4]<9:continue
    component=(lab==i).astype('uint8')*255
    contours,_=cv2.findContours(component,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c)<5:continue
        q=cv2.approxPolyDP(c,.45,True).reshape(-1,2)
        if len(q)<3:continue
        poly=Polygon(q).buffer(0)
        if poly.is_empty:continue
        buildings.append({'id':f'RF{len(buildings)+1:04d}','coordinates':q.tolist(),'area_source_pixels':float(poly.area),'centroid_source_pixels':[float(poly.centroid.x),float(poly.centroid.y)],'basis':'source roof-color silhouette; may split roof ridges or join touching structures; not a building census'})
        cv2.fillPoly(buildingmask,[q],255)

districts=[
 {'id':'D01','name':'Port District','color':'#cbdedd','coordinates':[[367,103],[386,104],[397,161],[399,207],[396,252],[381,282],[360,309],[337,343],[318,340],[307,325],[317,301],[318,280],[337,255],[363,226],[374,204],[364,171],[362,149],[367,116]],'anchor':[375,204]},
 {'id':'D02','name':'Warehouse District','color':'#e8d7b5','coordinates':[[386,104],[396,88],[435,46],[567,46],[629,108],[535,108],[535,252],[396,252],[399,207],[397,161]],'anchor':[465,200]},
 {'id':'D03','name':'Merchant District','color':'#e7c9c0','coordinates':[[337,343],[360,309],[381,282],[396,252],[535,252],[537,327],[581,275],[663,239],[661,334],[628,334],[564,397],[373,397]],'anchor':[478,365]},
 {'id':'D04','name':"Governor's District",'color':'#d2dce9','coordinates':[[535,108],[596,108],[596,261],[581,275],[550,305],[537,327],[535,252]],'anchor':[563,228]},
 {'id':'D05','name':'Living District','color':'#d9d4e6','coordinates':[[596,108],[721,109],[722,173],[752,207],[752,238],[722,269],[722,334],[661,334],[663,239],[596,261]],'anchor':[690,192]}
]
for d in districts:d['basis']='interpretive boundary connecting source-mapped district blocks; ownership and legal ward limits unknown'
roads=[f for f in P.MAN['features'] if f['type']=='road'];walls=[f for f in P.MAN['features'] if f['type']=='wall']
# Correct source-edge junction reading without changing shared coast.
next(f for f in roads if f['id']=='R07')['pixel_coordinates'][0]=[355,239]
piers=[[[353,123],[367,126],[365,131],[352,127]],[[351,147],[363,149],[363,154],[350,152]],[[351,169],[364,169],[365,174],[351,174]],[[356,187],[372,189],[373,194],[356,192]],[[356,208],[374,208],[372,213],[356,213]],[[345,226],[359,236],[355,240],[342,230]],[[321,249],[337,257],[334,262],[318,254]],[[309,272],[323,278],[321,284],[306,278]],[[300,309],[317,315],[315,320],[297,314]]]

# Proposed parcel edges from nearest source silhouette, clipped to interpreted urban blocks.
# This is a disclosed reconstruction; never substitute it for legal cadastral evidence.
urban=np.zeros_like(roof)
for d in districts:cv2.fillPoly(urban,[np.array(d['coordinates'],np.int32)],255)
roadmask=np.zeros_like(roof)
for f in roads:cv2.polylines(roadmask,[np.array(f['pixel_coordinates'],np.int32)],False,255,10 if f['id']=='R01' else 7)
seed=np.where(buildingmask>0,0,255).astype('uint8')
dist,near=cv2.distanceTransformWithLabels(seed,cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_CCOMP)
edge=np.zeros_like(roof);edge[:,1:]=np.where(near[:,1:]!=near[:,:-1],255,0);edge[1:,:]|=np.where(near[1:,:]!=near[:-1,:],255,0).astype('uint8')
edge[(urban==0)|(roadmask>0)|(buildingmask>0)|(water>0)]=0
parcel_lines=[]
for yy in range(592):
    xs=np.flatnonzero(edge[yy]);groups=np.split(xs,np.flatnonzero(np.diff(xs)>1)+1)
    for g in groups:
        if len(g):parcel_lines.append([[int(g[0]),yy],[int(g[-1])+1,yy]])

allgeo={'revision':'r02','master_id':P.MAN['master_id'],'land_water_geometry_sha256':P.MAN['geometry_sha256'],'source':'ArrabarIA.webp','source_sha256':P.sha(ROOT/'source-maps/ArrabarIA.webp'),'coordinate_system':'image pixels, x right/y down; not georeferenced','extent':[0,0,1000,592],'source_roof_silhouettes':buildings,'districts':districts,'roads':roads,'walls':walls,'piers':[{'id':f'P{i+1:02d}','coordinates':p,'basis':'manually traced visible pier symbol; not shoreline'} for i,p in enumerate(piers)],'proposed_parcels':{'method':'nearest source structure silhouette; clipped to interpreted city blocks and excluded road corridors','status':'inferred planning subdivision; not historical ownership','scanline_edges':parcel_lines},'unresolved':['Source has stylized roofs, not surveyed building footprints','Roof component count is not a count of buildings or households','Exact legal district boundaries and parcel boundaries unknown','Locations 10-12 have no readable numbered anchors in supplied raster','Text-only named places are listed in key without invented point positions']}
P.writejson(GEO/'arrabar-thematic-geometry-r02.json',allgeo)
Image.fromarray(buildingmask).save(GEO/'source-roof-silhouettes-r02.png')
Image.fromarray(edge).save(GEO/'proposed-parcel-edges-r02.png')
featurecollection={'type':'FeatureCollection','coordinate_system':'LOCAL IMAGE PIXELS; NOT WGS84','features':[]}
for b in buildings:featurecollection['features'].append({'type':'Feature','id':b['id'],'properties':{'basis':b['basis']},'geometry':{'type':'Polygon','coordinates':[b['coordinates']+[b['coordinates'][0]]]}})
P.writejson(GEO/'source-building-silhouettes-r02.geojson',featurecollection)

def polygon(parent,points,**attrs):
    parent.append(P.el('polygon',points=' '.join(f'{x},{y}' for x,y in points),**attrs))
def polyline(parent,points,**attrs):
    parent.append(P.el('polyline',points=' '.join(f'{x},{y}' for x,y in points),fill='none',**attrs))
def base():return P.boundary_layer()
def city_layer(style='cadastral',labels=True,parcels=False):
    g=base()
    for d in districts:polygon(g,d['coordinates'],fill=d['color'],stroke='#8a8580',stroke_width='.6',stroke_dasharray='3 2')
    if parcels:
        pg=P.el('g',id='inferred-parcels',stroke='#8e8478',stroke_width='.42',stroke_opacity='.8')
        for p in parcel_lines:polyline(pg,p,stroke='#8e8478',stroke_width='.42')
        g.append(pg)
    for f in roads:polyline(g,f['pixel_coordinates'],stroke='#fffefa',stroke_width=9 if f['id']=='R01' else 6,stroke_linejoin='round',stroke_linecap='round')
    for b in buildings:polygon(g,b['coordinates'],fill='#50565b' if style=='cadastral' else '#bc895f',stroke='#343b3f',stroke_width='.38')
    if style=='atlas':
        for b in buildings:
            p=b['coordinates'];xs=[v[0] for v in p];ys=[v[1] for v in p]
            if max(xs)-min(xs)>7 and max(ys)-min(ys)>6:
                # Ridge stays clipped to the source silhouette.
                defs=P.el('defs');cl=P.el('clipPath',id='clip-'+b['id']);polygon(cl,p);defs.append(cl);g.append(defs)
                ridge=P.el('g',clip_path='url(#clip-'+b['id']+')');polyline(ridge,[[min(xs)+1,(min(ys)+max(ys))/2],[max(xs)-1,(min(ys)+max(ys))/2]],stroke='#79553a',stroke_width='.5');g.append(ridge)
    for p in piers:polygon(g,p,fill='#aa916c',stroke='#5d584d',stroke_width='.65')
    for f in walls:polyline(g,f['pixel_coordinates'],stroke='#333b42',stroke_width=2.2,stroke_linejoin='round')
    for f in walls:
        for x,y in [f['pixel_coordinates'][0],f['pixel_coordinates'][-1]]:g.append(P.el('circle',cx=x,cy=y,r=3.6,fill='#fffdf3',stroke='#333b42',stroke_width='1'))
    if labels:
        for f in P.MAN['features']:
            if f['id'].startswith('L00'):
                x,y=f['pixel_coordinates'][0];n=f['id'][-1];g.append(P.el('circle',cx=x,cy=y,r=7.5,fill='#fff8dc',stroke='#4b4d50',stroke_width='.7'));P.txt(g,x,y+3,n,9,True,'middle')
        for d in districts:
            x,y=d['anchor'];P.txt(g,x,y,d['id'][-1],12,True,'middle',fill='#202b32',stroke='#fffaf0',stroke_width='.8',paint_order='stroke')
        P.txt(g,129,268,'VILHON REACH',12,True,'middle',fill='#f0fbff')
        P.txt(g,866,200,'Emerald Corridor',9,False,'middle',fill='#52616b')
        P.txt(g,478,500,'Golden Road',9,False,'middle',fill='#52616b',transform='rotate(-58 478 500)')
    return g

KEY=[('DISTRICT KEY',['1 Port — western waterfront.','2 Warehouse — northwest blocks.','3 Merchant — southern blocks.','4 Governor — central precinct.','5 Living — eastern blocks.']),('SOURCE-KEYED PLACES',['6 The Generon — north-central.','7 Temple to Tempus — source-plan position.','8 Temple of Silvanus.','9 Temple of Lliira.']),('UNRESOLVED LOCATIONS',['Crying Claw: Warehouse District; exact plot unknown. Academia Vilhonus: Governor District, south of Generon.','Seaside, Temple of Waukeen, Efusio’s Cafe and Neely’s Cheese: no verified point coordinates assigned.'])]

def render_planar():
    P.make_plate('02-cadastral-master-v1.8','Cadastral Working Plan',city_layer(parcels=True),KEY+[('GEOMETRY AND PARCELS',[str(len(buildings))+' source roof-silhouette components, not a census of separate buildings. Roof bounds proxy ground footprints.','Thin parcel divisions and dashed district edges are inferred planning layers. Streets follow source; widths approximate.']),('READING LIMITS',['Scale/population conflict unresolved. The source plan places Tempus west of Governor; prose says east.'])],subtitle='Source geometry + explicitly inferred parcel subdivisions • no ownership claims')
    P.make_plate('04-five-districts-v1.8','Five Districts',city_layer(),KEY+[('DISTRICT BOUNDARIES',['District names and relative positions are sourced. Colored polygon edges interpret the mapped blocks; legal limits are unknown.']),('REGISTRATION',['Same coastline, source extent, streets and roof polygons as the cadastral working plan.','No arbitrary scaling to the population scenario.'])],subtitle='All five districts • interpreted block boundaries shown dashed')
    P.make_plate('05-port-district-v1.8','Port District Detail',city_layer(),[('EXTENT AND REGISTRATION',['Detail crop: atlas x=285–545, y=95–360. Uniform zoom of master geometry; no repositioning.']),('WATERFRONT',['Source-drawn piers project over the fixed water mask. They are structures, not islands.','The covered Netherwaters are not a second surface river; see the underground reconstruction.']),('NEARBY SOURCE KEYS',['1 Port District. 2 Warehouse District.','7 Temple to Tempus. 9 Temple of Lliira.','8 Temple of Silvanus appears at the detail’s southern edge.']),('LIMITS',['Roof silhouettes are source symbols; building heights and legal parcels are unknown.','Crying Claw has a Warehouse District context, but its exact plot is unresolved.','Source-stated scale retained without population-driven enlargement.'])],extent=(285,95,260,265),subtitle='Registered detail crop • shared master mask and source building positions')
    P.make_plate('08-illustrated-town-atlas-v1.8','Illustrated Town Atlas',city_layer(style='atlas'),KEY+[('ILLUSTRATION CONTRACT',['Ink-and-wash palette and roof ridges remain inside source silhouettes. Architecture is stylized; footprints are unchanged.']),('SOURCE AND INFERENCE',['District boundaries are interpretive. No added canals, parcels or named-site coordinates are presented as established fact.','Warm, humid subtropical setting; no invented vegetation footprint.'])],subtitle='Watercolor-toned vector atlas • source-anchored buildings and keyed locations')

overlay=Image.fromarray(im).convert('RGBA');od=ImageDraw.Draw(overlay)
for b in buildings:od.line([tuple(p) for p in b['coordinates']]+[tuple(b['coordinates'][0])],fill=(0,255,255,255),width=1)
overlay.convert('RGB').save(QA/'building-silhouette-overlay-r02.png')
P.writejson(QA/'thematic-validation-r02.json',{'source_roof_components':len(buildings),'coordinates_within_source_bounds':all(0<=x<1000 and 0<=y<592 for b in buildings for x,y in b['coordinates']),'building_mask_water_overlap_pixels':int(np.count_nonzero((buildingmask>0)&(water>0))),'unchanged_water_mask_sha256':P.sha(GEO/'arrabar-water-mask-r01.png'),'districts':len(districts),'piers':len(piers),'footprint_claim':'source roof silhouettes, not surveyed footprints or house count','parcel_claim':'explicitly inferred nearest-structure subdivision','pending_visual_qa':True})
print(json.dumps({'roof_components':len(buildings),'parcel_scanline_edges':len(parcel_lines)}))
if __name__=='__main__':
    render_planar();shutil.copy2(__file__,GEO/'build_arrabar_thematic.py')
