from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, shutil, zipfile, math

ROOT=Path(r'C:\repos\Source\Faerun-Economy-Engine\wiki\locations\arrabar')
OUT=ROOT/'cartography-set-v1'
SRC=OUT/'source-maps'; GEO=OUT/'working-geometry'; QA=GEO/'validation'; ASSETS=OUT/'skill-assets'
for d in [SRC,GEO,QA,ASSETS,OUT/'finished-plates']:
    d.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,obj): Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

source_names=['Arrabar_map.webp','ArrabarIA.webp','OIP.webp','arrabar-sketch.svg','arrabar.json','README.md']
inventory=[]
for name in source_names:
    source=ROOT/name; dest=SRC/name
    if dest.exists() and sha(dest)!=sha(source): raise RuntimeError('Existing copy differs: '+str(dest))
    shutil.copy2(source,dest)
    entry={'file':name,'original_path':str(source),'copy_path':str(dest),'sha256':sha(source),'size_bytes':source.stat().st_size}
    if name.endswith('.webp'): entry['pixel_size']=list(Image.open(source).size)
    inventory.append(entry)
js(SRC/'source-checksums.json',inventory)
package=Path(r'C:\Users\localadmin\Downloads\faerun-cartography-unified-master-collection.zip')
prefix='faerun-cartography-unified-master/faerun-map-geometry-master/'
with zipfile.ZipFile(package) as z:
    for rel in ['SKILL.md','references/geometry-manifest-template.json','references/validation-checklist.md']:
        target=ASSETS/'faerun-map-geometry-master'/rel; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(z.read(prefix+rel))
js(ASSETS/'recovered-asset-provenance.json',{'source_zip':str(package),'sha256':sha(package),'members_root':prefix,'status':'original files recovered; no re-creation'})

W,H=1000,592
# Trace follows the visible land edge, joining dock bases; piers are NOT land.
coast=[[338,0],[336,12],[336,24],[339,36],[346,51],[350,65],[352,81],[358,91],[364,103],[367,116],[366,129],[364,140],[362,149],[362,160],[364,171],[370,182],[373,193],[374,204],[370,215],[363,226],[355,237],[347,246],[337,255],[328,265],[321,276],[318,288],[317,301],[314,312],[307,325],[297,338],[285,352],[275,367],[265,382],[258,394],[255,409],[252,425],[250,443],[249,457],[251,472],[257,488],[265,502],[272,517],[275,531],[275,545],[279,559],[278,574],[273,585],[266,592]]
water=[[0,0]]+coast+[[0,H],[0,0]]
land=[coast[0],[W,0],[W,H],coast[-1]]+list(reversed(coast[:-1]))
mask=Image.new('L',(W,H),0); ImageDraw.Draw(mask).polygon(water,fill=255)
mask.save(GEO/'arrabar-water-mask-r01.png')
landmask=mask.point(lambda x:255-x);landmask.save(GEO/'arrabar-land-mask-r01.png')
im=Image.new('RGB',(W,H),'#f5efdf'); im.paste('#3798be',(0,0,W,H),mask)
ImageDraw.Draw(im).line(coast,fill='#354450',width=1)
im.save(GEO/'arrabar-land-water-draft-r01.png')

roads=[
 ('R01','Golden Road / main diagonal',[[435,592],[465,551],[493,505],[516,454],[530,400],[539,348],[550,305],[583,274],[625,252],[673,235],[721,224],[754,222],[803,220],[852,216],[899,210],[951,199],[1000,184]]),
 ('R02','Outer ring road',[[451,12],[487,12],[539,18],[597,31],[650,52],[705,79],[756,108],[803,149],[837,185],[849,216],[845,251],[830,284],[806,312],[773,339],[724,362],[667,379],[606,399],[559,424],[527,439],[486,441],[442,440],[401,437],[367,426],[342,409],[325,388],[317,366],[317,348],[325,331],[344,310]]),
 ('R03','Northwest ring continuation',[[451,12],[422,20],[397,35],[384,48],[379,61],[379,76],[388,97],[395,119]]),
 ('R04','North cross street',[[377,108],[457,108],[528,108],[594,108],[654,108],[663,109]]),
 ('R05','Port spine',[[376,109],[390,138],[397,164],[399,200],[397,236],[391,258],[380,281],[361,306],[339,329]]),
 ('R06','Warehouse middle street',[[363,164],[400,159],[532,159]]),
 ('R07','Warehouse south street',[[348,239],[396,252],[535,252]]),
 ('R08','West diagonal',[[327,277],[359,308],[388,327],[450,329],[537,329]]),
 ('R09','Southern cross street',[[325,342],[363,309],[398,280]]),
 ('R10','Governor west street',[[533,108],[533,246],[538,327],[529,397],[524,440]]),
 ('R11','Governor east street',[[596,109],[596,261]]),
 ('R12','Living north-south street',[[664,91],[662,169],[662,238],[659,334],[655,365]]),
 ('R13','Southern central street',[[436,330],[439,400],[442,439]]),
 ('R14','Northern west gate street',[[466,0],[467,108]]),
 ('R15','Living cross street',[[597,176],[660,176],[721,176]]),
 ('R16','Living south cross street',[[599,294],[655,294],[721,294]])]
walls=[
 ('W01',[[381,101],[396,88],[435,47],[458,46]]),
 ('W02',[[480,46],[567,46],[629,108],[652,108]]),
 ('W03',[[670,109],[721,109],[722,173],[752,207]]),
 ('W04',[[752,238],[722,269],[722,334],[671,334]]),
 ('W05',[[651,334],[628,334],[564,397],[545,397]]),
 ('W06',[[517,397],[450,397]]),
 ('W07',[[429,397],[373,397],[333,355]]),
 ('W08',[[319,340],[307,331]])]
footprints=[('B006','The Generon',[[548,136],[584,136],[584,174],[548,174]],6),('B007','Temple to Tempus',[[489,263],[528,263],[528,279],[489,279]],7),('B008','Temple of Silvanus',[[431,303],[475,303],[475,324],[431,324]],8),('B009','Temple of Lliira',[[398,258],[425,258],[425,282],[398,282]],9)]
landmarks=[('L006','The Generon',(565,154),6),('L007','Temple to Tempus',(508,271),7),('L008','Temple of Silvanus',(452,314),8),('L009','Temple of Lliira',(411,270),9)]
# Points identify district areas; district boundary polygons are not yet accepted.
districts=[('D01','Port District',(367,211)),('D02','Warehouse District',(462,203)),('D03','Merchant District',(473,367)),('D04',"Governor's District",(563,227)),('D05','Living District',(689,189))]
features=[]
def add(fid,name,typ,geom,coords,confidence='estimated',note=''):
    features.append({'id':fid,'name':name,'type':typ,'geometry_type':geom,'normalized_coordinates':[[round(x/W,7),round(y/H,7)] for x,y in coords],'pixel_coordinates':coords,'source':'ArrabarIA.webp','confidence':confidence,'note':note})
add('LW-WATER','Vilhon Reach','water','polygon',water,note='One contiguous water surface. No source islands; piers are excluded.')
add('LW-LAND','Continental land','terrain','polygon',land,note='Connected north/east/south; shoreline under small piers interpolated between visible dock bases.')
add('LW-SHORE','Visible coast / dock-base interpolation','water','polyline',coast,note='Manual digitization at source resolution; approximately 2-4 px uncertainty, larger under dock symbols.')
for fid,name,pts in roads:add(fid,name,'road','polyline',pts,note='Selected major street centerline only; widths not measured; minor streets pending.')
for fid,pts in walls:add(fid,'Source wall segment','wall','polyline',pts,note='Gate gaps preserved. Towers not yet separately digitized.')
for fid,name,pts,n in footprints:add(fid,name,'building','polygon',pts,note='Visible stylized roof/compound bounds; not a measured ground footprint. Source key '+str(n))
for fid,name,pt,n in landmarks:add(fid,name,'landmark','point',[pt],note='Source-keyed landmark '+str(n)+'; Tempus text/plan placement conflict retained in audit.')
for fid,name,pt in districts:add(fid,name,'landmark','point',[pt],note='District label anchor only, not a district boundary.')

# Three or more non-collinear control pairs; fitting does not alter the primary trace.
controls=[('NW-tower',[435,46],[220,37]),('NE-bend',[628,108],[313,67]),('SW-tower',[373,397],[190,202]),('SE-wall',[722,334],[360,174]),('S-central-tower',[517,397],[260,202])]
def solve3(a,b):
    a=[list(r)+[v] for r,v in zip(a,b)]
    for i in range(3):
        k=max(range(i,3),key=lambda j:abs(a[j][i]));a[i],a[k]=a[k],a[i]
        v=a[i][i];a[i]=[x/v for x in a[i]]
        for j in range(3):
            if j!=i:
                v=a[j][i];a[j]=[x-v*y for x,y in zip(a[j],a[i])]
    return [r[3] for r in a]
rows=[[p[0],p[1],1] for _,p,q in controls]
ata=[[sum(r[i]*r[j] for r in rows) for j in range(3)] for i in range(3)]
coeff=[solve3(ata,[sum(r[i]*q[k] for r,(_,p,q) in zip(rows,controls)) for i in range(3)]) for k in [0,1]]
registration=[]
for name,p,q in controls:
    pred=[sum(a*b for a,b in zip(c,p+[1])) for c in coeff];err=math.dist(pred,q)
    registration.append({'id':name,'atlas_px':p,'numbered_plan_px':q,'predicted_px':pred,'residual_px':err})
manifest=json.loads((ASSETS/'faerun-map-geometry-master/references/geometry-manifest-template.json').read_text())
manifest.update({'map_name':'Arrabar draft source geometry r01','source_image':'source-maps/ArrabarIA.webp','source_priority':'Interactive Atlas redrawing for draft geometry and scale; numbered Arrabar_map.webp corroborates layout. Not a user-approved geographic master.','image_width_px':W,'image_height_px':H,'north_rotation_degrees':0,'scale':{'units':'feet','pixels_per_unit':0.3,'source_bar_pixels':[777,927],'source_bar_value':500,'status':'source-stated, not verified ground survey','feet_per_pixel':500/150},'control_points':[{'id':n,'u':p[0]/W,'v':p[1]/H,'description':'Paired with numbered plan in registration.json'} for n,p,q in controls],'features':features,'elevation':{'source':'No quantitative heights supplied; text describes hills descending toward bay','vertical_datum':'unknown','contour_interval':None,'is_hypothetical':True},'notes':['No arbitrary rescaling for population of 61,012.','Source extent retained at 1000 x 592 pixels; title, key, compass and scale are source annotations, not geographic features.','Missing street-width, cadastral parcel and majority building-footprint layers remain pending, not empty verified layers.','No invented canals, river, turning basin geometry, islands, elevations or parcel boundaries in this draft.','Only key 6-9 landmarks are geometrically anchored in this revision. Positions of key 10-12 not resolved from supplied atlas rendering.']})
master_id='ARRABAR-LW-r01-DRAFT';geomsha=hashlib.sha256(json.dumps({'extent':[W,H],'shoreline':coast},sort_keys=True,separators=(',',':')).encode()).hexdigest()
manifest['master_id']=master_id;manifest['geometry_sha256']=geomsha;manifest['approval_state']='draft; not user-approved';manifest['source_sha256']=sha(SRC/'ArrabarIA.webp')
js(GEO/'geometry-manifest-r01.json',manifest)
js(GEO/'registration-r01.json',{'primary':'ArrabarIA.webp','secondary':'Arrabar_map.webp','method':'least-squares affine fit from five manually selected non-collinear controls; comparison only','matrix_atlas_to_numbered':coeff,'controls':registration,'rms_residual_px':math.sqrt(sum(r['residual_px']**2 for r in registration)/len(registration)),'warning':'Redrawings differ; never combine their footprints or average coastlines. OIP.webp has incompatible numbering and is contextual only.'})
geojson={'type':'FeatureCollection','coordinate_system':'LOCAL IMAGE PIXELS; x right, y down; NOT WGS84 and NOT georeferenced','master_id':master_id,'features':[]}
for f in features:
    g=f['geometry_type'];p=f['pixel_coordinates'];typ={'polygon':'Polygon','polyline':'LineString','point':'Point'}[g]
    coords=[p+[p[0]]] if g=='polygon' and p[-1]!=p[0] else [p] if g=='polygon' else p[0] if g=='point' else p
    geojson['features'].append({'type':'Feature','id':f['id'],'properties':{k:v for k,v in f.items() if k not in ['pixel_coordinates','normalized_coordinates','geometry_type']},'geometry':{'type':typ,'coordinates':coords}})
js(GEO/'arrabar-local-pixel-geometry-r01.geojson',geojson)

def pts(p):return ' '.join(f'{x},{y}' for x,y in p)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="592" viewBox="0 0 1000 592">',f'<metadata>{master_id}; pixel coordinates; draft manual trace; source-stated scale 500ft/150px.</metadata>',f'<g id="land"><polygon points="{pts(land)}" fill="#f5efdf"/></g>',f'<g id="water"><polygon points="{pts(water)}" fill="#3798be"/></g>',f'<g id="shoreline"><polyline points="{pts(coast)}" fill="none" stroke="#354450" stroke-width="1"/></g>','</svg>']
(GEO/'arrabar-land-water-r01.svg').write_text('\n'.join(svg),encoding='utf-8')
vector=svg[:-1]+['<g id="roads" fill="none" stroke="white" stroke-width="5">']
for fid,name,p in roads:vector.append(f'<polyline id="{fid}" points="{pts(p)}"/>')
vector+=['</g>','<g id="walls" fill="none" stroke="#42464b" stroke-width="2">']
for fid,p in walls:vector.append(f'<polyline id="{fid}" points="{pts(p)}"/>')
vector+=['</g>','<g id="keyed-building-bounds" fill="#d1b77b" stroke="#3f4144" stroke-width="1">']
for fid,name,p,n in footprints:vector.append(f'<polygon id="{fid}" points="{pts(p)}"/>')
vector+=['</g>','</svg>'];(GEO/'arrabar-draft-geometry-r01.svg').write_text('\n'.join(vector),encoding='utf-8')
source=Image.open(SRC/'ArrabarIA.webp').convert('RGB');overlay=source.copy();d=ImageDraw.Draw(overlay)
d.line(coast,fill='#ff20c7',width=2)
for fid,name,p in roads:d.line(p,fill='#fff52d',width=2)
for fid,p in walls:d.line(p,fill='#7b2cff',width=2)
for fid,name,p,n in footprints:d.line(p+[p[0]],fill='#00f8fa',width=2)
for fid,name,p,n in landmarks:d.text((p[0]+3,p[1]+3),str(n),fill='white',stroke_width=1,stroke_fill='black')
overlay.save(QA/'source-geometry-overlay-r01.png')
pure=im.copy();d=ImageDraw.Draw(pure)
for fid,name,p in roads:d.line(p,fill='#ffffff',width=5)
for fid,p in walls:d.line(p,fill='#42464b',width=2)
for fid,name,p,n in footprints:d.polygon(p,fill='#d1b77b',outline='#3f4144');d.text((p[0][0],p[0][1]),str(n),fill='black')
pure.save(GEO/'arrabar-draft-geometry-r01.png')

def comps(image,value):
    pix=image.load(); seen=bytearray(W*H); sizes=[]
    for y in range(H):
        for x in range(W):
            idx=y*W+x
            if seen[idx] or pix[x,y]!=value:continue
            seen[idx]=1;stack=[(x,y)];n=0
            while stack:
                xx,yy=stack.pop();n+=1
                for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
                    if 0<=nx<W and 0<=ny<H:
                        k=ny*W+nx
                        if not seen[k] and pix[nx,ny]==value:seen[k]=1;stack.append((nx,ny))
            sizes.append(n)
    return sizes
watercomp=comps(mask,255);landcomp=comps(mask,0)
validation={'status':'draft geometry checked; not a final-plate acceptance','master_id':master_id,'geometry_sha256':geomsha,'mask_sha256':sha(GEO/'arrabar-water-mask-r01.png'),'dimensions':[W,H],'water_convention':'255/white=water;0/black=land','water_components':len(watercomp),'land_components':len(landcomp),'islands':0,'water_pixels':sum(watercomp),'land_pixels':sum(landcomp),'land_touches_north_east_south':True,'source_copy_hashes_match':all(sha(ROOT/i['file'])==sha(SRC/i['file']) for i in inventory),'north_rotation_degrees':0,'source_scale_bar':{'from_px':[777,532],'to_px':[927,532],'pixel_length':150,'distance_feet':500,'feet_per_px':500/150,'measurement_uncertainty_px':2},'feature_counts':{'shoreline_vertices':len(coast),'selected_roads':len(roads),'wall_segments':len(walls),'keyed_building_bounds':len(footprints),'district_anchors':5},'not_passed_or_pending':['User approval of draft geographic master','Complete building and parcel tracing','Detailed district boundaries','Source-map coast overlay visual inspection','Original v1.8 frame/spec/validator/seal access on Windows','No final plate framing, grid or seal checks performed']}
js(QA/'geometry-validation-r01.json',validation)
assert len(watercomp)==1 and len(landcomp)==1
assert sum(watercomp)+sum(landcomp)==W*H
contact=Image.new('RGB',(1600,1070),'white');font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);dd=ImageDraw.Draw(contact)
panels=[(source,'SOURCE: Interactive Atlas plan (unaltered)',0,55),(im,'DRAFT: land-water trace; no piers treated as land',800,55),(overlay,'QA: trace overlay; manual source-resolution digitization',0,565),(pure,'DRAFT: selected streets / walls / four keyed sites',800,565)]
for pic,label,x,y in panels:
    contact.paste(pic.resize((800,474)),(x,y));dd.text((x+12,y-28),label,font=small,fill='black')
dd.text((12,4),'ARRABAR | PREPARATORY GEOMETRY r01 — NOT A FINISHED PLATE',font=font,fill='black')
dd.text((12,1045),'Source-stated scale retained: 500 ft / 150 px. Draft manual trace; unknown parcels, canals and elevations are not invented.',font=small,fill='black')
contact.save(QA/'arrabar-preparation-preview-r01.png')

audit='''# Arrabar cartography preparation — r01\n\nStatus: draft source geometry, not final plates or an approved geographic master.\n\n## Source authority and extent\n\nThe repository's Interactive Atlas redrawing (`ArrabarIA.webp`, 1000 × 592 px) is the draft tracing reference because it resolves individual roof symbols, named key and a numerical scale. `Arrabar_map.webp` corroborates the district and road layout. A five-point affine comparison is recorded; it does not modify or average either plan. `OIP.webp` uses a different numbering scheme and remains contextual. The old sketch is approximate and not to scale; generated illustrations are not geometry sources. All originals are preserved, with byte-identical copies and SHA-256 checksums.\n\nFull atlas extent is retained. Its overlaid title, key, compass, sea-color bands, road arrows and scale are annotations, not additional geography. The depth-color bands are not bathymetry.\n\n## Scale\n\nThe source bar's 0–500 ft interval measures about 150 px (endpoints x=777 and x=927; ±2 px reading uncertainty). Thus 1 px = 3.333… source-stated feet. This is an editorial map scale, not a ground survey. Do not enlarge it to accommodate 61,012 residents. Walled city dimensions are roughly 1,400–1,500 ft; the population/scale conflict remains unresolved.\n\n## Geometry status\n\nThe land-water draft contains one continuous western water body and one eastern mainland; no islands. The visible coast is digitized manually, interpolating between dock bases where pier symbols obscure it. Piers are excluded from land geometry. There is no plotted river or new harbor channel. Selected major street centerlines, discontinuous wall segments, four keyed building/compound bounds, and five district anchors are traced. Source rooftops are stylized; the four polygons are not surveyed ground footprints. Remaining buildings, parcel lines and district boundaries are pending rather than claimed absent.\n\nNo canals or turning basin geometry are invented in this revision. Text establishes covered canals and a water turning basin south of the Warehouse District, but does not supply its dimensions or exact location. No measured elevation or vertical datum is available.\n\n## Checks\n\nBinary mask and SVG share the same 1000 × 592 pixel frame. Automated 4-connected-component tests pass: one water region, one land region, zero isolated islands. Copy hashes match originals. Registration residuals and a source overlay are included. This is source-resolution manual digitization, not GIS georeferencing or pixel-perfect reconstruction of the published shoreline.\n\n## Production blocker\n\nThe original geometry manifest and checklist were recovered unchanged from a Downloads skill ZIP. The parent recovered the original v1.8 plat ZIP in Library. Its Windows transfer downloaded bytes but failed at library_file_transfer.py line 64 because Windows Python lacks os.setxattr; the required final file was not installed. Original frame, spec, validator and seal must be transferred before final plate generation. No replacement seal or frame was invented.\n\n## Layout and interpretation cautions\n\nWarehouse District is northwest; Generon is north-central. The supplied atlas's temple 7 is west of the Governor District, conflicting with prose that places Tempus to the east. Keep the source-mapped temple position and flag the prose discrepancy. The atlas key lists sites 10–12 but those numerals are not legible on the supplied raster, so they are not assigned invented point coordinates.\n'''
(OUT/'SOURCE-AUDIT.md').write_text(audit,encoding='utf-8')
index='''# Arrabar cartography set\n\n**Status: preparatory geometry available; final plates pending.** Originals remain unchanged.\n\n- [Source audit and assumptions](SOURCE-AUDIT.md)\n- [Source copies and checksums](source-maps/source-checksums.json)\n- [Draft land-water preview](working-geometry/arrabar-land-water-draft-r01.png)\n- [Editable land-water SVG](working-geometry/arrabar-land-water-r01.svg)\n- [Binary water mask](working-geometry/arrabar-water-mask-r01.png) — white=water, black=land\n- [Geometry manifest](working-geometry/geometry-manifest-r01.json)\n- [Editable local-pixel GeoJSON](working-geometry/arrabar-local-pixel-geometry-r01.geojson) — not geographic coordinates\n- [Editable selected geometry SVG](working-geometry/arrabar-draft-geometry-r01.svg)\n- [Registration comparison](working-geometry/registration-r01.json)\n- [Source overlay](working-geometry/validation/source-geometry-overlay-r01.png)\n- [QA results](working-geometry/validation/geometry-validation-r01.json)\n- [Four-panel preview](working-geometry/validation/arrabar-preparation-preview-r01.png)\n\n`finished-plates/` is deliberately empty. No cadastral, topographic, district, underground, isometric, illustrated-atlas or ground-level sheet is complete.\n'''
(OUT/'INDEX.md').write_text(index,encoding='utf-8')
shutil.copy2(__file__,GEO/'prepare_arrabar_geometry.py')
print(json.dumps({'output':str(OUT),'master_id':master_id,'features':len(features),'geometry_sha256':geomsha,'water_components':len(watercomp),'land_components':len(landcomp),'registration_rms_px':validation.get('registration_rms_px',math.sqrt(sum(r['residual_px']**2 for r in registration)/len(registration))),'preview':str(QA/'arrabar-preparation-preview-r01.png')},indent=2))
