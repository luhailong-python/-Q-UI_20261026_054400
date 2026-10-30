from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--dest',required=True);ap.add_argument('--prompt',required=True);a=ap.parse_args()
    src=Path(a.source);dst=R/a.dest;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and dst.read_bytes()!=src.read_bytes():raise FileExistsError(dst)
    dst.write_bytes(src.read_bytes());im=Image.open(dst);im.load()
    data={'file':dst.relative_to(R).as_posix(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'nativeSize':list(im.size),'mode':im.mode,'alphaRange':list(im.getchannel('A').getextrema()) if 'A' in im.getbands() else None,'generatedAt':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'generationTimeEvidence':'Source output-file LastWriteTimeUtc; tool returned no time field','recordedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','operation':'AI-generated from text; byte-identical copy into project','configSnapshot':json.loads((R/'image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host manages model and quality; exposed tool has no selector and returned no identifying metadata','prompt':a.prompt,'references':[],'externalReferenceImagesUsed':False,'sourceArtFromFDrive':False,'returnedInformation':{'keys':['image_url','output_hint'],'outputFile':str(src),'imageDataOmittedFromText':True}}
    Path(str(dst)+'.generation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(data,ensure_ascii=False))
if __name__=='__main__':main()
