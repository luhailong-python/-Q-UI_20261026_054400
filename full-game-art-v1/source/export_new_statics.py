"""Export only G's approved original stills and explicitly authorized technical data.

No image-generation calls, repainting, per-pixel noise deletion, or body animation.
"""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
import numpy as np

G=Path(__file__).resolve().parents[1]
T=16
NAMES={'orig_mob05':'桃木小傀','orig_mob06':'玄甲山魈'}
SEED=2026102801

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def bbox(im):return im.getchannel('A').point(lambda x:255 if x>=T else 0).getbbox()
def metrics(im):
 a=np.array(im.getchannel('A'));b=bbox(im);w,h=im.size
 return {'size':[w,h],'mode':im.mode,'alphaRange':[int(a.min()),int(a.max())],'visibleBBoxAlpha16':list(b) if b else None,'visibleMarginsLTRB':[b[0],b[1],w-b[2],h-b[3]] if b else None,'edgeMaxAlphaLTRB':[int(a[:,0].max()),int(a[0].max()),int(a[:,-1].max()),int(a[-1].max())],'alphaExactly1Pixels':int((a==1).sum())}
def source(p):
 im=Image.open(p);im.load()
 if im.mode!='RGBA' or im.getchannel('A').getextrema()[0]!=0:raise ValueError('Real RGBA Alpha required '+str(p))
 record=Path(str(p)+'.generation.json');j=json.loads(record.read_text(encoding='utf-8-sig'))
 if j['sha256']!=sha(p):raise ValueError('Native generation-record SHA mismatch')
 return im,record,j

def fit(im,size,pad,foot=False):
 box=bbox(im)
 if not box:raise ValueError('Empty subject')
 w,h=im.size;bw,bh=box[2]-box[0],box[3]-box[1]
 scale=min(1,(size[0]-2*pad)/bw,(size[1]-2*pad)/bh)
 for _ in range(6):
  rs=(max(1,round(w*scale)),max(1,round(h*scale)))
  resized=im.convert('RGBa').resize(rs,Image.Resampling.LANCZOS).convert('RGBA');b=bbox(resized)
  rw,rh=b[2]-b[0],b[3]-b[1]
  if rw<=size[0]-2*pad and rh<=size[1]-2*pad:break
  scale*=min((size[0]-2*pad)/rw,(size[1]-2*pad)/rh)*.999
 if foot:
  target=[512,896];off=[round(512-(b[0]+b[2])/2),896-b[3]];anchor=[(box[0]+box[2])/2,box[3]];pivot=[.5,.125]
 else:
  target=[size[0]//2,size[1]//2];off=[round(target[0]-(b[0]+b[2])/2),round(target[1]-(b[1]+b[3])/2)];anchor=[(box[0]+box[2])/2,(box[1]+box[3])/2];pivot=[.5,.5]
 out=Image.new('RGBA',size);out.alpha_composite(resized,off);m=metrics(out)
 if min(m['visibleMarginsLTRB'])<pad:raise ValueError('Visible padding failed')
 a=np.array(resized.getchannel('A'));yy,xx=np.indices(a.shape);lost=a[(xx+off[0]<0)|(xx+off[0]>=size[0])|(yy+off[1]<0)|(yy+off[1]>=size[1])]
 if lost.size and lost.max()>=T:raise ValueError('Visible source would be clipped')
 transform={'requestedUniformScale':scale,'actualRasterScaleXY':[rs[0]/w,rs[1]/h],'resizedWholeOwnershipCanvas':list(rs),'offsetTopLeft':off,'sourceAnchorXY':anchor,'outputAnchorTopLeftXY':target,'sourceSubjectBBoxAlpha16':list(box),'anchorDefinition':'Static complete-body Alpha>=16 bbox bottom, horizontally centered; this does not register an animation' if foot else 'Static visible-subject center','pivotBottomLeft':pivot,'resampling':'Premultiplied-alpha Pillow RGBa Lanczos, then unpremultiply; never upscale','wholeSourceOrOwnershipCanvasPlaced':True,'perFrameBBoxScaling':False,'sourcePixelsDeletedToCleanEdges':False,'outsideOutput':{'nonzeroAlphaPixels':int((lost>0).sum()),'visibleAlpha16Pixels':int((lost>=T).sum()),'maxAlpha':int(lost.max()) if lost.size else 0}}
 return out,transform,m

def save_derived(im,p,identity,name,purpose,native,gen,rect,transform,source_metrics):
 p.parent.mkdir(parents=True,exist_ok=True);im.save(p);m=metrics(im)
 rec={'id':identity,'name':name,'purpose':purpose,'file':p.relative_to(G).as_posix(),'sha256':sha(p),'size':list(im.size),'mode':im.mode,'alphaRange':m['alphaRange'],'pivot':transform['pivotBottomLeft'],'borderLeftBottomRightTop':[0,0,0,0],'sourceAtlas':native.relative_to(G).as_posix(),'sourceSha256':sha(native),'sourceGenerationRecord':gen.relative_to(G).as_posix(),'sourceRectTopLeftXYWH':rect,'sourceMeasurements':source_metrics,'transform':transform,'measurements':m,'operation':'Technical ownership crop/one uniform downscale/transparent placement of existing same-project original art; no AI edit or newly drawn details','newAIGeneration':False,'nativeDetailIncreased':False,'staticOnly':True,'animationClaimed':False,'sourceArtFromFDrive':False,'unityVerified':False,'exportedAtUtc':datetime.now(timezone.utc).isoformat()}
 write(Path(str(p)+'.derived.json'),rec);return rec

def main():
 entries=[];warnings=[];sources=[]
 for aid,name in NAMES.items():
  native=G/f'assets/native/{aid}.png';im,gen,j=source(native);digest=sha(native);sm=metrics(im)
  for purpose,folder,size,pad,foot in [('runtime','actors',(1024,1024),128,True),('portrait','portraits',(512,512),64,False),('target','targets',(256,256),32,False)]:
   out,transform,m=fit(im,size,pad,foot)
   rec=save_derived(out,G/f'assets/{folder}/{aid}.png',aid+'_'+purpose,name,purpose,native,gen,[0,0,im.width,im.height],transform,sm);entries.append(rec)
  if max(sm['edgeMaxAlphaLTRB'])>0:warnings.append({'id':'native_edge_alpha','file':native.relative_to(G).as_posix(),'value':sm['edgeMaxAlphaLTRB'],'visibleThreshold':T,'blocking':max(sm['edgeMaxAlphaLTRB'])>=T,'meaning':'Source preserved; raw-view brightRGB at alpha1 is not automatically a visible dirty edge.'})
  if sha(native)!=digest:raise ValueError('Native actor was modified')
  sources.append({'file':native.relative_to(G).as_posix(),'sha256':digest,'unchangedAfterExport':True})
 native=G/'assets/native/utility_effects.png';im,gen,j=source(native);digest=sha(native);a=np.array(im.getchannel('A'))
 # Real measured transparent runs X[659,789),Y[695,955); partition at their interior.
 xsplit=724;ysplit=825
 if a[:,xsplit-1:xsplit+1].max()>1 or a[ysplit-1:ysplit+1,:].max()>1:raise ValueError('Planned ownership is no longer inside measured transparency')
 specs=[('fx_gravity_well','地面引力井','effects',(512,512),[0,0,xsplit,ysplit]),('look_indicator','朝向指示环','utility',(256,256),[xsplit,0,im.width-xsplit,ysplit]),('soft_shadow','通用接地阴影','utility',(512,256),[0,ysplit,xsplit,im.height-ysplit])]
 for aid,name,folder,size,rect in specs:
  x,y,w,h=rect;crop=im.crop((x,y,x+w,y+h));sm=metrics(crop)
  if max(sm['edgeMaxAlphaLTRB'])>=T:raise ValueError('Visible utility subject crosses ownership border')
  out,tr,m=fit(crop,size,32);entries.append(save_derived(out,G/f'assets/{folder}/{aid}.png',aid,name,'static_effect' if folder=='effects' else 'utility',native,gen,rect,tr,sm))
 empty=a[ysplit:,xsplit:]
 if (empty>=T).any():raise ValueError('Unexpected fourth utility object')
 sources.append({'file':native.relative_to(G).as_posix(),'sha256':digest,'unchangedAfterExport':sha(native)==digest,'nominalEqualQuartersUsed':False,'ownershipSplitXY':[xsplit,ysplit],'emptyOwnershipRect':[xsplit,ysplit,im.width-xsplit,im.height-ysplit],'emptyVisibleAlpha16Pixels':int((empty>=T).sum()),'emptyMaxAlpha':int(empty.max()),'seamMaxAlpha':int(max(a[:,xsplit-1:xsplit+1].max(),a[ysplit-1:ysplit+1,:].max()))})
 shadow=next(e for e in entries if e['id']=='soft_shadow')
 warnings.append({'id':'shadow_opacity_target','file':shadow['file'],'value':shadow['alphaRange'][1],'requestedApproxMaxAlpha':round(.35*255),'blocking':False,'meaning':'Retained original generated translucent shadow; approximately52percent source opacity vs35percent prompt target. Runtime tint alpha is a future suggestion, not a validated Unity result.'})
 # These two are explicitly authorized technical data/basic geometry, not painted art.
 generator=Path(__file__);generator_hash=sha(generator)
 rng=np.random.Generator(np.random.PCG64(SEED));arr=rng.integers(0,256,size=(256,256),dtype=np.uint8);noise=Image.fromarray(arr,mode='L');npth=G/'assets/technical/env_repeat_noise.png';npth.parent.mkdir(parents=True,exist_ok=True);noise.save(npth)
 technical=[]
 nr={'id':'env_repeat_noise','name':'确定性灰度噪声数据','file':npth.relative_to(G).as_posix(),'sha256':sha(npth),'size':[256,256],'mode':'L','alpha':False,'category':'technical_data_not_handpainted_art','source':'Explicitly authorized deterministic technical data generation','newAIGeneration':False,'nativePaintingClaimed':False,'algorithm':{'library':'numpy','version':np.__version__,'generator':'Generator(PCG64)','seed':SEED,'call':'integers(low=0, high=256, size=(256,256), dtype=uint8)','rangeInclusive':[0,255]},'sourceScript':generator.relative_to(G).as_posix(),'sourceScriptSha256':generator_hash,'purpose':'Source infinite-background shader noise texture slot; contains random scalar data rather than level art','unityImportSuggestions':{'textureType':'Default','sRGB':False,'wrapMode':'Repeat','filterMode':'Bilinear','maxSize':256,'compression':'None for initial verification','mipmaps':'Review with shader scale and platform; not Unity-verified'},'unityVerified':False}
 write(Path(str(npth)+'.derived.json'),nr);technical.append(nr)
 white=Image.new('RGBA',(4,4),(255,255,255,255));wp=G/'assets/utility/flash_white.png';wp.parent.mkdir(parents=True,exist_ok=True);white.save(wp)
 wr={'id':'flash_white','name':'全屏白闪基础色块','file':wp.relative_to(G).as_posix(),'sha256':sha(wp),'size':[4,4],'mode':'RGBA','alphaRange':[255,255],'category':'basic_geometry_not_handpainted_art','source':'Explicitly authorized opaque-white primitive','newAIGeneration':False,'nativePaintingClaimed':False,'algorithm':'Pillow Image.new RGBA4x4 with every pixel(255,255,255,255)','sourceScript':generator.relative_to(G).as_posix(),'sourceScriptSha256':generator_hash,'pivot':[.5,.5],'borderLeftBottomRightTop':[0,0,0,0],'purpose':'Source full-screen white flash sprite; opacity/fade controlled by future Unity integration','unityImportSuggestions':{'textureType':'Sprite(2D and UI)','spriteMode':'Single','meshType':'Full Rect','imageType':'Simple','compression':'None','mipmap':False},'unityVerified':False}
 write(Path(str(wp)+'.derived.json'),wr);technical.append(wr)
 all_entries=entries+technical
 board=Image.new('RGBA',(1400,90+5*345),'#eae2ce');d=ImageDraw.Draw(board);f=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n);d.text((25,18),'新增静态美术 · 浅米 / 深玉（技术数据另列）',font=f(29),fill='#164337')
 for i,e in enumerate(entries):
  col=i%2;row=i//2;x=col*700;y=85+row*345;d=ImageDraw.Draw(board);d.text((x+18,y),e['name']+' · '+e['purpose'],font=f(22),fill='#164337')
  for k,bg in enumerate(['#fff3da','#123b33']):
   q=Image.open(G/e['file']).convert('RGBA');q.thumbnail((290,280),Image.Resampling.LANCZOS);bx=x+20+k*330;by=y+42;board.paste(Image.new('RGBA',(310,290),bg),(bx,by));board.alpha_composite(q,(bx+(310-q.width)//2,by+(290-q.height)//2))
 preview=G/'previews/new-statics-light-dark.jpg';preview.parent.mkdir(exist_ok=True);board.convert('RGB').save(preview,quality=97)
 report={'schemaVersion':1,'exportedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'G new9 static art derivatives plus2 explicitly authorized technical resources. Existing O/oldUI untouched.','runtimeFileCount':len(all_entries),'newStaticArtPNGCount':len(entries),'technicalPNGCount':len(technical),'newAIGenerationCalls':0,'noAnimationCreated':True,'assets':entries,'technicalAssets':technical,'sourceFiles':sources,'warnings':warnings,'errors':[],'technicalPassed':True,'visualReview':{'status':'pending actual final light/dark contact inspection'},'preview':preview.relative_to(G).as_posix(),'unityVerified':False}
 write(G/'records/new-static-exports.json',report)
 print(json.dumps({'runtimeFileCount':len(all_entries),'artPNG':len(entries),'technicalPNG':len(technical),'technicalPassed':True,'warnings':len(warnings),'preview':str(preview)},ensure_ascii=False))

if __name__=='__main__':main()
