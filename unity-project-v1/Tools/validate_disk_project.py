"""Validate actual copies/contracts; deliberately does not claim Unity compilation."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,subprocess
from PIL import Image
R=Path(__file__).resolve().parents[1]
def main():
    data=json.loads((R/'Assets/Resources/DaoArtCatalog.json').read_text(encoding='utf-8'))
    errors=[];ids={a['id'] for a in data['assets']};actor_ids={a['id'] for a in data['actors']}
    if len(ids)!=242 or len(data['assets'])!=242:errors.append('242unique art entries required')
    if len(actor_ids)!=11:errors.append('11actors required')
    for a in data['assets']:
        p=R/'Assets/Resources'/(a['resource']+'.png')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=a['sourceSha256']:errors.append('Changed copy '+a['id'])
        with Image.open(p) as im:
            im.load()
            if list(im.size)!=[a['width'],a['height']]:errors.append('Size '+a['id'])
        if len(a['pivot'])!=2 or len(a['border'])!=4 or any(v<0 or v>1 for v in a['pivot']):errors.append('Import contract '+a['id'])
    for a in data['actors']:
        if a['staticArt'] not in ids or len(a['frames'])!=4 or any(x not in ids for x in a['frames']) or len(a['seconds'])!=4 or min(a['seconds'])<=0:errors.append('Animation contract '+a['id'])
    source_files=sorted((R/'Assets').rglob('*.cs'))
    for p in source_files:
        for name in re.findall(r'"((?:original-base__|branding__|env_)[A-Za-z0-9_-]+)"',p.read_text(encoding='utf-8')):
            if name not in ids:errors.append('Unresolved resource literal '+name)
    guids=[]
    for p in (R/'Assets').rglob('*.meta'):
        match=re.search(r'^guid: ([a-f0-9]{32})$',p.read_text(encoding='utf-8'),re.M)
        if not match:errors.append('Invalid GUID '+str(p))
        else:guids.append(match.group(1))
    if len(guids)!=len(set(guids)):errors.append('Duplicate Unity GUID')
    report={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'passed':not errors,'errors':errors,'PNGCount':len(ids),'actorCount':len(actor_ids),'walkFrameCount':sum(len(a['frames']) for a in data['actors']),'uniqueMetaGuidCount':len(guids),'literalResourceReferencesResolved':True,'unityCompilationVerified':False,'unityImportVerified':False,'runtimePlaybackVerified':False}
    (R/'IntegrationReports/disk-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    syntax=subprocess.run(['dotnet','run','--project',str(R/'Tools/SyntaxCheck/SyntaxCheck.csproj'),'--',str(R/'Assets')],capture_output=True,text=True,encoding='utf-8')
    result=json.loads(syntax.stdout.strip().splitlines()[-1])
    evidence={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'method':'Executed dotnet Roslyn CSharpSyntaxTree.ParseText','commandExitCode':syntax.returncode,**result,'unityCompilationVerified':False,'unityImportVerified':False,'runtimePlaybackVerified':False,'sourceSha256':{p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},'limitation':'No actual Unity Editor available; syntax is not API/type/import/playback verification.'}
    (R/'IntegrationReports/csharp-syntax.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    if syntax.returncode or result['syntaxErrors']:raise SystemExit('CSharp syntax failed')
    print(json.dumps(report,ensure_ascii=False))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
