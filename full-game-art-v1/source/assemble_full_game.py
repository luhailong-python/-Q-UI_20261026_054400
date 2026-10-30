"""Assemble a reviewable art library. Never edit existing UI or upstream files."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,shutil,csv
R=Path(__file__).resolve().parents[1]
P=R.parent;O=P/'original-monsters-v1';A=O/'ability-expansion-v1';V=O/'combat-fx-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def cp(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists() or sha(src)!=sha(dest):shutil.copyfile(src,dest)
 if sha(src)!=sha(dest):raise ValueError('Copy digest mismatch')
def norm(base,record,group,assets,mapping):
 src=base/record['file'];rel=Path(record['file']);tail=Path(*rel.parts[1:]) if rel.parts[0]=='assets' else rel
 dest=R/'assets/final'/group/tail;cp(src,dest)
 im=Image.open(dest);im.load();pivot=record.get('pivot',[.5,.5]);border=record.get('borderLeftBottomRightTop',[0,0,0,0])
 out={'id':group+'__'+record.get('id',record.get('iconId',src.stem)),'name':record.get('name',record.get('originalChineseName',src.stem)),'file':dest.relative_to(R).as_posix(),'kind':group,'size':list(im.size),'mode':im.mode,'alphaRange':list(im.getchannel('A').getextrema()) if 'A'in im.getbands() else None,'pivot':pivot,'borderLeftBottomRightTop':border,'imageType':record.get('imageType','Simple'),'sha256':sha(dest),'sourceFile':str(src),'sourceSha256':sha(src),'operation':'Byte-identical copy; no art/pixel changes','unityVerified':False}
 if 'enemy_lob_orb_pending' in str(src):out.update({'functionalBinding':'GravityThrowable confirmed by fixed-commit prefab/meta; body plus separate gravity-well effect','status':'art-ready-binding-pending','name':'敌方引力投掷本体'})
 else:out['status']='art-reviewed' if group!='preserved-ui' else 'preserved-user-approved-ui'
 for key in ['state','purpose','monsterId','function','durationMs','sourceAnchorXY','outputAnchorTopLeftXY','sharedUniformScale','uniformScale','dynamicTextInArt','fixedDecorativeMarks']:
  if key in record:out[key]=record[key]
 assets.append(out);mapping[str(src)]=out['file']
 side=Path(str(src)+'.derived.json')
 if side.exists():cp(side,R/'records/provenance'/group/(str(tail)+'.derived.json'))
 return out
def main():
 assets=[];mapping={};screens=[];evidence=[]
 old=read(P/'assets/manifest.json');layouts=read(P/'records/screen-layouts.json');refs={a['asset'] for s in layouts['screens'] for a in s['assets']}
 for rec in old['assets']:
  if not rec['file'].startswith('assets/monsters/') or rec['file'] in refs:norm(P,rec,'preserved-ui',assets,mapping)
 for base,group in [(O,'original-base'),(A,'abilities'),(V,'combat')]:
  m=read(base/'assets/manifest.json')
  for rec in m['assets']:norm(base,rec,group,assets,mapping)
  cp(base/'assets/manifest.json',R/f'records/provenance/{group}/original-manifest.json')
 for group,base,items in [('preserved',P,layouts['screens']),('functional',O,read(O/'assets/manifest.json')['screens'])]:
  for s in items:
   src=base/s['file'];tail=Path(*Path(s['file']).parts[1:]);dest=R/'designs'/group/tail;cp(src,dest)
   screens.append({'file':dest.relative_to(R).as_posix(),'sourceFile':str(src),'sha256':sha(dest),'orientation':s.get('orientation'),'state':s.get('state'),'existingPixelsChanged':False})
   side=src.with_suffix('.layout.json')
   if side.exists():cp(side,dest.with_suffix('.layout.json'))
 cp(P/'records/screen-layouts.json',R/'records/provenance/preserved-ui/original-screen-layouts.json')
 n=read(R/'records/new-static-exports.json')
 for rec in n['assets']+n['technicalAssets']:
  p=R/rec['file'];im=Image.open(p);im.load();q={**rec,'kind':'new-static' if rec in n['assets'] else 'technical-data','size':list(im.size),'mode':im.mode,'sha256':sha(p),'status':'art-reviewed' if rec in n['assets'] else 'technical-source-documented','unityVerified':False};assets.append(q)
 ground=R/'assets/native/env_battle_ground_01.png'
 if ground.exists():
  dest=R/'assets/environment/env_battle_ground_01.png';cp(ground,dest);im=Image.open(dest)
  assets.append({'id':'env_battle_ground_01','name':'连续战斗地面','file':dest.relative_to(R).as_posix(),'kind':'environment','size':list(im.size),'mode':im.mode,'sha256':sha(dest),'wrap':'Repeat U/V','sprite':False,'sourceFile':str(ground),'operation':'Byte-identical native original; no upscale','status':'visual-tiling-reviewed','review':'records/ground-tile-review.json','unityVerified':False})
 walk=R/'records/walk-exports.json';walkdoc=read(walk) if walk.exists() else {'clips':[],'assets':[],'all11Passed':False}
 assets.extend(walkdoc.get('assets',[]))
 for base,group,paths in [(O,'original-base',read(O/'assets/manifest.json')['nativeOriginalArt']), (A,'abilities',[{'file':f'assets/native/ability_pack_{n}.png'} for n in 'abc']+[{'file':'assets/native/existing_abilities_atlas.png'}]),(V,'combat',[{'file':f'assets/native/{n}.png'} for n in ['projectiles_a','projectiles_b','weapons','particles','pickups','fx_explosion','fx_firefield']])]:
  for rec in paths:
   src=base/rec['file'];dest=R/'sources'/group/rec['file'];cp(src,dest)
   side=Path(str(src)+'.generation.json')
   if side.exists():cp(side,Path(str(dest)+'.generation.json'))
   evidence.append({'file':dest.relative_to(R).as_posix(),'sourceFile':str(src),'sha256':sha(dest),'purpose':'Native original/source atlas provenance; not an extra runtime asset'})
 for src in R.glob('assets/native/*.png'):
  evidence.append({'file':src.relative_to(R).as_posix(),'sha256':sha(src),'purpose':'Current final-stage native source'})
 fonts=read(R/'records/font-sources.json') if (R/'records/font-sources.json').exists() else None
 data={'schemaVersion':1,'assembledAtUtc':datetime.now(timezone.utc).isoformat(),'referenceRepository':'https://github.com/matthiasbroske/VampireSurvivorsClone','referenceCommit':'01f8c76e40f52b853117f436d6d3d08f80a41506','formalProjectRemote':'not provided','sourceUse':'function only, no upstream/F-drive images newly read or copied','existingUIPolicy':'131 previews and their current needed controls preserved by byte; new body/object/motion art original','runtimeImageCount':len(assets),'designScreenCount':len(screens),'preservedUIDesignCount':109,'functionalUIDesignCount':22,'configuredActorCount':11,'requiredWalkClipCount':11,'walkClipCount':len(walkdoc.get('clips',[])),'walkAllPassed':walkdoc.get('all11Passed',False),'assets':assets,'screens':screens,'sourceToFinalResourceMap':mapping,'nativeSources':evidence,'clips':walkdoc.get('clips',[]),'fxPlaybackReview':'records/fx-playback-review.json','fontSourceRecord':'records/font-sources.json' if fonts else None,'unityVerified':False,'allGameArtComplete':False,'completionRule':'Requires all11 walk clips accepted, environment/utility and44 combat images reviewed,131 UI preserved, source/alpha/dimensions/packaging verified. Unity integration intentionally next stage.'}
 write(R/'records/final-resource-manifest.json',data)
 with (R/'assets/asset-list.csv').open('w',encoding='utf-8-sig',newline='') as f:
  fields=['id','name','file','kind','size','mode','pivot','borderLeftBottomRightTop','sha256','status'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(assets)
 print(json.dumps({'runtimeImages':len(assets),'screens':len(screens),'walkClips':len(walkdoc.get('clips',[])),'nativeSources':len(evidence)},ensure_ascii=False))
if __name__=='__main__':main()
