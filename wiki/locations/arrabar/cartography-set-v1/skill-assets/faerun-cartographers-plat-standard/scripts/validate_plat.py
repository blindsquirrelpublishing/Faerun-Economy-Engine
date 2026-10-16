#!/usr/bin/env python3
"""Validate geometric Plat Standard v1.8 metadata; exit nonzero on failure."""
import json, sys, math
from pathlib import Path

def check(m):
 errors=[]
 def test(cond,message):
  if not cond:errors.append(message)
 eq=lambda a,b: math.isclose(float(a),float(b),rel_tol=1e-5,abs_tol=1e-5)
 test(eq(m['sheet_width_in']/m['sheet_height_in'],19/13),'sheet is not 19:13')
 test(eq(m['left_panel_width_in']/m['sheet_width_in'],.20),'left panel not 20%')
 test(m['left_sections_pct']==[15,15,60,10],'sidebar zones not 15/15/60/10')
 test(m['grid_cols']=='ABCDEFGHIJKLMNOPQ' and m['grid_rows']==16,'grid dimensions/labels incorrect')
 test(eq(m['grid_cell_width_in'],m['grid_cell_height_in']),'grid cells not square')
 test(eq(m['compass_diameter_pt'],72),'compass diameter must be 72pt')
 test(eq(m['seal_width_in'],m['seal_height_in']),'seal is distorted; must be round')
 test(eq(m['scale_bar_length_in'], m['scale_bar_feet']/m['scale_feet_per_cell']*m['grid_cell_width_in']),'scale bar physically inconsistent')
 ticks=m['scale_tick_feet']; pos=m['scale_tick_positions_in']
 test(len(ticks)==len(pos) and len(ticks)>=2,'ticks mismatch')
 if len(ticks)==len(pos) and len(ticks)>=2:
  test(ticks[0]==0 and eq(pos[0],0),'ticks must start at zero')
  test(eq(ticks[-1],m['scale_bar_feet']) and eq(pos[-1],m['scale_bar_length_in']),'last tick must match scale end')
  for t,p in zip(ticks,pos):test(eq(p,t/m['scale_feet_per_cell']*m['grid_cell_width_in']),f'tick {t} position incorrect')
 return errors
if __name__=='__main__':
 if len(sys.argv)!=2:
  raise SystemExit('Usage: python validate_plat.py plate-metadata.json')
 errors=check(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')))
 if errors:
  print('FAIL\n'+'\n'.join(' - '+e for e in errors));sys.exit(1)
 print('PASS: measured layout / scale contract checks')
