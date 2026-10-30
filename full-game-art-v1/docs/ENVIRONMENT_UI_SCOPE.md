> 此文是制作前的固定commit范围审计快照，文中的当时缺项保留作证据。当前交付状态请看 `ACCEPTANCE.md` 与 `records/final-resource-manifest.json`。

# 全游戏场景与UI美术收口审计

功能参考为[VampireSurvivorsClone](https://github.com/matthiasbroske/VampireSurvivorsClone)，固定commit `01f8c76e40f52b853117f436d6d3d08f80a41506`。本审计只读E盘既有成品及固定commit文字；没有读取F盘图片、复制上游图片、生图、改UI、改代码、Unity运行或Git变更。文件/行号/SHA、远端纯文字回执和完整清单在[JSON](../records/environment-ui-full-scope.json)。

## 数量结论

- BuildSettings启用2个场景：菜单Main Menu、可玩Level1。角色确认固定载入索引1，所以当前游戏只有1个可玩战斗场景。
- 两份关卡配置为Level1和Test Level；场景引用GUID实际对应Level1，Test Level没有成为第二关。另有Character Set Generation工具场景，未启用，不扩成新游戏地图。
- 环境硬缺1张可连续平铺、可任意偏移的俯视战斗地面。当前无限地面材质还引用1张噪声数据纹理，需自主提供或在后续接入明确关闭反重复分支。它是技术纹理，不是第二张地图。
- 已有109张旧UI加22张新增功能图，共131张冻结界面；核心菜单、选角、HUD、选卡、暂停、结算和语言流程未发现必须再画的新整屏缺口。此处按清单/文本核对，不等于131张逐像素重验或Unity功能完成。

## 无限地面与现有庭院背景

绑定链已按GUID和固定commit meta核实：Level1.scene → Level1.asset(`ace7…`) → DirtTile(`42b11…`)；Infinite Background.mat(`4d3…`)使用InfiniteTile.shader，主纹理为同一DirtTile，NoiseTex是WhiteNoise256(`76b38…`)，`_AvoidRepitition=1`，`_Scale=4.5`。

[InfiniteBackground](https://github.com/matthiasbroske/VampireSurvivorsClone/blob/01f8c76e40f52b853117f436d6d3d08f80a41506/Assets/Scripts/Utilities/InfiniteBackground.cs)把Mesh缩放到相机视口，并把关卡纹理赋入材质。Shader依据世界XY坐标采样，循环偏移并以噪声混合不同偏移，磁铁触发的冲击波也通过同一材质处理。[Shader](https://github.com/matthiasbroske/VampireSurvivorsClone/blob/01f8c76e40f52b853117f436d6d3d08f80a41506/Assets/Shaders/InfiniteTile.shader#L92)因此要求无天空、无地平线、无巨大固定太极中心、无对不上边的建筑。随机偏移混合不适合强规则大图案。

我实际查看本项目两张原创庭院图：横1672×941、竖941×1672，均有天空、消失点、正面建筑及中心太极，适合UI场景展示。它们继续保留，不能据此把“无限战斗地面”标为已验收。背景文件仍在`original-monsters-v1/assets/context/`，本轮没有编辑。

| 必做槽位 | 建议规格 | 验收 |
|---|---|---|
| `env_battle_ground_01` | 原创俯视手绘2048²不透明PNG，暖浅灰/青灰低对比石地或土石；玉绿/暖金点到为止；相对边连续 | 3×3平铺、两对边、随机偏移/平移预览；叠加角色/弹体检查辨识；横1920×1080及竖1080×1920视口都看 |
| `env_repeat_noise` | 自主技术噪声256²，Repeat；数据来源与手绘图区分 | 原材质需要此槽；是否linear/sRGB、Mip与压缩由后续Shader接入验证；不复制上游像素 |

战斗地面作为Texture Default/Repeat U,V/Bilinear起步；不是Sprite，也不做九宫格。Mip、压缩与纹理世界缩放须后续设备验证。`4.5`仅为源材质参数证据，不是新美术已测试的世界单位合同。单张可重复地面可同时服务横竖屏，不需要旋转或另造竖版地图。

## 环境物、边界、阴影及全屏效果

已启用场景和玩法代码没有Tilemap、实体墙/树/岩石障碍、边界或城镇地形配置。场景没有单独脚下阴影Sprite必需槽，地面Mesh也关闭投射/接收阴影。因此不为“全部”自动扩城镇、主城65536图块、阻挡树石、多关卡、天气、昼夜、碰撞边界或阴影系统。软椭圆影子可以是美术增强，必须标可选。

两个实用槽位应在最终资源总表明确：

1. 朝向指示：Character.Update只把`lookIndicator`移到面向方向乘半径，不要求独立方向动画。可用128²/256²透明中性环/标记，或明确映射到本项目已有简单Sprite；要记录别名和Pivot，不能在总表遗漏。
2. 炸弹白闪：EntityManager.Flash打开白色全屏Sprite，在约0.25秒内改变Alpha，然后隐藏。可用标准白色矩形/一个中性白纹理；这是基础几何，不需要新绘手绘全屏爆炸或逐帧片。磁铁是地面材质Shockwave，不能把额外独立波纹动画当源码硬缺。旧的暗遮罩与白闪角色不同。

## 核心UI流程对应

| 源功能 | 现有成图 | 当前结论 |
|---|---|---|
| 主菜单/开始/返回 | 旧`01-main`、`06-pause`、`08-dialog-exit` | 保留；源Shop/强化只有标签和空点击，不扩商店/永久技能树 |
| 选角、拥有/购买/余额不足 | 新`character_select_owned/buyable/insufficient` | 横竖齐；买入后变拥有，再点击已拥有角色才开始 |
| 生存HUD、四库存及空态 | 新`survival_hud_normal/empty` | 横竖齐；血/经验/等级/击杀/铜钱/计时+四道具。旧演示的灵力/主动技能布局保持原图，接入以新增源码对齐图为准 |
| 升级选卡 | 新`levelup_three/four/one` | 横竖齐；直接选择，0项关闭并宝箱回退，不需要0项空界面/确认/刷新/跳过 |
| 暂停/恢复 | 旧`06-pause` | 有静态暂停设计；play/pause可由已有文字按钮表达，状态逻辑不在美术阶段实现 |
| 胜负结算 | 新`survival_results_win/loss` | 横竖齐；四统计为铜钱/击杀/造成伤害/受到伤害 |
| 语言 | 新`locale_dropdown_open`及设置页 | 英语/简中/繁中为动态文字；即时切换，无源Save步骤；无需3份烘焙语言底图 |

131张现有图全部冻结；旧UI的演示扩展和源功能差异通过交接文档说明，不能为了对齐源码改用户已经确认的UI。新22图用于源功能真实语义。所有动态数字/名称/文案独立排版，牌框图不随语言重画。

## 已确认扩展及不新增项

旧图中的10条任务及任务状态、装备/背包分类、图鉴/遭遇和设置多页是已确认演示扩展，继续保留，单列于上游基线。图鉴“精英”标签不证明上游新增精英类；任务文字也不自动证明要制作实体NPC、城镇或社交功能。没有网络流程，就不额外强制联网失败/服务器列表等界面；没有关卡选择流程，就不造多地图选关。

## 字体与验收边界

现有预览合成脚本实际用STKAITI.TTF和msyh.ttc，但本审计没有复制或确认这些Windows字体可再分发。后续动态Text/TMP应选择有明确发行许可、覆盖英语/简体/繁体的字体，并随交付保留许可。现有PNG与布局继续保留，不因此重绘。若最终包宣称已含运行时字体，必须另有字体文件及许可核实，不能以预览可见中文代替。

本报告仅收敛环境/UI范围。地面与噪声纹理、实用槽位映射及相应美术检查仍需完成；角色/怪物静态、walk、能力与FX覆盖由并行清单另审。Unity运行、碰撞、材质效果、Safe Area、设备显示均留下一阶段，不能在本次审计称已完成。
