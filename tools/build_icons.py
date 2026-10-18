"""Build TL vector artwork and native-size Windows/Tk icons. Pillow is build-only."""
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SIZES=(16,20,24,28,32,40,48,64,96,128,256)
PATHS=[[(128,224),(544,224),(544,352),(400,352),(400,800),(272,800),(272,352),(128,352)],[(576,224),(704,224),(704,672),(896,672),(896,800),(576,800)]]
def render(size):
    scale=size*4/1024
    image=Image.new('RGBA',(size*4,size*4));draw=ImageDraw.Draw(image)
    draw.rounded_rectangle((0,0,size*4-1,size*4-1),radius=round(176*scale),fill='#17181c')
    for points in PATHS:draw.polygon([(round(x*scale),round(y*scale)) for x,y in points],fill='white')
    return image.resize((size,size),Image.Resampling.LANCZOS)
def build():
    icons=ROOT/'icons';icons.mkdir(exist_ok=True)
    shapes=''.join('<polygon fill="#ffffff" points="'+' '.join(f'{x},{y}' for x,y in p)+'"/>' for p in PATHS)
    (ROOT/'assets').mkdir(exist_ok=True)
    (ROOT/'assets/app-icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024"><rect width="1024" height="1024" rx="176" fill="#17181c"/>'+shapes+'</svg>\n')
    frames=[render(size) for size in SIZES]
    for size,image in zip(SIZES,frames):image.save(icons/f'icon-{size}.png')
    frames[-1].save(ROOT/'app.ico',sizes=[(s,s) for s in SIZES],append_images=frames[:-1])
    render(1024).save(ROOT/'app-mark.png')
if __name__=='__main__':build()
