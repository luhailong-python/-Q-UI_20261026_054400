"""Verify existing game art plus later branding and publish one local art bundle."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,zipfile,csv
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    core=read(R/'records/final-resource-manifest.json');brand=read(R/'branding-v1/records/brand-assets.json')
    walk=read(R/'records/walk-exports.json');play={a['actor']:a for a in read(R/'records/walk-playback-review.json')['actors']}
    combined=[]
    for a in core['assets']:
        combined.append({**a,'deliveryGroup':'core-game-art'})
    for i,a in enumerate(brand['assets']):
        combined.append({**a,'id':'branding__'+Path(a['file']).stem,'name':'一符镇万妖 '+('主Logo' if 'logo-primary' in a['file'] else '符印徽记'),'file':'branding-v1/'+a['file'],'source':'branding-v1/'+a['source'],'deliveryGroup':'branding','status':'art-and-alpha-reviewed'})
    errors=[]
    for a in combined+core['screens']+core['nativeSources']:
        p=R/a['file']
        if not p.exists() or sha(p)!=a['sha256']:errors.append('Missing or changed '+a['file']);continue
        with Image.open(p) as im:
            im.load()
            if a.get('size') and list(im.size)!=a['size']:errors.append('Size '+a['file'])
    for a in core['screens']:
        if sha(Path(a['sourceFile']))!=a['sha256']:errors.append('Frozen UI '+a['file'])
    required={'hero_daotong','hero_lingyi','hero_leixiu','orig_mob01','orig_mob02','orig_mob03','orig_mob04','orig_mob05','orig_mob06','orig_boss_minor','orig_boss01'}
    if {c['actor'] for c in walk['clips']}!=required or len(walk['clips'])!=11:errors.append('Actor coverage')
    for c in walk['clips']:
        pr=play[c['actor']]
        if not c['playbackAccepted'] or not pr['accepted'] or pr['frameSha256']!=[f['sha256'] for f in c['frames']] or pr['durationsMs']!=[f['durationMs'] for f in c['frames']]:errors.append('Playback '+c['actor'])
    if len(combined)!=242 or len(core['screens'])!=131:errors.append('Delivery counts')
    if not read(R/'branding-v1/records/acceptance.json')['passed']:errors.append('Branding review')
    if not read(R/'records/final-acceptance.json')['allGameArtComplete']:errors.append('Core review')
    fonts=read(R/'records/font-sources.json')
    for f in fonts['fontFiles']:
        for field,digest in [('fontFile','fontSha256'),('licenseFile','licenseSha256')]:
            if sha(R/f[field])!=f[digest]:errors.append('Font/license '+f[field])
    if errors:raise ValueError(str(errors))
    manifest={'assembledAtUtc':datetime.now(timezone.utc).isoformat(),'gameName':'一符镇万妖','referenceCommit':core['referenceCommit'],'scope':'Previously confirmed whole-game art scope plus later approved naming/logo work','artComplete':True,'missingRequiredArt':[],'runtimeImageCount':len(combined),'coreGameImageCount':len(core['assets']),'brandingImageCount':len(brand['assets']),'uiDesignCount':len(core['screens']),'actorIdentityCount':11,'walkClipCount':11,'walkFrameCount':44,'fontFamilyCount':len(fonts['fontFiles']),'existing131UIPixelsChanged':False,'assets':combined,'screens':core['screens'],'clips':walk['clips'],'coreManifest':'records/final-resource-manifest.json','brandManifest':'branding-v1/records/brand-assets.json','artAcceptance':['records/final-acceptance.json','records/walk-playback-review.json','records/composite-playback-review.json','branding-v1/records/acceptance.json'],'unityVerified':False,'limits':['Each body has a four-key-pose stepped original walk/hover loop; not continuous video or additional action families.','Ground is native1254px visual repeat with documented numeric edge differences.','Unity import, animation control, scene/prefab/logic and device verification remain the agreed next stage.']}
    write(R/'records/complete-art-manifest.json',manifest)
    with (R/'assets/complete-asset-list.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['id','name','file','deliveryGroup','size','mode','pivot','borderLeftBottomRightTop','sha256','status'];w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(combined)
    doc='''# 一符镇万妖 · 全游戏美术统一交付

当前确认范围的美术已齐并验收。本统一包收齐原游戏美术和后来完成的正式名称/Logo，不需要另外寻找品牌补充包。

| 内容 | 已交付 |
|---|---|
| 正式PNG | 242张：235张游戏美术 + 7张Logo/徽记及尺寸版本 |
| 横竖UI设计与状态图 | 131张，保留原像素 |
| 角色与怪物 | 3角色、6普通怪、2首领，共11身份 |
| 必需身体动作 | 11组原创行走/浮游循环，共44张正式帧 |
| 能力与战斗美术 | 21类能力图标，配套武器、弹体、粒子、爆裂、流火、引力井 |
| 拾取与物件 | 4档经验、5档钱币、4消耗品、共用宝箱三态 |
| 场景与辅助图 | 战斗重复地面、噪声、方向标记、阴影、白闪 |
| 字体 | 两套字体及对应OFL许可，正文/标题回退规则已附 |

逐图规格、来源与SHA以 `records/complete-art-manifest.json` 和 `assets/complete-asset-list.csv` 为统一索引。原批次清单保留以便溯源，不会把本次合并打包说成新画了242张原画。

## 查看与使用

- `previews/index.html`：动作、全角色叠加、地面和特效播放入口。
- `previews/all-actors-walk-contact.jpg`：11身份的四姿势浅深底总览。
- `branding-v1/README.md`：主Logo、符印徽记与多尺寸透明PNG。
- `docs/UNITY_IMPORT.md`：Sprite、Pivot、九宫格、字体与纹理导入建议。
- `docs/ACCEPTANCE.md`：实际验收证据、保留的地面诊断和原画差异。

动作按每身份4张独立AI关键姿势组成分格循环，已做浅深底和正常/半速审片。Unity导入、动画控制、Prefab、场景、业务与设备验证按约定留下一阶段，尚未执行。美术交付完成不代表可玩的Unity工程已经完成。

本次只合并本项目已采用成果与新增品牌文件，未重画131张UI，未读写F盘、未Git提交或发布。旧交付ZIP保留。新的完整包：`delivery/yifu_zhen_wanyao_complete_art_20261029.zip`；同名`.zip.sha256`为包校验值，逐文件打包记录保存在`records/complete-delivery-package.json`。
'''
    (R/'docs/COMPLETE_DELIVERY.md').write_text(doc,encoding='utf-8')
    p=R/'README.md';s=p.read_text(encoding='utf-8')
    entry='\n**当前完整交付已合并Logo：242张正式图片、131张设计图、11组44帧动作。** [统一交付说明](docs/COMPLETE_DELIVERY.md) · [统一完整ZIP](delivery/yifu_zhen_wanyao_complete_art_20261029.zip)。下方235张/旧ZIP为上一批次记录，继续保留。\n'
    if '当前完整交付已合并Logo' not in s:s=s.replace('# 道家Q版全游戏美术收口\n','# 道家Q版全游戏美术收口\n'+entry,1);p.write_text(s,encoding='utf-8')
    previous=read(R/'records/delivery-package.json')
    paths={R/a['file'] for a in previous['entryManifest']}
    paths.update(p for p in (R/'branding-v1').rglob('*') if p.is_file() and 'delivery' not in p.relative_to(R/'branding-v1').parts and '__pycache__' not in p.parts)
    paths.update([R/'README.md',R/'docs/COMPLETE_DELIVERY.md',R/'records/complete-art-manifest.json',R/'assets/complete-asset-list.csv',Path(__file__)])
    dest=R/'delivery/yifu_zhen_wanyao_complete_art_20261029.zip'
    if dest.exists():raise FileExistsError('Preserve existing version')
    entries=[]
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(paths):
            if not p.is_file():raise FileNotFoundError(str(p))
            rel=p.relative_to(R).as_posix();z.write(p,'yifu_zhen_wanyao_art/'+rel);entries.append({'file':rel,'sha256':sha(p),'bytes':p.stat().st_size})
    with zipfile.ZipFile(dest) as z:
        bad=z.testzip()
        if bad:raise ValueError('CRC '+bad)
        for a in entries:
            if hashlib.sha256(z.read('yifu_zhen_wanyao_art/'+a['file'])).hexdigest()!=a['sha256']:raise ValueError('Archived SHA '+a['file'])
        for a in combined:
            if 'yifu_zhen_wanyao_art/'+a['file'] not in z.namelist():raise ValueError('Missing packaged runtime '+a['file'])
    v={'builtAtUtc':datetime.now(timezone.utc).isoformat(),'gameName':'一符镇万妖','file':dest.relative_to(R).as_posix(),'bytes':dest.stat().st_size,'sha256':sha(dest),'entryCount':len(entries),'runtimePNGCount':242,'uiDesignCount':131,'walkClipCount':11,'brandingIncluded':True,'crcVerified':True,'allArchivedEntryHashesVerified':True,'entries':entries,'oldPackagesPreserved':True}
    write(R/'records/complete-delivery-package.json',v);dest.with_suffix('.zip.sha256').write_text(v['sha256']+'  '+dest.name+'\n',encoding='utf-8')
    print(json.dumps({k:v[k] for k in ['file','bytes','sha256','entryCount','brandingIncluded','crcVerified','allArchivedEntryHashesVerified']},ensure_ascii=False))
if __name__=='__main__':main()
