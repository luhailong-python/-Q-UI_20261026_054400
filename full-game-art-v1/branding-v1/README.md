# 一符镇万妖 · 命名与Logo补充包

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
