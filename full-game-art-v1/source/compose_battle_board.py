"""Static art proportion/camera review. No game or replacement UI implementation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R.parent/'original-monsters-v1'
IDS=['hero_daotong','hero_lingyi','hero_leixiu','orig_mob01','orig_mob02','orig_mob03','orig_mob04','orig_mob05','orig_mob06','orig_boss_minor','orig_boss01']
NAMES=['青云道童','清荷灵医','玄霆道人','青符灵','苔玉小魁','灯芯小魅','竹甲小妖','桃木小傀','玄甲山魈','铜铃卫','玄坛石尊']
def file(actor):
 if actor.startswith('hero'):return O/f'assets/heroes/{actor}.png'
 if actor in ['orig_mob05','orig_mob06']:return R/f'assets/actors/{actor}.png'
 return O/f'assets/runtime/{actor}_runtime_E.png'
def font(n):return ImageFont.truetype(str(R/'assets/fonts/noto-cjk-sc/NotoSansCJKsc-Regular.otf'),n)
def ground(size,uv):
 tex=Image.open(R/'assets/native/env_battle_ground_01.png').convert('RGB');tex.thumbnail((626,626),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',size);w,h=tex.size
 for y in range(-uv[1]%h-h,size[1],h):
  for x in range(-uv[0]%w-w,size[0],w):out.paste(tex,(x,y))
 return out
def main():
 proof=[]
 for orientation,size in [('landscape',(1920,1080)),('portrait',(1080,1920))]:
  w,h=size;out=ground(size,(210,130));d=ImageDraw.Draw(out)
  d.rectangle((0,0,w,116),fill='#f7eed8');d.text((28,14),'道家Q版 · 全角色战斗美术比例审阅',font=font(34 if w>1100 else 30),fill='#174437')
  d.text((28,67),'1个生存场景 · 3名角色 / 6普通怪 / 2首领 · 非新增玩法或UI',font=font(24 if w>1100 else 21),fill='#486457')
  if orientation=='landscape':positions=[(.32,.61),(.5,.61),(.68,.61),(.13,.32),(.31,.32),(.49,.32),(.67,.32),(.85,.32),(.14,.89),(.45,.9),(.79,.9)]
  else:positions=[(.23,.66),(.5,.66),(.77,.66),(.2,.29),(.5,.29),(.8,.29),(.2,.46),(.5,.46),(.8,.46),(.29,.9),(.71,.9)]
  records=[]
  for actor,name,(px,py) in zip(IDS,NAMES,positions):
   src=file(actor);im=Image.open(src).convert('RGBA');b=im.getchannel('A').point(lambda x:255 if x>=16 else 0).getbbox();body=b[3]-b[1]
   display=230 if actor.startswith('orig_boss') else 168 if actor.startswith('hero') else 135
   scale=display/body;rs=[round(im.width*scale),round(im.height*scale)];art=im.convert('RGBa').resize(rs,Image.Resampling.LANCZOS).convert('RGBA');root=[round(px*w),round(py*h)];offset=[round(root[0]-512*scale),round(root[1]-896*scale)]
   shadow=Image.open(R/'assets/utility/soft_shadow.png').convert('RGBA');shadow=shadow.convert('RGBa').resize((round(display*.9),round(display*.3)),Image.Resampling.LANCZOS).convert('RGBA');out.alpha_composite(shadow,(root[0]-shadow.width//2,root[1]-shadow.height//2));out.alpha_composite(art,offset)
   d=ImageDraw.Draw(out);tb=d.textbbox((0,0),name,font=font(23));tx=root[0]-(tb[2]-tb[0])//2;ty=root[1]+12;d.rounded_rectangle((tx-8,ty-3,tx+tb[2]+8,ty+31),radius=7,fill='#f8efd9');d.text((tx,ty),name,font=font(23),fill='#174437')
   records.append({'actor':actor,'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'displayBodyHeightPx':display,'uniformScale':scale,'rootXY':root,'offsetTopLeft':offset})
  out.convert('RGB').save(R/f'previews/battle-art-{orientation}.jpg',quality=95)
  proof.append({'orientation':orientation,'canvas':list(size),'actors':records})
 # Four distinct global UV offsets; never randomize separate tile boundaries.
 board=Image.new('RGB',(1280,720));uvs=[(0,0),(200,150),(500,300),(900,750)]
 for i,uv in enumerate(uvs):
  piece=ground((640,360),uv).convert('RGB');board.paste(piece,((i%2)*640,(i//2)*360))
 board.save(R/'previews/ground-uv-offsets.jpg',quality=95)
 (R/'records/battle-board-layout.json').write_text(json.dumps({'scope':'Static art/camera proportion review, no gameplay or Unity validation','all11ActorsShown':True,'multipleHeroesShownOnlyForArtReview':True,'groundNativeSize':[1254,1254],'groundPreviewTileSize':[626,626],'uvOffsetPreviews':uvs,'viewports':proof,'unityVerified':False},ensure_ascii=False,indent=2),encoding='utf-8')
 print('Wrote landscape/portrait and UV-offset art previews')
if __name__=='__main__':main()
