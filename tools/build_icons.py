"""Build Lightning S vector artwork and native-size Windows/Tk icons. Pillow is build-only."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SIZES=(16,20,24,28,32,40,48,64,96,128,256)
PATHS=json.loads((ROOT/'assets/app-icon-paths.json').read_text())
COLORS=('#b89cf4','#f4f4f6')
def outline(points):
    """Round shallow contour joins while preserving the bolt's sharp corners."""
    commands=[]
    for i,(x,y) in enumerate(points):
        prev=points[i-1];nxt=points[(i+1)%len(points)]
        ax,ay=x-prev[0],y-prev[1];bx,by=nxt[0]-x,nxt[1]-y
        angle=math.acos(max(-1,min(1,(ax*bx+ay*by)/(math.hypot(ax,ay)*math.hypot(bx,by)))))
        if angle<math.radians(35):
            commands.append(('L',x-.4*ax,y-.4*ay))
            commands.append(('Q',x,y,x+.4*bx,y+.4*by))
        else:commands.append(('L',x,y))
    return commands

def polygon(commands):
    points=[];previous=commands[-1][-2:]
    for command in commands:
        if command[0]=='L':points.append(command[1:])
        else:
            ax,ay=previous;cx,cy,x,y=command[1:]
            for step in range(1,17):
                t=step/16;u=1-t
                points.append((u*u*ax+2*u*t*cx+t*t*x,u*u*ay+2*u*t*cy+t*t*y))
        previous=command[-2:]
    return points

OUTLINES=[outline(p) for p in PATHS]
def render(size):
    scale=size*4/1024
    image=Image.new('RGBA',(size*4,size*4));draw=ImageDraw.Draw(image)
    draw.rounded_rectangle((0,0,size*4-1,size*4-1),radius=round(140*scale),fill='#101114')
    for points,color in zip([polygon(c) for c in OUTLINES],COLORS):draw.polygon([(round(x*scale),round(y*scale)) for x,y in points],fill=color)
    return image.resize((size,size),Image.Resampling.LANCZOS)
def build():
    icons=ROOT/'icons';icons.mkdir(exist_ok=True)
    shapes=''.join('<path fill="'+color+'" d="M '+' '.join(map(str,commands[-1][-2:]))+' '+ ' '.join(command[0]+' '+' '.join(map(str,command[1:])) for command in commands)+' Z"/>' for commands,color in zip(OUTLINES,COLORS))
    (ROOT/'assets').mkdir(exist_ok=True)
    (ROOT/'assets/app-icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024"><rect width="1024" height="1024" rx="140" fill="#101114"/>'+shapes+'</svg>\n')
    frames=[render(size) for size in SIZES]
    for size,image in zip(SIZES,frames):image.save(icons/f'icon-{size}.png')
    frames[-1].save(ROOT/'app.ico',sizes=[(s,s) for s in SIZES],append_images=frames[:-1])
    render(1024).save(ROOT/'app-mark.png')
if __name__=='__main__':build()
