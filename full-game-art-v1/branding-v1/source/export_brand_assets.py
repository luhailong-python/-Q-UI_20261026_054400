"""Transparent safety padding and premultiplied downscales only; no logo redraw."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def artbox(im):return im.getchannel('A').point(lambda x:255 if x>=16 else 0).getbbox()
def add_asset(im,dest,src,operation,meta):
    dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest);box=artbox(im)
    return {'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'source':src.relative_to(R).as_posix(),'sourceSha256':sha(src),'size':list(im.size),'mode':im.mode,'alphaRange':list(im.getchannel('A').getextrema()),'visibleMarginsLTRB':[box[0],box[1],im.width-box[2],im.height-box[3]],'pivot':[.5,.5],'borderLeftBottomRightTop':[0,0,0,0],'operation':operation,'nativeDetailIncreased':False,'unityVerified':False,**meta}
def main():
    assets=[];originals=[];finals={}
    for kind in ['logo-primary','brand-emblem']:
        src=R/f'assets/native/yifu-zhen-wanyao-{kind}.png';im=Image.open(src).convert('RGBA');n=Image.open(src);n.load()
        rec=json.loads(Path(str(src)+'.generation.json').read_text(encoding='utf-8'))
        if sha(src)!=rec['sha256']:raise ValueError('Native digest')
        originals.append({'file':src.relative_to(R).as_posix(),'sha256':sha(src),'size':list(im.size),'alphaRange':list(im.getchannel('A').getextrema())})
        if kind=='logo-primary':
            size=(math.ceil(im.width*1.09/48)*48,math.ceil(im.width*1.09/48)*32)
            if size[1]<im.height:raise ValueError('Canvas too short')
            scales=[(1200,800),(768,512)]
        else:
            side=math.ceil(max(im.size)*1.1/16)*16;size=(side,side);scales=[(512,512),(256,256),(128,128)]
        offset=((size[0]-im.width)//2,(size[1]-im.height)//2);out=Image.new('RGBA',size);out.alpha_composite(im,offset)
        path=R/f'assets/yifu-zhen-wanyao-{kind}.png'
        assets.append(add_asset(out,path,src,'Native artwork placed at1:1 pixel scale on a larger transparent safety canvas; no painted content changed',{'nativeScale':1,'offsetTopLeft':list(offset)}));finals[kind]=out
        for target in scales:
            if target[0]>size[0] or target[1]>size[1]:continue
            smaller=out.convert('RGBa').resize(target,Image.Resampling.LANCZOS).convert('RGBA');dest=R/f'assets/yifu-zhen-wanyao-{kind}-{target[0]}w.png'
            assets.append(add_asset(smaller,dest,path,'Premultiplied-alpha Lanczos downscale; no AI generation or invented detail',{'sourceScaleXY':[target[0]/out.width,target[1]/out.height]}))
    b=Image.new('RGBA',(1600,1080),'#e9dfca');fontpath=R.parent/'assets/fonts/noto-cjk-sc/NotoSansCJKsc-Regular.otf';font=lambda n:ImageFont.truetype(str(fontpath),n)
    d=ImageDraw.Draw(b);d.text((28,18),'一符镇万妖 · 主Logo与符印徽记',font=font(34),fill='#174437')
    for i,bg in enumerate(['#fff4dc','#103d35']):
        tile=Image.new('RGBA',(800,530),bg);logo=finals['logo-primary'].convert('RGBa').resize((768,512),Image.Resampling.LANCZOS).convert('RGBA');tile.alpha_composite(logo,(16,9));b.alpha_composite(tile,(i*800,78))
        tile=Image.new('RGBA',(800,430),bg)
        emblem=finals['brand-emblem'].convert('RGBa').resize((360,360),Image.Resampling.LANCZOS).convert('RGBA');tile.alpha_composite(emblem,(45,24))
        for k,edge in enumerate([128,64]):
            small=finals['brand-emblem'].convert('RGBa').resize((edge,edge),Image.Resampling.LANCZOS).convert('RGBA');tile.alpha_composite(small,(470,50+k*180));ImageDraw.Draw(tile).text((460,200+k*135),str(edge)+'px',font=font(20),fill='#597463' if i==0 else '#e6d8b6')
        b.alpha_composite(tile,(i*800,628))
    R.joinpath('previews').mkdir(exist_ok=True);b.convert('RGB').save(R/'previews/brand-light-dark.jpg',quality=95)
    write(R/'records/brand-assets.json',{'generatedAtUtc':datetime.now(timezone.utc).isoformat(),'gameName':'一符镇万妖','language':'zh-Hans','brandId':'yifu-zhen-wanyao','nativeOriginals':originals,'assets':assets,'frozenExistingGameAssetsChanged':False,'runtimeTextBakedIntoLogoOnly':'一符镇万妖','toolRoute':'builtin image_gen','actualModel':None,'actualQuality':None,'unityVerified':False})
    print(json.dumps({'assets':len(assets),'nativeOriginals':len(originals)},ensure_ascii=False))
if __name__=='__main__':main()
