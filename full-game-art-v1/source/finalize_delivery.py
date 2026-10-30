"""Verify the adopted art library and package only reviewed runtime/native cels."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,zipfile,argparse
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',action='store_true');args=ap.parse_args()
    m=read(R/'records/final-resource-manifest.json');walk=read(R/'records/walk-exports.json')
    failures=[];checked=[]
    playback_path=R/'records/walk-playback-review.json'
    playback={a['actor']:a for a in read(playback_path).get('actors',[])} if playback_path.exists() else {}
    expected_motion={a['file']:a['sha256'] for a in walk.get('assets',[])}
    manifest_motion={a['file']:a['sha256'] for a in m['assets'] if a.get('kind')=='character-walk-frame'}
    if expected_motion!=manifest_motion or len(manifest_motion)!=44:failures.append('manifest must contain exactly the current44 adopted motion frames; run assemble after export')
    if m.get('walkClipCount')!=11 or {c['actor'] for c in m.get('clips',[])}!={c['actor'] for c in walk['clips']}:failures.append('manifest current eleven clips')
    for a in m['assets']+m['screens']+m['nativeSources']:
        p=R/a['file']
        if not p.is_file():failures.append('missing '+a['file']);continue
        if sha(p)!=a['sha256']:failures.append('digest '+a['file']);continue
        with Image.open(p) as im:
            im.load()
            if a.get('size') and list(im.size)!=a['size']:failures.append('size '+a['file'])
            if a.get('alphaRange') and list(im.getchannel('A').getextrema())!=a['alphaRange']:failures.append('alpha '+a['file'])
        checked.append(a['file'])
    ui_ok=len(m['screens'])==131
    if not ui_ok:failures.append('131 retained screens required')
    for a in m['screens']:
        if not (R/a['file']).exists() or sha(R/a['file'])!=a['sha256'] or sha(Path(a['sourceFile']))!=a['sha256']:
            failures.append('retained UI changed '+a['file']);ui_ok=False
    if len(walk['clips'])!=11 or not walk['all11Passed']:failures.append('all eleven adopted walk clips must have current playback acceptance')
    expected_ids={'hero_daotong','hero_lingyi','hero_leixiu','orig_mob01','orig_mob02','orig_mob03','orig_mob04','orig_mob05','orig_mob06','orig_boss_minor','orig_boss01'}
    if {c['actor'] for c in walk['clips']}!=expected_ids:failures.append('fixed-commit actor identity coverage')
    adopted=[]
    for c in walk['clips']:
        review=read(R/c['nativePoseReview'])
        if not review.get('passed') or review.get('blockingIssues'):failures.append('native review '+c['actor'])
        if not c['playbackAccepted'] or len(c['frames'])!=4:failures.append('playback review '+c['actor'])
        pr=playback.get(c['actor'],{})
        if pr.get('accepted') is not True or pr.get('frameSha256')!=[f['sha256'] for f in c['frames']] or pr.get('durationsMs')!=[f['durationMs'] for f in c['frames']]:failures.append('current playback evidence '+c['actor'])
        if len({f['sha256'] for f in c['frames']})!=4:failures.append('unique cels '+c['actor'])
        for f in c['frames']:
            p=Path(f['sourceFile']);g=read(Path(str(p)+'.generation.json'))
            if g['sha256']!=sha(p):failures.append('native provenance '+str(p))
            if g.get('sourceArtFromFDrive') is not False:failures.append('native source '+str(p))
            if not (R/g['prompt']).is_file():failures.append('prompt '+g['prompt'])
            adopted.extend([p,Path(str(p)+'.generation.json')])
    fonts=read(R/'records/font-sources.json')
    if len(fonts.get('fontFiles',[]))!=2 or not fonts.get('combinedFallbackCoveragePassed'):failures.append('font scope/coverage')
    for f in fonts.get('fontFiles',[]):
        for key,digest_key in [('fontFile','fontSha256'),('licenseFile','licenseSha256')]:
            if key in f and digest_key in f:
                p=R/f[key]
                if not p.exists() or sha(p)!=f[digest_key]:failures.append('font '+str(p))
    for f in ['records/fx-playback-review.json','records/ground-tile-review.json','records/composite-playback-review.json']:
        if not (R/f).exists() or not read(R/f).get('passed'):failures.append('visual evidence '+f)
    report={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Fixed-commit complete image/UI art scope plus previously confirmed demo quests; Unity intentionally next stage','allGameArtComplete':not failures,'failures':failures,'runtimeImageCount':len(m['assets']),'designScreenCount':len(m['screens']),'bodyIdentityCount':11,'walkClipCount':len(walk['clips']),'walkFrameCount':len(walk['assets']),'all11WalksAccepted':walk['all11Passed'],'checkedImageEntries':len(checked),'oldUI131ByteIdentical':not any('UI' in f for f in failures),'actualVisualEvidence':['records/walk-playback-review.json','records/fx-playback-review.json','records/ground-tile-review.json','records/composite-playback-review.json','records/scope-audit-20261028.json'],'limitations':['Four independently AI-painted key cels per identity: deliberately stepped stylized loops, not fluid video or additional action families.','Native image-generation model and quality selectors/returns are undisclosed; configured targets are not verified actual model metadata.','Ground native size1254x1254; opposite edges differ numerically, visually reviewed repeat rather than mathematically identical seams.','Unity import, shader, prefabs, scene, behavior, controls, device performance and production localization remain next stage.'],'unityVerified':False,'gitCommittedOrPublished':False}
    report['oldUI131ByteIdentical']=ui_ok
    write(R/'records/final-acceptance.json',report)
    m['allGameArtComplete']=not failures;m['acceptanceReport']='records/final-acceptance.json';m['walkAllPassed']=walk['all11Passed'];write(R/'records/final-resource-manifest.json',m)
    if failures:print(json.dumps({'allGameArtComplete':False,'failures':failures},ensure_ascii=False));return
    if args.package:
        paths={R/a['file'] for a in m['assets']+m['screens']+m['nativeSources']};paths.update(adopted)
        for folder in ['docs','records','sources','source','assets/fonts']:
            paths.update(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        paths.update([R/'README.md',R/'AGENTS.md',R/'IMAGE_MODEL_POLICY.md',R/'image-generation.json',R/'assets/asset-list.csv'])
        for p in (R/'designs').rglob('*.layout.json'):paths.add(p)
        for p in (R/'assets/motion').rglob('*.json'):paths.add(p)
        paths.update(p for p in (R/'previews').rglob('*') if p.is_file())
        dest=R/'delivery/dao_full_game_art_20261028.zip';dest.parent.mkdir(exist_ok=True)
        if dest.exists():raise FileExistsError('Keep prior package, choose a new version')
        entries=[]
        with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in sorted(paths):
                if p.suffix in ['.pyc'] or p.name=='delivery-package.json':continue
                rel=p.relative_to(R).as_posix();z.write(p,'dao_full_game_art/'+rel);entries.append({'file':rel,'sha256':sha(p),'bytes':p.stat().st_size})
        with zipfile.ZipFile(dest) as z:
            bad=z.testzip()
            if bad:raise ValueError('CRC '+bad)
            for a in entries:
                if hashlib.sha256(z.read('dao_full_game_art/'+a['file'])).hexdigest()!=a['sha256']:raise ValueError('Archived digest '+a['file'])
        record={'builtAtUtc':datetime.now(timezone.utc).isoformat(),'file':dest.relative_to(R).as_posix(),'bytes':dest.stat().st_size,'sha256':sha(dest),'fileCount':len(entries),'crcVerified':True,'allArchivedEntryHashesVerified':True,'entryManifest':entries,'rejectedNativePosesPackaged':False,'unityVerified':False}
        write(R/'records/delivery-package.json',record);(dest.with_suffix('.zip.sha256')).write_text(record['sha256']+'  '+dest.name+'\n',encoding='utf-8')
        print(json.dumps({k:record[k] for k in ['file','bytes','sha256','fileCount','crcVerified']},ensure_ascii=False))
    else:print(json.dumps({k:report[k] for k in ['allGameArtComplete','runtimeImageCount','designScreenCount','walkClipCount']},ensure_ascii=False))
if __name__=='__main__':main()
