#!/usr/bin/env python3
"""WorldForge: deterministic procedural world generation, no external services."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image

PALETTE = {
    0: (11, 37, 88),      # deep sea
    1: (31, 91, 147),     # shallows
    2: (232, 212, 152),   # beach
    3: (201, 175, 105),   # desert
    4: (123, 159, 81),    # grassland
    5: (46, 111, 64),     # forest
    6: (22, 77, 55),      # rainforest
    7: (134, 142, 110),   # scrub
    8: (124, 125, 114),   # mountains
    9: (229, 235, 239),   # snow
    10: (45, 125, 180),   # lake / river
    11: (100, 141, 108),  # wetlands
}
NAMES = ['deep_ocean','ocean','beach','desert','grassland','forest','rainforest','scrub','mountain','snow','freshwater','wetland']

def noise(shape, rng, grid, persistence=.55, octaves=6):
    """Fast multiscale value noise with bilinear interpolation."""
    h,w=shape
    y,x=np.mgrid[:h,:w]
    result=np.zeros(shape,dtype=np.float32)
    amp=1.0; total=0
    for i in range(octaves):
        gh=max(2, int(grid*(2**i))); gw=max(2,int(grid*(2**i)*w/h))
        a=rng.random((gh+1,gw+1)).astype(np.float32)
        yy=y/(h-1)*gh; xx=x/(w-1)*gw
        y0=np.minimum(yy.astype(int),gh-1); x0=np.minimum(xx.astype(int),gw-1)
        fy=yy-y0; fx=xx-x0
        fy=fy*fy*(3-2*fy); fx=fx*fx*(3-2*fx)
        layer=(a[y0,x0]*(1-fx)*(1-fy)+a[y0,x0+1]*fx*(1-fy)+a[y0+1,x0]*(1-fx)*fy+a[y0+1,x0+1]*fx*fy)
        result+=layer*amp; total+=amp; amp*=persistence
    return result/total

def generate(size=512,seed=42,sea_level=.47,river_count=25):
    rng=np.random.default_rng(seed)
    h=w=size
    yy,xx=np.mgrid[:h,:w]
    # Broad continent field plus ridged terrain; slight coastal taper creates islands.
    broad=noise((h,w),rng,3,octaves=6)
    detail=noise((h,w),rng,9,octaves=5)
    ridges=1-np.abs(2*noise((h,w),rng,5,octaves=5)-1)
    # Bias toward sea at edges without always forcing land to be an island.
    edge=np.minimum.reduce((xx,yy,w-1-xx,h-1-yy)).astype(np.float32)/(size*.28)
    edge=np.clip(edge,0,1)
    elevation=np.clip(.58*broad+.19*detail+.23*ridges - .18*(1-edge),0,1)
    # Stretch elevations for useful topographical relief across seeds.
    elevation=np.clip((elevation-.25)/.48,0,1)
    moisture=noise((h,w),rng,5,octaves=6)
    temp=noise((h,w),rng,4,octaves=5)
    latitude=np.abs(yy/(h-1)*2-1)
    temperature=np.clip(.80-.54*latitude+.30*(temp-.5)-.45*np.maximum(0,elevation-.62),0,1)
    moisture=np.clip(moisture+.12*(elevation<sea_level)-.10*np.maximum(elevation-.65,0),0,1)
    land=elevation>=sea_level
    biome=np.full((h,w),4,np.uint8)
    biome[elevation<sea_level-.11]=0
    biome[(elevation>=sea_level-.11)&(~land)]=1
    biome[land & (elevation<sea_level+.022)]=2
    interior=land & (elevation>=sea_level+.022)
    biome[interior & (temperature>.48)&(moisture<.39)]=3
    biome[interior & (moisture>=.51)&(temperature>.53)]=5
    biome[interior & (moisture>=.62)&(temperature>.72)]=6
    biome[interior & (temperature<.47)]=7
    biome[interior & (elevation>.73)]=8
    biome[interior & ((temperature<.30)|(elevation>.84))]=9
    # Rivers follow downhill local minima; paths stop on oceans or stalled basins.
    # Track carved cells separately so river tracing does not alter elevation routing.
    rivers=np.zeros((h,w),bool)
    lakes=np.zeros((h,w),bool)
    high=np.argwhere((elevation>.63)&land)
    if len(high):
        rng.shuffle(high)
        starts=high[:river_count]
        neighbors=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        for sy,sx in starts:
            y,x=int(sy),int(sx)
            seen=set()
            path=[]
            for _ in range(size*3):
                if (y,x) in seen: break
                seen.add((y,x))
                if not land[y,x]: break
                path.append((y,x))
                options=[]
                for dy,dx in neighbors:
                    ny,nx=y+dy,x+dx
                    if 0<=ny<h and 0<=nx<w and (ny,nx) not in seen:
                        options.append((float(elevation[ny,nx]),ny,nx))
                if not options: break
                lowest,ny,nx=min(options)
                if lowest>=elevation[y,x]:
                    if len(path)>10:
                        lakes[max(0,y-2):min(h,y+3),max(0,x-2):min(w,x+3)]=True
                    break
                y,x=ny,nx
            if len(path)>=9:
                for py,px in path:
                    rivers[py,px]=True
    biome[lakes & land]=10
    biome[rivers & land]=10
    # Wetlands in very moist lowland pockets near rivers/lakes.
    fresh=rivers|lakes
    nearby=fresh.copy()
    for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
        ys=slice(max(0,dy),min(h,h+dy)); xs=slice(max(0,dx),min(w,w+dx))
        sy=slice(max(0,-dy),min(h,h-dy)); sx=slice(max(0,-dx),min(w,w-dx))
        nearby[ys,xs]|=fresh[sy,sx]
    wet=land & nearby & (~fresh) & (moisture>.53) & (elevation<.65)
    biome[wet]=11
    # Cave network: cellular automaton in underground slice, unrelated to top biome.
    cave_rng=np.random.default_rng(seed+29017)
    cave=(cave_rng.random((h,w))<.47)
    cave[[0,-1],:]=False; cave[:,[0,-1]]=False
    for _ in range(5):
        count=np.zeros((h,w),np.uint8)
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dy==dx==0:continue
                count[max(0,dy):min(h,h+dy),max(0,dx):min(w,w+dx)] += cave[max(0,-dy):min(h,h-dy),max(0,-dx):min(w,w-dx)]
        cave=count>=5
        cave[[0,-1],:]=False;cave[:,[0,-1]]=False
    return dict(elevation=elevation,moisture=moisture,temperature=temperature,biome=biome,caves=cave)

def save(world,directory,seed,sea_level):
    directory.mkdir(parents=True,exist_ok=True)
    palette=np.array([PALETTE[i] for i in range(len(PALETTE))],dtype=np.uint8)
    rgb=palette[world['biome']]
    # Gentle elevation shading creates legible mountains and coastal terrain.
    dy,dx=np.gradient(world['elevation'])
    shade=np.clip(1.03-1.5*dx-.9*dy,.78,1.18)
    rgb=np.clip(rgb.astype(float)*shade[...,None],0,255).astype(np.uint8)
    Image.fromarray(rgb).save(directory/'world.png')
    for key in ['elevation','moisture','temperature']:
        Image.fromarray((world[key]*255).astype(np.uint8)).save(directory/f'{key}.png')
    Image.fromarray(np.where(world['caves'],235,20).astype(np.uint8)).save(directory/'caves.png')
    counts=np.bincount(world['biome'].ravel(),minlength=len(NAMES))
    metadata={'seed':seed,'size':int(world['biome'].shape[0]),'sea_level':sea_level,'biomes':{name:int(counts[i]) for i,name in enumerate(NAMES)}}
    (directory/'world.json').write_text(json.dumps(metadata,indent=2)+'\n')
    # A portable compressed numeric dataset for further simulations.
    np.savez_compressed(directory/'world.npz',**world)
    return metadata

def main():
    p=argparse.ArgumentParser(description='WorldForge procedural world generator')
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--size',type=int,default=512)
    p.add_argument('--sea-level',type=float,default=.47)
    p.add_argument('--rivers',type=int,default=25)
    p.add_argument('--output',default='output')
    args=p.parse_args()
    if not 64<=args.size<=2048:p.error('--size must be 64..2048')
    if not .2<=args.sea_level<=.8:p.error('--sea-level must be .2..8')
    if not 0<=args.rivers<=500:p.error('--rivers must be 0..500')
    meta=save(generate(args.size,args.seed,args.sea_level,args.rivers),Path(args.output),args.seed,args.sea_level)
    print(f"Generated seed={args.seed} size={args.size}, files in {args.output}/")
    print(json.dumps(meta['biomes'],indent=2))
if __name__=='__main__':main()
