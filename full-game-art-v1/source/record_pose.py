"""Record a real individual AI-painted walk pose, including actual master input."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import argparse,json,hashlib
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--actor',required=True);p.add_argument('--phase',type=int,required=True);p.add_argument('--master',required=True);p.add_argument('--prompt',required=True);p.add_argument('--version',default='');a=p.parse_args()
 if a.phase not in range(4):raise ValueError('phase0..3')
 src=Path(a.source);master=Path(a.master);prompt=R/a.prompt
 if a.version and (not a.version.isalnum()):raise ValueError('Version must be alphanumeric')
 suffix='_'+a.version if a.version else ''
 dest=R/f'assets/motion-native/{a.actor}/{a.actor}_walk_{a.phase:02d}{suffix}.png';dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists() and sha(dest)!=sha(src):raise FileExistsError('Use a versioned filename for repair, do not overwrite an adopted pose')
 dest.write_bytes(src.read_bytes());im=Image.open(dest);im.load()
 v={'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'operation':'AI individual pose edit from approved original master; not image-to-video and not transformed still animation','actor':a.actor,'action':'walk','phase':a.phase,'phaseRole':['left-contact','right-passing','right-contact','left-passing'][a.phase],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((R/'image-generation.json').read_text(encoding='utf-8-sig')),'prompt':a.prompt,'promptSha256':sha(prompt),'actualSubmittedToolArguments':{'promptTextFile':a.prompt,'referenced_image_paths':[str(master)],'transparent_background':True},'actualModel':None,'actualQuality':None,'selectorEvidence':'Tool exposes no model/quality selectors and returns no identifying metadata','references':[{'file':str(master),'sha256':sha(master),'role':'identity/shape/costume master, actually viewed before AI edit','sameProjectOriginal':True}],'returnedInformation':{'keys':['image_url','output_hint'],'outputFile':str(src),'imageDataOmittedFromText':True},'generatedAtUtc':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'generationTimeEvidence':'Output-file LastWriteTimeUtc; tool returned no time field','recordedAtUtc':datetime.now(timezone.utc).isoformat(),'nativeSize':list(im.size),'mode':im.mode,'alphaRange':list(im.getchannel('A').getextrema()) if 'A' in im.getbands() else None,'sourceArtFromFDrive':False,'adoptedForPlayback':False,'status':'native-pose-awaiting-registration-and-visual-review'}
 Path(str(dest)+'.generation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'file':str(dest),'size':im.size,'sha256':v['sha256'],'alphaRange':v['alphaRange']},ensure_ascii=False))
if __name__=='__main__':main()
