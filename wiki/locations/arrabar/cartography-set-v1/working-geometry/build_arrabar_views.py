from pathlib import Path
import sys,json,math,copy,shutil,xml.etree.ElementTree as ET
sys.path.insert(0,r'C:\Users\localadmin\Documents\Codex\2026-10-14\task')
import render_arrabar_plates as P
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Point,Polygon
R=P.ROOT;G=P.GEO;O=R/'finished-views';O.mkdir(exist_ok=True)
D=json.loads((G/'arrabar-thematic-geometry-r02.json').read_text(encoding='utf-8'))
M=P.MAN;B=D['source_roof_silhouettes'];water=next(f['pixel_coordinates'] for f in M['features'] if f['id']=='LW-WATER');land=next(f['pixel_coordinates'] for f in M['features'] if f['id']=='LW-LAND')
coast=next(f['pixel_coordinates'] for f in M['features'] if f['id']=='LW-SHORE')
def shore(y):
 for a,b in zip(coast,coast[1:]):
  if min(a[1],b[1])<=y<=max(a[1],b[1]) and a[1]!=b[1]:return a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
 return 338
def ground(x,y):return max(x-shore(y),0)*.025
def height(b):
 x,y=b['centroid_source_pixels'];return 12 if 548<x<580 and 130<y<175 else 5.4+(int(b['id'][2:])%4)*1.2
def poly(parent,p,**attr):parent.append(P.el('polygon',points=' '.join(f'{x:.3f},{y:.3f}' for x,y in p),**attr))
def line(parent,p,**attr):parent.append(P.el('polyline',points=' '.join(f'{x:.3f},{y:.3f}' for x,y in p),fill='none',**attr))
def iso(p,z=0):x,y=p;return (.8660254*(x-y),.5*(x+y)-z)
def iso_ref():
 root=P.el('svg',width='2200',height='1550',viewBox='0 0 2200 1550');root.append(P.el('rect',width=2200,height=1550,fill='#f8f4e9'))
 P.txt(root,90,85,'ARRABAR | REGISTERED AXONOMETRIC VIEW',38,True)
 P.txt(root,90,127,'Source plan preserved; all heights and architectural details are conceptual.',24)
 g=P.el('g',transform='translate(820,230) scale(1.4)');root.append(g)
 poly(g,[iso(p,0) for p in water],fill='#6fa7b5',stroke='#426875',stroke_width='.7')
 poly(g,[iso(p,ground(*p)) for p in land],fill='#e6dabb',stroke='#81775f',stroke_width='.7')
 for d in D['districts']:poly(g,[iso(p,ground(*p)) for p in d['coordinates']],fill=d['color'],fill_opacity='.45')
 for r in D['roads']:line(g,[iso(p,ground(*p)+.1) for p in r['pixel_coordinates']],stroke='#faf5df',stroke_width=8 if r['id']=='R01' else 5)
 for p in D['piers']:poly(g,[iso(q,1) for q in p['coordinates']],fill='#ad8a61',stroke='#675f4b',stroke_width='.7')
 objs=[]
 for b in B:
  pts=b['coordinates'];z=ground(*b['centroid_source_pixels']);h=height(b)
  for a,c in zip(pts,pts[1:]+pts[:1]):
   shade='#c8b392' if c[0]-a[0]>0 else '#ab9478'
   objs.append((sum(a+c)/2,[iso(a,z),iso(c,z),iso(c,z+h),iso(a,z+h)],shade))
  objs.append((sum(b['centroid_source_pixels'])+.1,[iso(p,z+h) for p in pts],'#b8764b'))
 for f in D['walls']:
  pts=f['pixel_coordinates']
  for a,c in zip(pts,pts[1:]):
   za=ground(*a);zc=ground(*c);objs.append((sum(a+c)/2,[iso(a,za),iso(c,zc),iso(c,zc+6),iso(a,za+6)],'#a69d85'))
 for _,p,c in sorted(objs,key=lambda q:q[0]):poly(g,p,fill=c,stroke='#504b42',stroke_width='.38')
 # North-direction arrow follows projection; this is not a planimetric scale bar.
 line(root,[(1920,1350),(2040,1280)],stroke='#263b42',stroke_width=4);poly(root,[(2040,1280),(2019,1285),(2034,1304)],fill='#263b42')
 P.txt(root,2055,1281,'N',28,True)
 P.txt(root,90,1465,'403 traced roof components | No buildings relocated | Source extent retained | Vertical dimensions unverified',23)
 P.txt(root,90,1505,'ARRABAR-LW-r01-DRAFT | Scenic projection: use the cadastral sheets for horizontal measurements.',21)
 path=O/'07-isometric-registered-reference.svg';path.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
 (O/'07-isometric-registered-reference.png').write_bytes(P.resvg_py.svg_to_bytes(svg_path=str(path),font_files=['C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/arialbd.ttf']))
 return {'projection':'x=.8660254*(x-y); y=.5*(x+y)-z','source_extent':[0,0,1000,592],'roof_component_count':len(B),'heights':'conceptual 18-30 ft ordinary, 40 ft Generon zone; not measured','terrain':'conceptual 2.5 percent rise away from source coastline','exact_plan_coordinates_preserved':True}
def perspective_ref(name,cam,bearing,fov):
 W,H=1600,1000;eye=ground(*cam)+1.65 if name=='street' else 1.65
 t=math.radians(bearing);fx,fy=math.sin(t),-math.cos(t);rx,ry=math.cos(t),math.sin(t);f=W/(2*math.tan(math.radians(fov)/2));horizon=H*.48
 def cv(p):x,y,z=p;return ((x-cam[0])*rx+(y-cam[1])*ry,z-eye,(x-cam[0])*fx+(y-cam[1])*fy)
 def clip(pts):
  out=[]
  for a,b in zip(pts,pts[1:]+pts[:1]):
   ain=a[2]>.6;bin=b[2]>.6
   if ain:out.append(a)
   if ain!=bin:
    v=(.6-a[2])/(b[2]-a[2]);out.append(tuple(a[i]+v*(b[i]-a[i]) for i in range(3)))
  return out
 def screen(ps):return [(W/2+f*a/c,horizon-f*b/c) for a,b,c in ps]
 faces=[];visible=[]
 for b in B:
  pts=b['coordinates'];z=ground(*b['centroid_source_pixels']);h=height(b);anyvis=False
  ps3=[[(a[0],a[1],z),(c[0],c[1],z),(c[0],c[1],z+h),(a[0],a[1],z+h)] for a,c in zip(pts,pts[1:]+pts[:1])]
  ps3.append([(x,y,z+h) for x,y in pts])
  for i,ps in enumerate(ps3):
   clipped=clip([cv(p) for p in ps])
   if len(clipped)<3:continue
   sp=screen(clipped)
   if max(p[0] for p in sp)<0 or min(p[0] for p in sp)>W:continue
   anyvis=True;faces.append((sum(p[2] for p in clipped)/len(clipped),sp,'#b97950' if i==len(ps3)-1 else '#d0c1a8'))
  if anyvis:visible.append(b['id'])
 im=Image.new('RGB',(W,H),'#d9e9e9');dr=ImageDraw.Draw(im);dr.rectangle((0,horizon,W,H),fill='#c5bda4')
 if name=='harbor':dr.rectangle((0,H*.63,W,H),fill='#639baa')
 for _,p,c in sorted(faces,key=lambda q:-q[0]):dr.polygon(p,fill=c,outline='#4b5150')
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',28)
 dr.rectangle((0,0,W,94),fill='#fffaf0');dr.text((24,14),f'ARRABAR | {name.upper()} CAMERA GEOMETRY REFERENCE',font=bold,fill='#263739');dr.text((24,53),f'Observer {cam}; bearing {bearing} degrees; FOV {fov} degrees; eye height 5.5 ft. Heights conceptual.',font=font,fill='#263739')
 dr.rectangle((0,H-54,W,H),fill='#fffaf0');dr.text((24,H-41),'Source footprint projection with depth-sorted occlusion; architecture and terrain are unverified.',font=font,fill='#263739')
 path=G/f'{name}-camera-reference.png';im.save(path)
 return {'id':name,'position_source_pixels':cam,'bearing_degrees_clockwise_from_north':bearing,'eye_height_ft':5.5,'field_of_view_degrees':fov,'eye_z_source_px':eye,'potentially_visible_components':visible,'visibility_method':'near-plane clipping and depth-sorted source polygon faces; approximate painter occlusion, no invented footprint relocation','reference':str(path),'camera_inside_roof_polygon':any(Polygon(b['coordinates']).contains(Point(cam)) for b in B)}
def basin_ref():
 im=Image.new('RGB',(1600,1000),'#f5f0e2');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',34)
 d.text((60,40),'ARRABAR | TURNING BASIN: CONCEPTUAL CUTAWAY',font=bold,fill='#233d44')
 d.polygon([(250,350),(800,150),(1380,350),(800,580)],fill='#b8aa8c',outline='#4d564e')
 d.ellipse((620,285,950,425),fill='#fff5d0',outline='#3e5350',width=5)
 d.polygon([(250,350),(250,750),(800,940),(800,580)],fill='#8d8172',outline='#4d564e')
 d.polygon([(800,580),(800,940),(1380,700),(1380,350)],fill='#aa987c',outline='#4d564e')
 d.ellipse((330,510,1290,860),fill='#528a96',outline='#2b535e',width=6)
 d.arc((330,440,1290,790),180,360,fill='#3c4849',width=8)
 d.line((620,355,620,640),fill='#d1b881',width=4);d.line((950,355,950,640),fill='#d1b881',width=4)
 d.polygon([(1200,630),(1500,520),(1530,590),(1240,710)],fill='#528a96',outline='#2b535e')
 d.polygon([(330,640),(140,530),(110,590),(330,740)],fill='#528a96',outline='#2b535e')
 d.polygon([(660,720),(800,675),(900,720),(760,765)],fill='#7c5031',outline='#402f25')
 for xy,tx in [((80,160),'Street and cellar level above'),((1000,230),'Small light well'),((80,900),'Broad water basin for turning boats'),((1090,900),'Covered canal')]:d.text(xy,tx,font=font,fill='#233d44')
 d.text((60,960),'Plan anchor (460,282); all underground dimensions and architecture are inferred. No mechanical turntable.',font=font,fill='#233d44')
 im.save(G/'basin-cutaway-reference.png')
def contact():
 files=sorted(P.OUT.glob('*-preview.png'));w,h=760,520;gap=24;header=110;rows=math.ceil(len(files)/2)
 im=Image.new('RGB',(2*w+3*gap,header+rows*(h+55)+gap),'#eeeae0');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',38)
 dr.text((gap,20),'ARRABAR | MAP REVIEW CONTACT SHEET',font=bold,fill='#263a40');dr.text((gap,70),'Source-traced review copies. Inferred parcels, relief and canals are identified on each sheet.',font=font,fill='#263a40')
 for i,p in enumerate(files):
  x=gap+(i%2)*(w+gap);y=header+(i//2)*(h+55);im.paste(Image.open(p).resize((w,h)),(x,y));dr.text((x,y+h+10),p.stem.replace('-v1.8-preview',''),font=font,fill='#263a40')
 path=R/'arrabar-completed-maps-contact-sheet.png';im.save(path)
 return str(path)
if __name__=='__main__':
 report={'master_id':M['master_id'],'land_water_geometry_sha256':M['geometry_sha256'],'isometric':iso_ref(),'cameras':[perspective_ref('harbor',[340,210],80,68),perspective_ref('street',[661,315],0,65)],'basin_camera':{'position_source_pixels':[439,290],'bearing':45,'fov':70,'eye_height_ft':5.5,'all_underground_geometry':'explicitly conceptual','water_basin_anchor':[460,282]}}
 basin_ref();P.writejson(G/'view-camera-manifest-r01.json',report);print(json.dumps({'contact_sheet':contact(),'cameras':[{k:v for k,v in c.items() if k!='potentially_visible_components'} for c in report['cameras']]}));shutil.copy2(__file__,G/'build_arrabar_views.py')
