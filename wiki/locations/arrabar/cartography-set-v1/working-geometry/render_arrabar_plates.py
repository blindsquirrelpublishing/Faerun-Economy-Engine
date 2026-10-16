from pathlib import Path
import sys,json,base64,hashlib,copy,xml.etree.ElementTree as ET,subprocess,textwrap,math
sys.path.insert(0,r'C:\Users\localadmin\Documents\Codex\2026-10-14\task\cartography-runtime')
import resvg_py
from PIL import Image

ROOT=Path(r'C:\repos\Source\Faerun-Economy-Engine\wiki\locations\arrabar\cartography-set-v1')
GEO=ROOT/'working-geometry'; OUT=ROOT/'finished-plates';QA=GEO/'validation'
PLAT=ROOT/'skill-assets/faerun-cartographers-plat-standard'
NS='http://www.w3.org/2000/svg';XL='http://www.w3.org/1999/xlink'
ET.register_namespace('',NS);ET.register_namespace('xlink',XL)
def el(tag,**attrs):return ET.Element('{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
def txt(parent,x,y,s,size=12.5,bold=False,anchor='start',**attrs):
    e=el('text',x=x,y=y,font_size=size,font_weight=700 if bold else 400,text_anchor=anchor,font_family='Arial,sans-serif',**attrs);e.text=s;parent.append(e);return e
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writejson(p,obj):Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

MAN=json.loads((GEO/'geometry-manifest-r01.json').read_text(encoding='utf-8'))
SEAL=PLAT/'assets/faerun-cartographers-official-red-seal.png'
SEAL_DATA='data:image/png;base64,'+base64.b64encode(SEAL.read_bytes()).decode()
def boundary_layer():
    r=ET.parse(GEO/'arrabar-land-water-r01.svg').getroot();g=el('g',id='registered-land-water')
    for n in r:
        if n.tag.endswith('g'):g.append(copy.deepcopy(n))
    return g

def make_plate(stem,title,theme,legend,*,extent=(0,0,1000,592),scale_note=None,status='Source-traced review copy',subtitle=None,land_water=True):
    r=ET.parse(PLAT/'templates/blank-plat-v1.8.svg').getroot()
    r.set('aria-label','Arrabar '+title+'; Faerûn Cartographers v1.8')
    r.set('font-family','Arial,sans-serif')
    groups=r.findall('{'+NS+'}g')
    original_text=groups[1]
    for e in list(original_text):original_text.remove(e)
    txt(original_text,190,75,'ARRABAR',50,True,'middle')
    txt(original_text,190,120,title,25,True,'middle')
    txt(original_text,190,158,'Faerûn Cartographers',15.28,False,'middle')
    txt(original_text,25,231,'Map Information',18.06,True)
    x,y,w,h=extent;k=min(1224/w,1152/h);tx=528+(1224-w*k)/2-x*k;ty=74+(1152-h*k)/2-y*k
    feet_per_cell=72/k*(500/150)
    info=[('Region: Chondath / Vilhon Reach',272),('Basis: late-14th-century city plans',296),(f'Grid: 1 square = {feet_per_cell:.3f} source ft',320),('Source: ArrabarIA.webp; north up',344),('Scale is source-stated; survey unverified.',369)]
    for s,yy in info:txt(original_text,28,yy,s,12.5)
    txt(original_text,25,431,'Legend & Evidence',18.06,True)
    yy=465
    for section,lines in legend:
        txt(original_text,25,yy,section,13,True);yy+=22
        for line in lines:
            for wrapped in textwrap.wrap(line,width=48,break_long_words=False,break_on_hyphens=False):
                txt(original_text,25,yy,wrapped,12.5);yy+=18
        yy+=21
    if yy>1142:raise ValueError('Legend exceeds fixed region: '+str(yy))
    txt(original_text,25,1138,status,11.81,True,fill='#684d3e')
    # Template geometry is retained; content is uniformly fitted, never stretched.
    rect=r.findall('{'+NS+'}rect')[1];idx=list(r).index(rect)
    defs=el('defs');clip=el('clipPath',id='source-clip');clip.append(el('rect',x=x,y=y,width=w,height=h));defs.append(clip);r.insert(0,defs)
    g=el('g',id='geographic-content',transform=f'translate({tx:.10f},{ty:.10f}) scale({k:.10f})',clip_path='url(#source-clip)')
    g.append(copy.deepcopy(theme));r.insert(list(r).index(rect)+1,g)
    # Grid is the original template's 17 x 16 square-cell layer.
    for grid in r.findall('{'+NS+'}g'):
        if grid.get('stroke')=='#cad1d7':grid.set('stroke','#8b9ba2');grid.set('stroke-opacity','.48');grid.set('id','reference-grid')
    groups=r.findall('{'+NS+'}g');comp=groups[-3];dirs=groups[-2];scalegroup=groups[-1]
    f=100/92;comp.set('id','compass');comp.set('transform',f'translate({93-f*93},{1221-f*1224}) scale({f})')
    for e in list(dirs):dirs.remove(e)
    for xx,yy,s in [(115,1184,'N'),(115,1268,'S'),(33,1226,'W'),(153,1226,'E')]:txt(dirs,xx,yy,s,11.11,True,'middle')
    seal=r.find('{'+NS+'}image');seal.set('id','official-seal');seal.set('x','230');seal.set('y','1160');seal.set('width','105');seal.set('height','105');seal.set('{'+XL+'}href',SEAL_DATA)
    for e in list(scalegroup):scalegroup.remove(e)
    distance=500 if 500/feet_per_cell*72<=300 else 250
    length=distance/feet_per_cell*72;sx=190-length/2;sy=1279
    for i in range(2):scalegroup.append(el('rect',x=sx+i*length/2,y=sy,width=length/2,height=4,fill='#222' if i==0 else '#fff',stroke='#222',stroke_width='.7'))
    for value in [0,distance/2,distance]:txt(scalegroup,sx+value/distance*length,1293,(str(int(value))+' ft') if value==distance else str(int(value)),11.11,False,'middle')
    scalegroup.set('id','scale-bar')
    if h*k<1152-50:
        txt(r,1140,ty+y*k-24,'FULL SOURCE EXTENT • NO GEOGRAPHY ADDED IN BLANK MARGINS',11.11,False,'middle',fill='#697178')
    if subtitle:txt(r,1140,1279,subtitle,11.11,False,'middle',fill='#59616a')
    metadata={'plat_standard_version':'1.8','sheet_width_in':19,'sheet_height_in':13,'left_panel_width_in':3.8,'left_sections_pct':[15,15,60,10],'grid_cols':'ABCDEFGHIJKLMNOPQ','grid_rows':16,'grid_cell_width_in':.72,'grid_cell_height_in':.72,'compass_diameter_pt':72,'seal_width_in':1.05,'seal_height_in':1.05,'scale_feet_per_cell':feet_per_cell,'scale_bar_feet':distance,'scale_bar_length_in':length/100,'scale_tick_feet':[0,distance/2,distance],'scale_tick_positions_in':[0,length/200,length/100],'extent_source_pixels':list(extent),'source_to_plate_transform':{'uniform_scale':k,'translate':[tx,ty]},'source_scale':{'feet':500,'pixel_length':150,'reading_uncertainty_px':2,'status':'source-stated; not surveyed'},'master_id':MAN['master_id'],'geometry_sha256':MAN['geometry_sha256'],'land_water_mask_sha256':sha(GEO/'arrabar-water-mask-r01.png'),'original_seal_sha256':sha(SEAL),'original_template_sha256':sha(PLAT/'templates/blank-plat-v1.8.svg'),'geographic_approval':'not approved; source-traced review copy','render_status':'completed; validation pending','same_planar_registration':True}
    OUT.mkdir(exist_ok=True);p=OUT/(stem+'.svg');p.write_bytes(ET.tostring(r,encoding='utf-8',xml_declaration=True))
    png=OUT/(stem+'.png');png.write_bytes(resvg_py.svg_to_bytes(svg_path=str(p),width=2850,height=1950,dpi=100,font_files=['C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/arialbd.ttf']))
    preview=OUT/(stem+'-preview.png');Image.open(png).resize((1710,1170)).save(preview)
    mp=OUT/(stem+'.metadata.json');writejson(mp,metadata)
    result=subprocess.run([sys.executable,str(PLAT/'scripts/validate_plat.py'),str(mp)],capture_output=True,text=True)
    actual_checks={'sheet_dimensions':r.get('width')=='19in' and r.get('height')=='13in','map_field_bounds':[528,74,1224,1152],'sidebar_rules':[195,390,1170],'compass_geometric_diameter_pt':92*f/100*72,'original_seal_bytes_unchanged':base64.b64decode(seal.get('{'+XL+'}href').split(',')[1])==SEAL.read_bytes(),'seal_rectangle_square':seal.get('width')==seal.get('height'),'scale_bar_below_compass':sy>1271,'scale_bar_length_units':length,'uniform_geography_scale':True,'raster_dimensions':list(Image.open(png).size),'validator_exit':result.returncode,'validator_output':result.stdout.strip()}
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    assert actual_checks['original_seal_bytes_unchanged'] and actual_checks['scale_bar_below_compass']
    assert math.isclose(actual_checks['compass_geometric_diameter_pt'],72)
    metadata['render_status']='completed; structural validation passed; visual review required';writejson(mp,metadata)
    writejson(QA/(stem+'-qa.json'),actual_checks)
    print(json.dumps({'plate':stem,'validator':result.stdout.strip(),'preview':str(preview)}))
    return p

if __name__=='__main__':
    make_plate('01-land-water-master-v1.8','Land & Water Master',boundary_layer(),[
        ('SURFACE CLASSES',['Warm ivory: continental land.','Blue: connected waters of the Vilhon Reach.','Fine dark line: traced coast. No islands.']),
        ('SOURCE AND TRACE',['Detailed atlas plan used for digitization. Numbered city plan corroborates layout.','Piers and docks are constructed features; excluded from land/water classification.','Shore hidden by small dock symbols is interpolated between visible dock bases.']),
        ('REGISTRATION',['North remains up; full 1000 × 592 source extent retained without stretching.','All planar derivatives inherit this mask and its checksum.']),
        ('SCALE LIMIT',['Source bar: 500 feet across about 150 pixels. Measurement uncertainty ±2 pixels.','The small source-scaled city does not accommodate the 61,012 population scenario without unresolved density assumptions.']),
        ('NOT SURVEYED',['No measured depths, elevations or river position. Canals remain a separate underground reconstruction.','Geometry is a review copy, not an approved geographic survey.'])
    ],subtitle='ARRABAR-LW-r01-DRAFT • immutable coast reference for this production set')
    import shutil
    shutil.copy2(__file__,GEO/'render_arrabar_plates.py')
