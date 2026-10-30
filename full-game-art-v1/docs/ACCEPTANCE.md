# 美术交付验收

本批范围是固定commit `01f8c76e40f52b853117f436d6d3d08f80a41506` 对应的全部游戏图片、美术与已确认演示任务扩展。正式项目远端未提供。131张旧UI保持原像素；新增游戏美术均使用本项目原创来源。

当前汇总：235张正式图片、131张横竖设计/状态图、11个身体身份、11组4姿势行走共44帧、21类能力图标、4档经验/5档钱、4类消耗品、宝箱三态、战斗场景、弹体/武器/粒子/特效与辅助纹理。数量是交付文件数，不冒充独立原画数量。

最终判定与逐图SHA：`records/final-acceptance.json`、`records/final-resource-manifest.json`。动作须以 `walk-playback-review.json` 当前帧SHA匹配为准。静态功能审计文档中的“缺失”是制作前快照，当前状态由上述最终记录覆盖。

## 实际检查

- 131张设计图逐张与原E盘图做字节哈希核对，保持现有UI像素。
- 11组原画均检查身份、持物同手、接触腿和抬腿交替；灯芯小魅检查原有壳体、两条带和三穗的真实变化。错误旧稿保留在工作目录，没有当作运行时帧。
- 注册后的正式帧检查浅米、深玉底，正常/半速播放、逐帧与首尾恢复；全角色叠加在移动重复地面复核。记录中明确区分原画检查和播放验收。
- PNG解码、尺寸、真实Alpha、留白、源/正式哈希、帧时长、Pivot与Border均核对。字体本体和两份OFL验证，正文缺字0；装饰标题缺字时整条回退正文。
- 独立ZIP含正式资源、选定原画、来源、设计图、预览、提示词、许可与导入建议。包CRC及每个解压条目SHA结果见 `records/delivery-package.json` 和ZIP旁SHA文件。

## 公开保留限制

动作是每身份4张独立AI绘制关键姿势组成的有意分格循环，存在轻微手绘造型变化；不是图生视频、连续流体动作或新增run/attack/death套组。工具的实际型号与质量未披露，不将配置目标当返回证据。

地面诊断保留两项WARN（不是未修复图片错误）：

| id | value | threshold / requested | file | 处理 |
|---|---|---|---|---|
| native-size-below-prompt-target | [1254,1254] | requested [2048,2048] | assets/native/env_battle_ground_01.png | 保留原生1254²，不放大或宣称2048原生细节 |
| opposite-edge-not-identical | leftRightMeanAbsRGB 11.144869804382324; topBottomMeanAbsRGB 11.169590950012207 | 0 | assets/native/env_battle_ground_01.png | 实际平铺及移动审片通过；不称数学逐像素无缝 |

Unity导入、材质、动画控制、Prefab、场景组装、C#、业务与设备运行均按约定留下一阶段。PPU、Pivot、Border、导入压缩为接入建议，尚未在Unity验证。当前未Git提交、推送或发布。
