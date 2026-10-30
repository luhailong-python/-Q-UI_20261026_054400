"""Persist manual observations of recovered original cels. Does not draw poses."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
R=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def native_review(actor,master,files,anchors,notes,excluded):
    files=[f'assets/motion-native/{actor}/{f}.png' for f in files]
    v={'actor':actor,'master':str(master),'masterSha256':sha(master),'selectedFiles':files,'selectedFileSha256':[sha(R/f) for f in files],
       'anchors':[{'phase':i,'sourceTorsoX':a[0],'sourceGroundY':a[1],'definition':'Manually observed chest/body axis and physical planted-foot sole plane; not automatic whole-alpha bbox registration','supportNote':notes[i],'approximatePixelTolerance':12} for i,a in enumerate(anchors)],
       'animationKind':'walk','passed':True,'passedMeaning':'Four native articulated poses and identity checked only; registered playback is not yet approved.','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
       'actuallyViewedNativeFiles':files,'masterActuallyViewedBeforeEdits':True,'blockingIssues':[],'findings':['Native cels contain real leg articulation, including opposite fore/aft contact and different-side lifted passing feet.','Face, horns, head/torso ratio, costume and carried objects retained; no mirrored frame or transformed still used.','Alpha seen over light background; final dark/light playback remains required.'],
       'phaseObservations':notes,'excludedFiles':excluded,'remainingReview':['Normal and half-speed looping on light/dark backgrounds','Scale, foot placement, seam and continuity at display size'],'sourceRoute':'builtin image_gen individual pose edits; not I2V','unityVerified':False,'bodyFramesRegistered':False}
    write(R/f'records/motion/{actor}-native-review.json',v)

if __name__=='__main__':
    actor='orig_mob06'
    native_review(actor,R/'assets/native/orig_mob06.png',[f'{actor}_walk_{i:02d}' for i in range(4)],[(790,1192),(780,1165),(780,1190),(780,1173)],
       ['Viewer-right foreground foot plants ahead, viewer-left foot trails; stone club remains in viewer-left hand.','Viewer-left rear foot lifts with flexed knee while viewer-right foot supports.','Viewer-left foreground foot is now extended and planted, viewer-right foot smaller and trailing.','Viewer-left foot rises with visible sole; viewer-right foot supports, opposite lifted side from phase1.'],[])
    actor='orig_mob02'
    native_review(actor,R.parent/'original-monsters-v1/assets/orig_mob02/orig_mob02_master_E.png',[f'{actor}_walk_00',f'{actor}_walk_01',f'{actor}_walk_02_v2',f'{actor}_walk_03_v2'],[(710,1192),(710,1222),(710,1214),(710,1195)],
       ['Viewer-right stone foot contacts in foreground; viewer-left foot trails.','Viewer-left stone foot supports while viewer-right knee and jade toe rise.','Repaired opposite contact: viewer-left leg extends to lower-left foreground with large planted toe; viewer-right leg recedes.','Opposite passing: viewer-left sole is lifted and viewer-right foot planted. Targeted repair restores cuff exclusively to viewer-left arm.'],['assets/motion-native/orig_mob02/orig_mob02_walk_02.png','assets/motion-native/orig_mob02/orig_mob02_walk_03.png'])
    # The repair was submitted with two actual image inputs, unlike a normal one-master pose.
    p=R/'assets/motion-native/orig_mob02/orig_mob02_walk_03_v2.png.generation.json'
    v=json.loads(p.read_text(encoding='utf-8'))
    target=R/'assets/motion-native/orig_mob02/orig_mob02_walk_03.png';master=Path(v['references'][0]['file'])
    v['actualSubmittedToolArguments']['referenced_image_paths']=[str(target),str(master)]
    v['references']=[{'file':str(target),'sha256':sha(target),'role':'precise costume continuity edit target, actually viewed','sameProjectOriginal':True},{'file':str(master),'sha256':sha(master),'role':'accepted identity master, actually viewed','sameProjectOriginal':True}]
    v['operation']='AI targeted cuff-side continuity repair preserving passing pose, with actual edit target plus identity master attached'
    write(p,v)
