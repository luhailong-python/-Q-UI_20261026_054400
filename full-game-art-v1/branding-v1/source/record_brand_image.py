"""Record actual native image generation and prepare optional runtime downscales."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,argparse,shutil
R=Path(__file__).resolve().parents[1];P=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--id',required=True);ap.add_argument('--args',required=True);ap.add_argument('--receipt',required=True);ap.add_argument('--prompt',required=True);a=ap.parse_args()
    src=Path(a.source);args=json.loads((R/a.args).read_text(encoding='utf-8'));receipt=json.loads((R/a.receipt).read_text(encoding='utf-8'))
    dest=R/f'assets/native/{a.id}.png';dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and sha(dest)!=sha(src):raise FileExistsError('Use a new version filename')
    shutil.copyfile(src,dest);im=Image.open(dest);im.load()
    refs=[{'file':f,'sha256':sha(Path(f)),'role':'actually viewed same-project original style/reference image','fromFDrive':False} for f in args.get('referenced_image_paths',[])]
    rec={'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'operation':'Native AI image output copied byte-identically; no artificial upscale or code-drawn replacement','tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((P/'image-generation.json').read_text(encoding='utf-8')),'actualSubmittedToolArguments':args,'actualReturnedInformation':receipt,'promptFile':a.prompt,'promptSha256':sha(R/a.prompt),'references':refs,'actualModel':None,'actualQuality':None,'undisclosedFields':'Exposed tool has no model/quality controls and no identifying model/quality return metadata','generatedAtUtc':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'generationTimeEvidence':'actual output file LastWriteTimeUtc; tool returns no timestamp field','recordedAtUtc':datetime.now(timezone.utc).isoformat(),'nativeSize':list(im.size),'mode':im.mode,'alphaRange':list(im.getchannel('A').getextrema()) if 'A' in im.getbands() else None,'sourceArtFromFDrive':False,'unityVerified':False}
    write(Path(str(dest)+'.generation.json'),rec)
    print(json.dumps({k:rec[k] for k in ['file','nativeSize','mode','alphaRange','sha256']},ensure_ascii=False))
if __name__=='__main__':main()
