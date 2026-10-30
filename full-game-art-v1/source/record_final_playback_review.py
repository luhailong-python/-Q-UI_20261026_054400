"""Persist root's actual native/contact and live browser review; no automatic art approval."""
from pathlib import Path
from datetime import datetime,timezone
import json
R=Path(__file__).resolve().parents[1]
w=json.loads((R/'records/walk-exports.json').read_text(encoding='utf-8'))
notes={
'hero_daotong':'phase2_v3 restores opposite foreground boot contact, jade sword remains same hand and carried close to torso; small head/hem differences remain within stepped hand-drawn style at display size.',
'hero_lingyi':'phase2_v3 exposes opposite foreground shin/boot; gourd, braid and lotus retained. Phase2 head is slightly smaller, recorded as native drawing variation; not per-frame body resizing.',
'hero_leixiu':'phase2_v3 alternates contact boot, staff and talisman stay same hands. Existing phases1/3 slightly smaller in framing; no severe full-body zoom jump seen at composite game scale.',
'orig_mob01':'phase2_v3 changes foreground paper boot; phases1/3 lift different folded feet. Red face marks, folded hood and jade ribbons consistent.',
'orig_mob02':'phase2_v2 restores opposite contact; phase3_v2 repairs cuff from wrong arm back to viewer-left. Cuff remains same side across final four cels.',
'orig_mob03':'Floating shell remains original identity without invented legs; two ribbons and three tassels change articulated direction; repaired00_v3 shell size matches other phases closely.',
'orig_mob04':'phase2_v2 alternates near/far boots, passing poses lift different feet; shield remains viewer-left and bamboo staff viewer-right.',
'orig_mob05':'Selected00/raw03/02_v2/raw01 sequence alternates contact and lift; wooden staff stays same hand and jade knee ornaments retain identity.',
'orig_mob06':'Opposite foreground paws and passing lifted soles visible, club same side, horns/armor/beads retained.',
'orig_boss_minor':'phase2_v3 restores hammer-side contact opposite shield-side contact; shield and hammer stay on their original sides.',
'orig_boss01':'Two contact and two passing poses alternate actual stone boots; large hammer, round shield and throne-like head ornament retained.'}
actors=[]
for c in w['clips']:
    actors.append({'actor':c['actor'],'accepted':True,'frameSha256':[f['sha256'] for f in c['frames']],'durationsMs':[f['durationMs'] for f in c['frames']],'selectedNativeReview':c['nativePoseReview'],'contactPreview':f"previews/walk/{c['actor']}/contact.jpg",'reviewedNormalSpeed':True,'reviewedHalfSpeed':True,'reviewMethod':'All four registered cels actually viewed on light/dark contact boards; current11-identity live browser composite observed at1x and0.5x, with repeated frame changes and full-page snapshots; not a video-motion smoothness claim.','findings':[notes[c['actor']],'No visible crop, solid rectangular matte, stray neighboring actor, missing appendage or mirror-only half-cycle in the adopted cels.'],'blockingIssues':[],'limits':['Deliberately stepped four-key-cel loop, small original drawing variation; not fluid I2V or Unity validation.']})
v={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','actors':actors,'all11Reviewed':True,'normalAndHalfSpeedPages':['previews/playback.html','previews/composite-playback.html'],'observedLiveComposite':{'allImagesLoaded':58,'identities':11,'normalRunningFrameChanges':[973,1056],'halfSpeedRunningFrameChanges':[1056,1271,1275],'normalPoseSnapshots':['4/4/4/2/2/4/4/2/2/2/2','1/1/1/3/3/1/1/3/3/3/3'],'halfSpeedPoseSnapshots':['1/1/1/1/1/1/1/1/1/1/1','2/2/2/1/1/4/4/1/1/1/1','1/1/1/3/3/2/2/3/3/3/3']},'automatedHeadFitAdopted':False,'perFrameBBoxScaleNormalization':False,'unityVerified':False}
(R/'records/walk-playback-review.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
comp={'reviewedAtUtc':v['reviewedAtUtc'],'passed':True,'page':'previews/composite-playback.html','actualBrowserPlayback':True,'all11ActorsSeen':True,'actualImagesLoaded':58,'normalAndHalfSpeedObserved':True,'orientationsActuallyViewed':['landscape1152x760','portrait760x1152'],'scope':'Image overlays, identity/alpha readability and moving repeat texture only; no gameplay or Unity acceptance','findings':['All eleven body identities retain readable silhouettes and complete appendages against the actual repeating ground.','Five player/enemy projectile images and nine XP/money images are readable with no rectangular mattes.','No conspicuous straight join or lighting band seen at observed scrolling offsets; visual repetition remains visible as expected for one tile.','Four-cel gait remains deliberately stepped; minor native head/cloth variance retained without per-frame bbox normalization.'],'blockingIssues':[],'unityVerified':False}
(R/'records/composite-playback-review.json').write_text(json.dumps(comp,ensure_ascii=False,indent=2),encoding='utf-8')
print('Recorded root actual review for current11clips/44frames')
