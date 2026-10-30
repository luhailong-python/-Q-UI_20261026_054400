# 一符镇万妖 · 道家Q版游戏美术

Unity下一阶段已启动：[接入工程与实际验证状态](unity-project-v1/README.md)。本地旧Git已清理，仅从当前交付快照继续；缓存/Library等不纳入版本。

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

身体动作为每身份4张独立绘制关键姿势组成的分格循环，已做正常/半速与浅深底美术审片。Unity下一阶段已建立工程、导入器与Prefab/动画/场景生成代码；真实编辑器导入、编译、播放以及业务与设备验证尚未完成。具体保留的原画差异与地面诊断见[验收说明](full-game-art-v1/docs/ACCEPTANCE.md)。

美术交付快照只收最终采用资源、原画来源、提示词、规格与验收证据，后续Unity工作在 `codex/unity-art-integration-v1` 分支继续。未上传早期废弃怪物408帧或参考代码子仓库。早期批次ZIP只保留为本地文件；交付以统一完整ZIP为准。旧本地main历史已按要求删除，已推送的美术快照保留。

## 获取大交付包

ZIP通过Git LFS保存。使用已安装Git LFS的Git客户端克隆此分支，必要时在仓库中执行 `git lfs pull` 获取真实ZIP；GitHub网页也可从上方下载链接取文件。图片、字体和ZIP均通过Git LFS保存；克隆后请确认Git LFS已安装并执行 `git lfs pull`，取回真正的PNG/字体/ZIP。仓库原始Git树中的LFS指针仅用于版本管理，不是运行时素材。
