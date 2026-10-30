> 此文是制作前的固定commit范围审计快照，文中的当时缺项保留作证据。当前交付状态请看 `ACCEPTANCE.md` 与 `records/final-resource-manifest.json`。

# 全角色、怪物、物件与动作美术范围核实

功能参考固定commit：`01f8c76e40f52b853117f436d6d3d08f80a41506`。只读本项目既有文字及同commit GitHub raw纯文本；未读F盘/上游图片，未改UI、图像、源码或Git。

## 数量结论

实际配置为 **3名角色 + 6个普通怪蓝图 + 2个Boss = 11个身体身份**。当前已有9个本项目原创静态身份（3角色、4普通、2Boss），普通近战三档中至少还缺2个可辨外观；11组真实原创walk循环均未交付。不能以四种普通行为代替六个普通蓝图，也不能把旧F来源408帧计入本批原创动作。

三档近战的walk分别引用不同纹理GUID，数值也不同；不增加elite玩法，但完整美术应保留三档视觉区分。

## 身份与主图映射

| 源蓝图 | 项目身份/提案 | 静态 | walk |
|---|---|---|---|
| Main Character Blueprint.asset | hero_daotong | existing-original-technical-and-visual-accepted-prior-batch | missing-original-walk-loop |
| Test Character Blueprint 1.asset | hero_lingyi | existing-original-technical-and-visual-accepted-prior-batch | missing-original-walk-loop |
| Test Character Blueprint 2.asset | hero_leixiu | existing-original-technical-and-visual-accepted-prior-batch | missing-original-walk-loop |
| 初級小兵.asset | orig_mob01 | existing-original-accepted-prior-batch | missing-original-walk-loop |
| 中級小兵.asset | new_melee_grade2 | missing-distinct-original-static-identity | missing-original-walk-loop |
| 高級小兵.asset | new_melee_grade3 | missing-distinct-original-static-identity | missing-original-walk-loop |
| 射擊小兵.asset | orig_mob02 | existing-original-accepted-prior-batch | missing-original-walk-loop |
| Boomerang Monster.asset | orig_mob03 | existing-original-accepted-prior-batch | missing-original-walk-loop |
| Gravity Monster.asset | orig_mob04 | existing-original-accepted-prior-batch | missing-original-walk-loop |
| Mini Boss.asset | orig_boss_minor | existing-original-accepted-prior-batch | missing-original-walk-loop |
| Final Boss.asset | orig_boss01 | existing-original-accepted-prior-batch | missing-original-walk-loop |

上述普通怪映射保留原批“四类行为顺序”为明确提案；原批没有Unity绑定证明。父制作窗口可调整具体角色与蓝图绑定，但缺两套普通怪的数量不受影响。主图绝对路径与SHA逐项见JSON。

## 波次与能力

Level1与TestLevel均包含相同6普通怪+2Boss。普通怪扁平顺序：初级近战、中级近战、高级近战、直射、回旋、抛投。0/30秒主出初级；150秒混中级；210秒混高级；360秒直射、420秒回旋、480秒抛投，540秒六类混合；小Boss300秒，终Boss600秒。完整每段概率与生命增幅以源配置和JSON为准，测试关仅调速/掉落等不新增身体类型。

能力图标已经19类候选池+2类额外初始能力=21张。源prefab/类与实际行为逐项保留；共用类不意味着共用图标。近战实体挥刺、发射器转向、飞行/回旋/抛物/投射物自转是后续Unity逻辑，不强制新增身体动作或飞行动画帧。

## 拾取与宝箱

经验4档（白1、蓝2、绿10、红50），钱5档（铜1、银2、金5、小袋30、大袋50），另4类消耗品。四种宝箱蓝图复用完全相同的closed/opening/open三个sprite引用，现有原创三态可共用，不需要因蓝图数4再画12张；源开箱是三态+代码缩放，不把额外完整动画当必需缺项。

## 动作与特效边界

每身份只硬性要求walk序列；停走用首帧，左右flipX。主角0.1秒/帧、普通近战与直射/两Boss0.2秒/帧、回旋及抛投0.15秒/帧是源示例，后续可按原创动作节奏调整并记录。独立run、idle、attack、cast、hurt、倒地身体序列不是源码必做。受击是白材质短闪；死亡是粒子/隐藏/回池或主角wipe，不以静态平移假装walk。

爆裂与火区在原项目为粒子/单Sprite缩放；本项目6阶段图集是原创替代方案，必须按实际播放验收。回血/吸血/DoT没有专属光环调用，属于可选增强。通用命中、发射、燃烧、死亡可共用云瓣/星火/玉叶/火舌等粒子；冲锋预警使用独立条纹素材。

## 补核的精确敌弹绑定

- `581c3629592bd4e348262df2e1facc62` → `Assets/Prefabs/Projectiles/Throwables/Gravity Well.prefab`（纯文字meta匹配；未读该prefab的图像）。
- `05da18cc29e0549b094ccd6c62ca69e5` → `Assets/Prefabs/Projectiles/Bullet.prefab`（纯文字meta匹配；未读该prefab的图像）。
- `1f463c2ded0b041a385a6795f9026ebe` → `Assets/Prefabs/Projectiles/Boomerangs/Enemy Boomerang.prefab`（纯文字meta匹配；未读该prefab的图像）。
- `92e4859746b3543d3979816ed1293839` → `Assets/Prefabs/Projectiles/Throwables/Boss Grenade.prefab`（纯文字meta匹配；未读该prefab的图像）。
- `6661e2369349241e8a016e87a4ff8c57` → `Assets/Prefabs/Projectiles/Shotgun Pellet.prefab`（纯文字meta匹配；未读该prefab的图像）。

Gravity Monster实际prefab已确认绑定`GravityThrowable.cs`，落地激活独立`gravityWell`与`wellParticles`，所以引力投掷本体之外，还必须有地面引力井视觉；范围伸缩由源码驱动，不硬性要求逐帧动画。确证来自该prefab的script GUID与同commit脚本meta，不再是仅凭蓝图名推断。详细脚本证据见JSON。

## 验收结论

本审计没有生成或验收任何新图、角色动作或Unity工程。它只固定全量范围与缺项。现有静态/图标/战斗资产文件哈希已核实，不能将“文件存在”写成玩法接入或动作通过。全游戏美术尚未完成。

补充验收：11个身份源序列均4帧引用，三档近战纹理GUID各不同；这只是源示例，不是已制作帧数。MainMenu确实列出上述3个角色蓝图。演员/弹体阴影与全屏白闪等基础辅助纹理也要在最终包给出共用资源或明确shader/基础primitive方案，不能遗漏；伤害数字保持文字。
