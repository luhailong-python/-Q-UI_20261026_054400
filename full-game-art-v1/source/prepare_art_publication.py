"""Create an isolated initial art-delivery branch without touching HEAD or real index."""
from pathlib import Path
from datetime import datetime,timezone
import os,json,subprocess,hashlib,re
R=Path(__file__).resolve().parents[1];REPO=R.parent
BRANCH='codex/deliver-yifu-zhen-wanyao-art'
def run(args,**kw):
    return subprocess.run(['git',*args],cwd=REPO,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw).stdout
def txt(args,**kw):return run(args,**kw).decode('utf-8').strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(REPO/'.git/publish-index-yifu-20261029')
    if Path(env['GIT_INDEX_FILE']).exists():raise FileExistsError('Preserve existing temporary index')
    head_before=txt(['rev-parse','HEAD']);real_index=REPO/'.git/index';index_before=sha(real_index) if real_index.exists() else None
    if txt(['branch','--show-current'])!='main':raise RuntimeError('Unexpected checkout')
    package=json.loads((R/'records/complete-delivery-package.json').read_text(encoding='utf-8'))
    m=json.loads((R/'records/complete-art-manifest.json').read_text(encoding='utf-8'))
    if not m['artComplete'] or m['missingRequiredArt']:raise RuntimeError('Art incomplete')
    paths={R/a['file'] for a in package['entries']}
    paths.update([R/'records/complete-delivery-package.json',R/'assets/complete-asset-list.csv',R/'records/complete-art-manifest.json',Path(__file__)])
    normal=sorted(p for p in paths if p.is_file() and p.suffix.lower()!='.zip')
    for p in normal:
        if not p.resolve().is_relative_to(R.resolve()):raise RuntimeError('Outside task '+str(p))
        if p.stat().st_size>=100*1024*1024:raise RuntimeError('Oversized ordinary blob '+str(p))
        if p.suffix.lower() in {'.json','.md','.txt','.html','.py','.csv'}:
            s=p.read_text(encoding='utf-8-sig',errors='replace')
            if re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|\b(?:ghp_|github_pat_)[A-Za-z0-9_]{25,}|\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}',s):raise RuntimeError('Credential-like content '+str(p))
    run(['read-tree','--empty'],env=env)
    pathspec=REPO/'.git/publish-pathspec-yifu-20261029'
    pathspec.write_bytes(b''.join(p.relative_to(REPO).as_posix().encode('utf-8')+b'\0' for p in normal))
    run(['add','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul'],env=env)
    def add_blob(path,blob):
        oid=txt(['hash-object','-w','--stdin'],input=blob,env=env)
        run(['update-index','--add','--cacheinfo','100644,'+oid+','+path],env=env)
    attributes=b'*.zip filter=lfs diff=lfs merge=lfs -text\n'
    add_blob('.gitattributes',attributes)
    add_blob('.gitignore',b'__pycache__/\n*.pyc\n.DS_Store\n')
    readme='''# 一符镇万妖 · 道家Q版游戏美术

已完成并验收的本地美术交付，对应固定功能基线与已确认演示扩展。正式名称与Logo已纳入本仓库。

- **242张正式PNG**：235张游戏美术与7张Logo/徽记尺寸版本。
- **131张横竖UI与状态图**，保持已确认原像素。
- **3角色、6普通怪、2首领**，11组原创行走/浮游循环、44张正式帧。
- 21类能力图标，武器/弹体/粒子/特效，经验/钱币/消耗品/宝箱，战斗地面与辅助图，两套字体及OFL。

[统一交付说明](full-game-art-v1/docs/COMPLETE_DELIVERY.md) · [逐图统一清单](full-game-art-v1/records/complete-art-manifest.json) · [Unity导入建议](full-game-art-v1/docs/UNITY_IMPORT.md)

[下载完整美术ZIP](full-game-art-v1/delivery/yifu_zhen_wanyao_complete_art_20261029.zip) · [ZIP SHA-256](full-game-art-v1/delivery/yifu_zhen_wanyao_complete_art_20261029.zip.sha256) · [包内逐文件校验记录](full-game-art-v1/records/complete-delivery-package.json)

![11身份动作总览](full-game-art-v1/previews/all-actors-walk-contact.jpg)

![游戏Logo](full-game-art-v1/branding-v1/assets/yifu-zhen-wanyao-logo-primary.png)

## 交付边界

身体动作为每身份4张独立绘制关键姿势组成的分格循环，已做正常/半速与浅深底美术审片。Unity工程、Prefab、动画控制、场景组装、业务与设备验证按约定留下一阶段。具体保留的原画差异与地面诊断见[验收说明](full-game-art-v1/docs/ACCEPTANCE.md)。

当前交付分支只收最终采用资源、原画来源、提示词、规格与验收证据，未上传早期废弃怪物408帧或参考代码子仓库。早期批次ZIP只留在本地历史记录；此分支以统一完整ZIP为准。原本地main历史未改写。

## 获取大交付包

ZIP通过Git LFS保存。使用已安装Git LFS的Git客户端克隆此分支，必要时在仓库中执行 `git lfs pull` 获取真实ZIP；GitHub网页也可从上方下载链接取文件。资源PNG和字体本身是普通Git文件，未以LFS指针冒充图片。
'''
    add_blob('README.md',readme.encode('utf-8'))
    lfs=[]
    for p in [R/package['file'],R/'branding-v1/delivery/yifu_zhen_wanyao_branding_v1.zip']:
        if not p.exists():raise FileNotFoundError(p)
        rel=p.relative_to(REPO).as_posix()
        with p.open('rb') as f:pointer=run(['lfs','clean','--',rel],stdin=f,env=env)
        s=pointer.decode('ascii')
        digest=sha(p)
        if not s.startswith('version https://git-lfs.github.com/spec/v1\n') or 'oid sha256:'+digest not in s or 'size '+str(p.stat().st_size) not in s:raise ValueError('Incorrect LFS pointer')
        add_blob(rel,pointer)
        side=p.with_suffix('.zip.sha256')
        add_blob(side.relative_to(REPO).as_posix(),side.read_bytes())
        lfs.append({'file':rel,'sha256':digest,'bytes':p.stat().st_size})
    tree=txt(['write-tree'],env=env)
    commit=txt(['commit-tree',tree],input='Deliver complete 一符镇万妖 game art and branding\n\nInclude242 runtime PNGs,131 retained UI designs,11 original four-pose walk cycles,fonts,provenance and verified delivery packages. Store ZIPs in Git LFS. Publish an isolated final-art snapshot; preserve original local main and reference-code checkout.\n'.encode('utf-8'),env=env)
    run(['update-ref','refs/heads/'+BRANCH,commit,'0'*40])
    if txt(['rev-parse','HEAD'])!=head_before or sha(real_index)!=index_before:raise RuntimeError('Original HEAD/index changed')
    record={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'branch':BRANCH,'commit':commit,'tree':tree,'parentCommits':[],'originalMainCommit':head_before,'originalMainUnchanged':True,'realIndexUnchanged':True,'sourceImagesVerifiedPreviously':242,'uiDesignsVerifiedPreviously':131,'normalStagedFiles':len(normal),'lfsPackages':lfs,'remote':'origin','remoteUrl':txt(['remote','get-url','origin']),'pushStatus':'prepared-not-yet-pushed'}
    p=R/'records/git-publication-preparation.json';p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False))
if __name__=='__main__':main()
