"""Register independently AI-painted cels; no still is used to invent extra poses."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];P=R.parent;O=P/'original-monsters-v1'
IDS=['hero_daotong','hero_lingyi','hero_leixiu','orig_mob01','orig_mob02','orig_mob03','orig_mob04','orig_mob05','orig_mob06','orig_boss_minor','orig_boss01']
NAMES=['青云道童','清荷灵医','玄霆道人','青符灵','苔玉小魁','灯芯小魅','竹甲小妖','桃木小傀','玄甲山魈','铜铃卫','玄坛石尊']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def bbox(im):return im.getchannel('A').point(lambda v:255 if v>=16 else 0).getbbox()
def master_runtime(actor):
 if actor.startswith('hero'):return O/f'assets/heroes/{actor}.png'
 if actor in ['orig_mob05','orig_mob06']:return R/f'assets/actors/{actor}.png'
 return O/f'assets/runtime/{actor}_runtime_E.png'
def source_anchor(a):
 if 'sourceAnchorXY'in a:return a['sourceAnchorXY']
 return [a['sourceTorsoX'],a['sourceGroundY']]
def main():
 clips=[];assets=[];pending=[]
 playback_file=R/'records/walk-playback-review.json'
 playback={v['actor']:v for v in read(playback_file).get('actors',[])} if playback_file.exists() else {}
 calibration_file=R/'records/motion-head-calibration.json'
 calibrations={v['actor']:v for v in read(calibration_file)['actors']} if calibration_file.exists() else {}
 for actor,name in zip(IDS,NAMES):
  rp=R/f'records/motion/{actor}-native-review.json'
  if not rp.exists():pending.append({'actor':actor,'reason':'native-review not delivered'});continue
  review=read(rp)
  if not review.get('passed') or review.get('blockingIssues'):pending.append({'actor':actor,'reason':'native review has unresolved issues','issues':review.get('blockingIssues',[])});continue
  files=[R/v for v in review['selectedFiles']];anchors=[source_anchor(a) for a in review['anchors']]
  if len(files)!=4 or len(anchors)!=4 or len(set(sha(p) for p in files))!=4:raise ValueError('Four actual unique painted poses required '+actor)
  images=[Image.open(p).convert('RGBA') for p in files];boxes=[bbox(im) for im in images]
  cal=calibrations.get(actor)
  factors=[v['relativeHeadScale'] for v in cal['records']] if cal and cal.get('approvedByVisualReview') is True and cal.get('selectedFiles')==review['selectedFiles'] else [1.0]*4
  static=Image.open(master_runtime(actor)).convert('RGBA');sb=bbox(static);height=sb[3]-sb[1]
  hover=review.get('animationKind')=='hover-walk'
  if hover:
   # The hanging body's registration anchor is manually identified, not tassel bottom.
   target=[512,round((sb[1]+sb[3])/2)];scale=min(1,height/(boxes[0][3]-boxes[0][1]))
  else:
   target=[512,896];refheight=anchors[0][1]-boxes[0][1]
   if refheight<=0:raise ValueError('Invalid physical ground anchor '+actor)
   scale=min(1,height/refheight)
  for b,a,factor in zip(boxes,anchors,factors):
   scale=min(scale,1/factor)
   for d,avail in [(a[0]-b[0],target[0]-32),(b[2]-a[0],1024-32-target[0]),(a[1]-b[1],target[1]-32),(b[3]-a[1],1024-32-target[1])]:
    if d>0:scale=min(scale,avail/(d*factor))
  scale*=.995
  frames=[];outframes=[];group=R/f'assets/motion/{actor}/walk';group.mkdir(parents=True,exist_ok=True)
  # Fixed-commit timing reference, adjustable during later Unity integration.
  tick=100 if actor.startswith('hero') else (150 if actor in ['orig_mob03','orig_mob04'] else 200)
  durations=review.get('durationsMs',[tick]*4)
  for i,(src,im,a,duration,factor) in enumerate(zip(files,images,anchors,durations,factors)):
   native=read(Path(str(src)+'.generation.json'))
   if native['sha256']!=sha(src):raise ValueError('Native pose provenance mismatch')
   effective_scale=scale*factor
   w,h=im.size;size=[max(1,round(w*effective_scale)),max(1,round(h*effective_scale))]
   art=im.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA');offset=[round(target[0]-a[0]*size[0]/w),round(target[1]-a[1]*size[1]/h)]
   out=Image.new('RGBA',(1024,1024));out.alpha_composite(art,offset);b=bbox(out);m=[b[0],b[1],1024-b[2],1024-b[3]]
   aa=np.array(art.getchannel('A'));yy,xx=np.indices(aa.shape);lost=aa[(xx+offset[0]<0)|(xx+offset[0]>=1024)|(yy+offset[1]<0)|(yy+offset[1]>=1024)]
   if min(m)<31 or (lost.size and lost.max()>=16):raise ValueError('Visible pose clipped/padding '+actor)
   dest=group/f'{actor}_walk_{i:02d}.png';out.save(dest);outframes.append(out)
   rec={'id':f'{actor}_walk_{i:02d}','name':name+f' 行走{i+1}','file':dest.relative_to(R).as_posix(),'kind':'character-walk-frame','actor':actor,'action':'walk','phase':i,'size':[1024,1024],'mode':'RGBA','alphaRange':list(out.getchannel('A').getextrema()),'pivot':[target[0]/1024,1-target[1]/1024],'sourceFile':str(src),'sourceSha256':sha(src),'sha256':sha(dest),'sourceAnchorXY':a,'outputAnchorTopLeftXY':target,'sharedUniformScale':scale,'actualRasterScaleXY':[size[0]/w,size[1]/h],'offsetTopLeft':offset,'visibleMarginsLTRB':m,'durationMs':duration,'borderLeftBottomRightTop':[0,0,0,0],'operation':'One distinct AI-painted pose, fixed shared downscale and physical anchor translation; no generated in-between or per-frame size normalization','perFrameBBoxScaling':False,'nativeDetailIncreased':False,'status':'playback-review-pending','nativeReview':rp.relative_to(R).as_posix(),'unityVerified':False}
   rec['cameraCalibrationFactor']=factor;rec['actualUniformScale']=effective_scale;rec['cameraCalibrationMethod']='None adopted; NCC candidates are analysis-only pending actual visual approval';rec['operation']='Distinct AI-painted pose, one common body scale and physical root registration; all resampling is downscale'
   write(Path(str(dest)+'.derived.json'),rec);assets.append(rec);frames.append({'file':rec['file'],'sha256':rec['sha256'],'durationMs':duration,'sourceFile':str(src),'sourceAnchorXY':a,'cameraCalibrationFactor':factor,'actualUniformScale':effective_scale})
  clip={'id':actor+'_walk','actor':actor,'name':name,'action':'walk','animationKind':review.get('animationKind','walk'),'frames':frames,'size':[1024,1024],'pivot':[target[0]/1024,1-target[1]/1024],'outputAnchorTopLeftXY':target,'sharedUniformScale':scale,'scaleReferencePhase':0,'staticReference':str(master_runtime(actor)),'referenceStaticHeightAlpha16':height,'loop':True,'durationMs':sum(durations),'artSource':'builtin image_gen individual pose edits from one original master; not I2V','nativePoseReview':rp.relative_to(R).as_posix(),'playbackAccepted':False,'unityVerified':False}
  clip['cameraCalibrationFactors']=factors;clip['oneCommonScale']=len(set(factors))==1;clip['cameraCalibrationEvidence']='records/motion-head-calibration.json';clip['registrationDisclosure']='One common scale from reference pose and physical root registration. Unapproved automated head-fit proposals are not applied. Actual source-to-output scales are recorded; no per-frame leg/bbox-size normalization.'
  accepted=playback.get(actor,{})
  current_hashes=[f['sha256'] for f in frames]
  clip['playbackAccepted']=accepted.get('accepted') is True and accepted.get('frameSha256')==current_hashes and accepted.get('durationsMs')==durations
  if clip['playbackAccepted']:
   clip['playbackReview']='records/walk-playback-review.json'
   for rec in assets[-4:]:
    rec['status']='art-and-playback-reviewed'
    write(Path(str(R/rec['file'])+'.derived.json'),rec)
  write(group/'clip.json',clip);clips.append(clip)
  outdir=R/f'previews/walk/{actor}';outdir.mkdir(parents=True,exist_ok=True)
  for bg,label in [('#fff3da','light'),('#123b33','dark')]:
   seq=[]
   for f in outframes:
    f=f.convert('RGBa').resize((384,384),Image.Resampling.LANCZOS).convert('RGBA');q=Image.new('RGBA',(384,384),bg);q.alpha_composite(f);seq.append(q)
   seq[0].save(outdir/f'{actor}-{label}.png',save_all=True,append_images=seq[1:],duration=durations,loop=0,disposal=0,blend=0)
  board=Image.new('RGBA',(1536,850),'#f2e5ca');d=ImageDraw.Draw(board);d.text((18,12),name+' · 四个独立原画姿势 / 固定共同尺度',font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28),fill='#164437')
  for i,f in enumerate(outframes):
   small=f.convert('RGBa').resize((384,384),Image.Resampling.LANCZOS).convert('RGBA')
   for j,bg in enumerate(['#fff3da','#123b33']):
    board.paste(Image.new('RGBA',(384,384),bg),(i*384,70+j*384));board.alpha_composite(small,(i*384,70+j*384))
  board.convert('RGB').save(outdir/'contact.jpg',quality=95)
 write(R/'records/walk-exports.json',{'exportedAtUtc':datetime.now(timezone.utc).isoformat(),'requiredIdentities':IDS,'requiredCount':11,'exportedCount':len(clips),'all11Passed':len(clips)==11 and all(c['playbackAccepted'] for c in clips),'clips':clips,'assets':assets,'pending':pending,'policy':'Individual painted poses and physical registration; exported does not equal playback-approved'})
 print(json.dumps({'exportedWalkClips':len(clips),'frames':len(assets),'pending':len(pending)},ensure_ascii=False))
if __name__=='__main__':main()
