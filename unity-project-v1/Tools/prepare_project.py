"""Copy adopted art exactly and emit Unity6 import/animation contracts."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];ART=R.parent/'full-game-art-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    source=json.loads((ART/'records/complete-art-manifest.json').read_text(encoding='utf-8'))
    frames=json.loads((ART/'records/walk-exports.json').read_text(encoding='utf-8'))
    rows=[];proof=[];ids={};textures={'env_battle_ground_01','env_repeat_noise'}
    for a in source['assets']:
        original=ART/a['file'];key=a['id'];dest=R/'Assets/Resources/DaoArt'/f'{key}.png';dest.parent.mkdir(parents=True,exist_ok=True)
        if sha(original)!=a['sha256']:raise ValueError('Source changed '+str(original))
        if not dest.exists() or sha(dest)!=a['sha256']:shutil.copyfile(original,dest)
        if sha(dest)!=a['sha256']:raise ValueError('Copy mismatch')
        row={'id':key,'resource':'DaoArt/'+key,'kind':a.get('kind','branding'),'sourceSha256':a['sha256'],'width':a['size'][0],'height':a['size'][1],'pivot':a.get('pivot') or [.5,.5],'border':a.get('borderLeftBottomRightTop') or [0,0,0,0],'textureOnly':key in textures}
        rows.append(row);ids[key]=row
        proof.append({'id':key,'source':str(original),'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size})
    actors=[]
    for clip in frames['clips']:
        actor=clip['actor']
        if actor.startswith('hero_'):static='original-base__'+actor
        elif actor in ['orig_mob05','orig_mob06']:static=actor+'_runtime'
        else:static='original-base__'+actor+'_runtime_E'
        rec=next(a for a in source['assets'] if a['id']==static)
        with Image.open(ART/rec['file']) as im:
            b=im.getchannel('A').point(lambda x:255 if x>=16 else 0).getbbox();height=b[3]-b[1]
        names=[actor+f'_walk_{i:02d}' for i in range(4)]
        if any(k not in ids for k in names):raise ValueError('Missing frames '+actor)
        actors.append({'id':actor,'name':clip['name'],'staticArt':static,'frames':names,'seconds':[f['durationMs']/1000 for f in clip['frames']],'displayHeight':1.8 if actor.startswith('orig_boss') else 1.35 if actor.startswith('hero') else 1.05,'staticVisibleHeightPx':height,'floating':clip['animationKind']=='hover-walk'})
    write(R/'Assets/Resources/DaoArtCatalog.json',{'gameName':'一符镇万妖','assets':rows,'actors':actors})
    fonts=json.loads((ART/'records/font-sources.json').read_text(encoding='utf-8'))
    for f in fonts['fontFiles']:
        dest=R/'Assets/Resources/DaoFonts'/Path(f['fontFile']).name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ART/f['fontFile'],dest)
        if sha(dest)!=f['fontSha256']:raise ValueError('Font mismatch')
        license_dest=R/'Assets/ThirdPartyNotices'/f['id']/'OFL.txt';license_dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ART/f['licenseFile'],license_dest)
    write(R/'Packages/manifest.json',{'dependencies':{'com.unity.ugui':'2.0.0','com.unity.modules.animation':'1.0.0','com.unity.modules.audio':'1.0.0','com.unity.modules.imageconversion':'1.0.0','com.unity.modules.imgui':'1.0.0','com.unity.modules.jsonserialize':'1.0.0','com.unity.modules.physics':'1.0.0','com.unity.modules.physics2d':'1.0.0','com.unity.modules.ui':'1.0.0'}})
    settings=R/'ProjectSettings';settings.mkdir(exist_ok=True)
    (settings/'ProjectVersion.txt').write_text('m_EditorVersion: 6000.4.5f1\nm_EditorVersionWithRevision: 6000.4.5f1 (cc83ebd631f8)\n',encoding='utf-8')
    (settings/'ProjectSettings.asset').write_text('''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 28
  companyName: Independent
  productName: 一符镇万妖
  defaultScreenWidth: 1920
  defaultScreenHeight: 1080
  defaultIsNativeResolution: 0
  runInBackground: 1
  resizableWindow: 1
  fullscreenMode: 3
  activeInputHandler: 0
''',encoding='utf-8')
    # Stable script/data/folder GUIDs; Unity supplies importer payload on first real import.
    for p in sorted((R/'Assets').rglob('*')):
        if p.suffix=='.meta':continue
        meta=Path(str(p)+'.meta')
        if meta.exists():continue
        guid=hashlib.sha256(('yifu-art-integration-v1/'+p.relative_to(R).as_posix()).encode()).hexdigest()[:32]
        content='fileFormatVersion: 2\nguid: '+guid+'\n'
        if p.is_dir():content+='folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n'
        elif p.suffix=='.cs':content+='MonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
        meta.write_text(content,encoding='utf-8')
    write(R/'IntegrationReports/disk-preparation.json',{'completedAtUtc':datetime.now(timezone.utc).isoformat(),'diskPreparationPassed':True,'sourcePNGCount':len(rows),'actorCount':len(actors),'walkFrameCount':sum(len(a['frames']) for a in actors),'fontCount':len(fonts['fontFiles']),'allCopiesByteIdentical':True,'unityEditorDetected':False,'unityCompilationVerified':False,'unityImportVerified':False,'runtimePlaybackVerified':False,'expectedGeneratedAfterUnityRun':{'actorPrefabs':11,'animationClips':22,'animatorControllers':11,'reviewScenes':1},'copies':proof})
    print(json.dumps({'copiedPNGs':len(rows),'actorContracts':len(actors),'fontFiles':len(fonts['fontFiles']),'UnityActualValidation':'pending-editor'},ensure_ascii=False))
if __name__=='__main__':main()
