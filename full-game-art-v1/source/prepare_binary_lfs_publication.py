"""Rebuild the unpublished delivery snapshot with binaries in LFS; preserve HEAD/index."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,os,json,hashlib
R=Path(__file__).resolve().parents[1];REPO=R.parent
BASE='codex/deliver-yifu-zhen-wanyao-art';BRANCH='codex/deliver-yifu-zhen-wanyao-lfs'
def run(args,**kw):return subprocess.run(['git',*args],cwd=REPO,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw).stdout
def text(args,**kw):return run(args,**kw).decode('utf-8').strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    head=text(['rev-parse','HEAD']);indexhash=sha(REPO/'.git/index');env=os.environ.copy();env['GIT_INDEX_FILE']=str(REPO/'.git/publish-index-binary-lfs-yifu-20261029')
    if Path(env['GIT_INDEX_FILE']).exists():raise FileExistsError('Keep existing temporary index')
    run(['read-tree',BASE],env=env)
    entries=text(['ls-tree','-r','--name-only',BASE]).splitlines();binary=[]
    extensions={'.png','.jpg','.jpeg','.otf','.ttf','.zip'}
    for rel in entries:
        if Path(rel).suffix.lower() in extensions:
            p=REPO/rel
            if not p.is_file() or not p.resolve().is_relative_to(R.resolve()):raise ValueError('Binary outside final task '+rel)
            binary.append(rel)
    attrs=''.join('*'+ext+' filter=lfs diff=lfs merge=lfs -text\n' for ext in sorted(extensions))
    attrfile=REPO/'.git/publication-binary-lfs.attributes';attrfile.write_text(attrs,encoding='utf-8')
    pathspec=REPO/'.git/publication-binary-lfs.pathspec';pathspec.write_bytes(b''.join(s.encode('utf-8')+b'\0' for s in binary))
    run(['-c','core.attributesFile='+str(attrfile),'add','--renormalize','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul'],env=env)
    def add_blob(rel,blob):
        oid=text(['hash-object','-w','--stdin'],input=blob,env=env);run(['update-index','--add','--cacheinfo','100644,'+oid+','+rel],env=env)
    add_blob('.gitattributes',attrs.encode('utf-8'))
    readme=run(['show',BASE+':README.md']).decode('utf-8').replace('资源PNG和字体本身是普通Git文件，未以LFS指针冒充图片。','图片、字体和ZIP均通过Git LFS保存；克隆后请确认Git LFS已安装并执行 `git lfs pull`，取回真正的PNG/字体/ZIP。仓库原始Git树中的LFS指针仅用于版本管理，不是运行时素材。')
    add_blob('README.md',readme.encode('utf-8'))
    add_blob(Path(__file__).relative_to(REPO).as_posix(),Path(__file__).read_bytes())
    tree=text(['write-tree'],env=env);commit=text(['commit-tree',tree],input='Deliver complete 一符镇万妖 art using Git LFS for binary assets\n\nPublish the verified242PNG/131UI/11walk art snapshot with image,font andZIP binaries in LFS, avoiding unreliable large ordinaryGit transfers. Preserve all original local branches and user index.\n'.encode('utf-8'),env=env)
    run(['update-ref','refs/heads/'+BRANCH,commit,'0'*40])
    if text(['rev-parse','HEAD'])!=head or sha(REPO/'.git/index')!=indexhash:raise RuntimeError('Original HEAD/index changed')
    stats={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'branch':BRANCH,'commit':commit,'tree':tree,'binaryFileCount':len(binary),'originalMainCommit':head,'originalMainUnchanged':True,'originalIndexUnchanged':True,'oldUnpublishedSnapshotPreserved':BASE,'pushStatus':'prepared-not-yet-pushed'}
    (R/'records/git-binary-lfs-publication.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(stats,ensure_ascii=False))
if __name__=='__main__':main()
