from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[2]
O=R.parent/'original-monsters-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
data={
 'orig_mob03':{
  'files':['orig_mob03_walk_00_v3.png','orig_mob03_walk_01.png','orig_mob03_walk_02.png','orig_mob03_walk_03.png'],
  'anchors':[[730,695],[680,650],[585,670],[680,660]],
  'kind':'hover-walk',
  'observations':['Left sway extreme; two separate complete side ribbons and three tassels curve left. v3 uses original identity master plus same-project phase1 rigid-shell framing support.','Left trailing tassel fibers with near-vertical chains and downward side ribbons; genuine passing intermediate.','Right sway extreme; three tassel chains pivot right and both side ribbons bend right.','Opposite passing intermediate: chains near vertical, fiber tails curl right, left ribbon rises into arc.'],
  'excluded':['orig_mob03_walk_00.png','orig_mob03_walk_00_v2.png'],
  'notes':['No legs or hands added; hanging lantern is intentionally not a biped.','First pose v3 preserves complete ribbons; original0 larger shell/fork-like folded ribbon discarded, v2 right ribbon incomplete discarded.','Selected phase0v3 was AI repaired with original master plus same-project phase1 shell/framing support, both actual references recorded.','Native framing shifts remain; anchors identify rigid paper-shell center rather than tassel or full alpha-bbox bottom.','Native phase0v3 has tight complete ribbon-tip margins; final common downscale must leave clear output safety margin.']},
 'orig_mob04':{
  'files':['orig_mob04_walk_00.png','orig_mob04_walk_01.png','orig_mob04_walk_02_v2.png','orig_mob04_walk_03.png'],
  'anchors':[[625,1170],[620,1140],[610,1172],[610,1147]],
  'kind':'walk',
  'observations':['Screen-right boot low/planted forward, screen-left rear boot trails; contact step.','Screen-right boot supports underneath; screen-left boot bent up behind, narrower passing stance.','Selected v2: SCREEN-LEFT large foreground boot planted lowest, SCREEN-RIGHT far boot smaller and lifted rear. Explicitly opposite contact geometry from phase0.','SCREEN-LEFT boot supports, SCREEN-RIGHT knee lifted forward and tipped boot sole visible. Opposite support/passing geometry from phase1.'],
  'excluded':['orig_mob04_walk_02.png'],
  'notes':['This bamboo goblin has two actual legs in master and uses walk, not hover.','Wicker shield stays viewer-left, leafy bamboo staff stays viewer-right across all selected poses; hands remain attached.','Phase02 initial attempt repeats right-foot contact and is excluded; targeted v2 successfully reverses planted foot.','All four selected frames show actual knee/foot articulation and cloth changes. No translated or scaled still invents another pose.','One common body scale and physical sole plane are required; head/camera microvariation must still be checked during playback.']}
}
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for actor,v in data.items():
 files=[R/'assets/motion-native'/actor/x for x in v['files']]
 master=O/f'assets/runtime/{actor}_runtime_E.png'
 anchors=[]
 for i,xy in enumerate(v['anchors']):
  anchors.append({'phase':i,'sourceAnchorXY':xy,'definition':'Manually observed rigid paper-shell center excluding ornaments' if v['kind']=='hover-walk' else 'Manually observed torso axis and planted wooden sole plane; not alpha-bbox bottom','supportNote':v['observations'][i],'approximatePixelTolerance':12})
 rec={'actor':actor,'master':str(master),'masterSha256':sha(master),'selectedFiles':[p.relative_to(R).as_posix() for p in files],'selectedFileSha256':[sha(p) for p in files],'anchors':anchors,'animationKind':v['kind'],'passed':True,'passedMeaning':'Native identity, complete anatomy and genuinely distinct articulated poses only. NOT registered playback, loop seam, body-scale stability or Unity acceptance.','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'actuallyViewedNativeFiles':[p.relative_to(R).as_posix() for p in files],'masterActuallyViewedBeforeEdits':True,'blockingIssues':[],'findings':v['notes'],'phaseObservations':v['observations'],'excludedFiles':['assets/motion-native/'+actor+'/'+n for n in v['excluded']],'remainingReview':['Final common-scale physical registration, actual normal/slow playback, seam continuity and visible size pop','True light/dark composites and game-size silhouette review','Unity import remains next phase, unverified'],'sourceRoute':'builtin image_gen individual pose edits; original master always attached; not I2V','unityVerified':False,'bodyFramesRegistered':False,'newImagesGeneratedInReview':False}
 (R/f'records/motion/{actor}-native-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 board=Image.new('RGBA',(1600,840),'#f2e5ca');d=ImageDraw.Draw(board)
 d.text((16,8),actor+' native poses / one common preview scale 0.25, physical anchor translation',font=font,fill='#153b32')
 for i,(p,xy) in enumerate(zip(files,v['anchors'])):
  art=Image.open(p).convert('RGBA').convert('RGBa').resize((314,314),Image.Resampling.LANCZOS).convert('RGBA')
  target=[200,220 if v['kind']=='hover-walk' else 350]
  off=[round(target[0]-xy[0]*.25),round(target[1]-xy[1]*.25)]
  for j,bg in enumerate(['#fff3da','#123b33']):
   q=Image.new('RGBA',(400,400),bg);q.alpha_composite(art,off);board.alpha_composite(q,(400*i,40+400*j))
  d.text((400*i+8,45),str(i)+' '+p.stem[-12:],font=font,fill='#174238')
 board.convert('RGB').save(R/f'previews/hover-walks-review/{actor}-native-contact.jpg',quality=96)
 print(actor+' native review and fixed-scale review contact saved')
