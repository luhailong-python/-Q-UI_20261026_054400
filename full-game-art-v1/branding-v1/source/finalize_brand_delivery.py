from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,zipfile,shutil,csv
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    m=read(R/'records/brand-assets.json');checks=[];failures=[];refmap=[]
    for a in m['assets']+m['nativeOriginals']:
        p=R/a['file'];im=Image.open(p);im.load()
        ok=sha(p)==a['sha256'] and im.mode=='RGBA' and list(im.size)==a['size'] and im.getchannel('A').getextrema()[0]==0
        if not ok:failures.append(a['file'])
        checks.append({'file':a['file'],'sha256':sha(p),'mode':im.mode,'size':list(im.size),'alphaRange':list(im.getchannel('A').getextrema()),'passed':ok})
    for a in m['nativeOriginals']:
        p=R/a['file'];g=read(Path(str(p)+'.generation.json'))
        if g['sha256']!=sha(p) or g['promptSha256']!=sha(R/g['promptFile']):failures.append('provenance '+a['file'])
        for ref in g['references']:
            src=Path(ref['file'])
            if sha(src)!=ref['sha256']:failures.append('reference '+str(src))
            if src.is_relative_to(R):dest=src
            else:
                dest=R/'sources'/src.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(src,dest)
            refmap.append({'actualInputFile':str(src),'packagedFile':dest.relative_to(R).as_posix(),'sha256':sha(dest)})
    write(R/'records/reference-map.json',refmap)
    acceptance={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'gameName':'一符镇万妖','passed':not failures,'failures':failures,'manualReview':{'actuallyReadTitleCharacters':['一','符','镇','万','妖'],'allFiveSimplifiedChineseCharactersCorrect':True,'nativeAndActualAlphaCompositeViewed':True,'primaryLightDark384pxActuallyViewed':True,'emblemLightDark128pxAnd64pxActuallyViewed':True,'style':'Jade/celadon, ivory, warm gold with cinnabar talisman, same-project original HD hand-painted Daoist chibi family','findings':['Five title glyphs read in correct order without duplicates or substitute characters.','Deep-jade silhouette keeps ivory/jade painted letters readable on pale and dark backgrounds.','Companion emblem retains the primary logo talisman, braided loop, jade cap, cinnabar mark and cloud crescent.','At64px small trim details soften; the ivory talisman/red mark/green cloud silhouette remains visible. Prefer128px+ for ornamental use.','No opaque rectangular matte, painted checkerboard, watermark or visibly clipped brush tip in actual alpha composite.']},'checks':checks,'artGeneration':'Two real built-in image_gen calls; native originals retained byte-identically','processing':'Transparent safety padding and premultiplied downscales only; no vector/PSD master or font file claimed','existingUIOverwritten':False,'unityVerified':False}
    write(R/'records/acceptance.json',acceptance)
    if failures:raise ValueError(str(failures))
    with (R/'assets/manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['file','size','mode','alphaRange','pivot','borderLeftBottomRightTop','operation','sha256'];w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(m['assets'])
    text='''# 一符镇万妖 · 命名与Logo补充包

游戏正式中文展示名采用 **一符镇万妖**。“一符”点出道家施法，“万妖”对应生存怪海，“镇”传达法术成型后的清场爽感。五字短名适合口头传播与上下两行排字。品牌决策和可独立排版的口号见 [BRAND_BRIEF.md](BRAND_BRIEF.md)。

## 直接使用

- [透明主Logo](assets/yifu-zhen-wanyao-logo-primary.png)：1680×1120，由1536×1024原生手绘Logo以1:1放入透明安全画布，没有放大细节。另附1200×800、768×512版本。
- [透明符印徽记](assets/yifu-zhen-wanyao-brand-emblem.png)：1392×1392，由1254×1254原生徽记以1:1补透明边；另附512、256、128像素版本。
- [浅深底与小尺寸预览](previews/brand-light-dark.jpg)。正式PNG本身透明，预览底色不在素材内。
- 原生图与逐图真实输入/回执：`assets/native/`；完整提示词：`prompts/`；参考来源：`sources/`与`records/reference-map.json`；规格清单：`records/brand-assets.json`及`assets/manifest.csv`。

主Logo在菜单/封面中建议显示宽度不小于320px；徽记建议128px起用于装饰。64px可辨识符纸/朱砂/云形，但细装饰会柔化。徽记是透明图形，不包含应用商店方形背景。

## Unity导入建议

Sprite(2D and UI)/Single、Pivot(0.5,0.5)、Border(0,0,0,0)、Simple、Preserve Aspect。Logo禁止九宫格拉伸。Bilinear、Clamp、Alpha Is Transparency、关闭Mipmap；初次使用无压缩，再按设备检查。主Logo Max Size至少2048；512徽记可用Max Size512。原生图与来源材料不必一起加入运行时图集。导入与设备表现尚未在Unity验证。

主Logo为AI绘制的定制字形，无对应字体、矢量或PSD源文件。已逐字核对一/符/镇/万/妖，检查真实Alpha、浅深底与小尺寸。图像入口没有披露真实型号或质量，实际字段记录为未确认。已有131张UI及上一轮501MiB游戏美术包保留原样；本包是后续新增品牌补充，不会批量替换旧设计图。

完整检查见 [records/acceptance.json](records/acceptance.json)。本轮使用内置image_gen，正式补充包位于`delivery/yifu_zhen_wanyao_branding_v1.zip`，同目录附SHA-256；这是PNG美术交付，没有发布或Git上传。
'''
    (R/'README.md').write_text(text,encoding='utf-8')
    dest=R/'delivery/yifu_zhen_wanyao_branding_v1.zip';dest.parent.mkdir(exist_ok=True)
    if dest.exists():raise FileExistsError('Keep prior package; choose another version')
    paths=[p for p in R.rglob('*') if p.is_file() and 'delivery' not in p.relative_to(R).parts and '__pycache__' not in p.parts and p.name!='package.json']
    entries=[]
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(paths):
            rel=p.relative_to(R).as_posix();z.write(p,'yifu_zhen_wanyao_branding/'+rel);entries.append({'file':rel,'sha256':sha(p),'bytes':p.stat().st_size})
    with zipfile.ZipFile(dest) as z:
        bad=z.testzip()
        if bad:raise ValueError('CRC '+bad)
        for a in entries:
            if hashlib.sha256(z.read('yifu_zhen_wanyao_branding/'+a['file'])).hexdigest()!=a['sha256']:raise ValueError('Archived digest '+a['file'])
    v={'builtAtUtc':datetime.now(timezone.utc).isoformat(),'file':dest.relative_to(R).as_posix(),'bytes':dest.stat().st_size,'sha256':sha(dest),'entryCount':len(entries),'crcPassed':True,'allEntryHashesPassed':True,'entries':entries}
    write(R/'records/package.json',v);dest.with_suffix('.zip.sha256').write_text(v['sha256']+'  '+dest.name+'\n',encoding='utf-8')
    print(json.dumps({k:v[k] for k in ['file','bytes','sha256','entryCount','crcPassed']},ensure_ascii=False))
if __name__=='__main__':main()
