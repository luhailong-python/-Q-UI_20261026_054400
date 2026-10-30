# 后续Unity导入建议

本次仅验收图片和美术合同，未运行Unity。所有实际尺寸、Alpha、Pivot和Border以`records/final-resource-manifest.json`与逐图派生记录为准。

## 正式图片与来源文件

`assets/final/`保存按字节复制的已采用资源；`assets/actors/portraits/targets/effects/utility/environment/technical/motion`保存本阶段新增正式资源。`assets/native/`、`assets/motion-native/`及`sources/`是原生母图/图集和溯源材料，不应一并自动加入运行时图集。文件数量不是独立原画数量；复用与派生明确标记。

保留UI与新功能图的原始布局记录保留原批次路径，统一`sourceToFinalResourceMap`给出源文件绝对路径到本包正式路径的映射。设计图是布局预览，不当整张Sprite代替独立控件。旧UI像素不改；源码行为以新增22张功能图与固定commit审计为准。

## Sprite与锚点

- UI控件：Sprite/Single，依清单Simple或Sliced；九宫格Border顺序为Left、Bottom、Right、Top，单位为对应源PNG像素。圆形卡头/标题牌不得当横向按钮皮肤硬拉伸；状态使用一致画布。
- 能力图标：384²、中心Pivot、Border0、Simple等比显示；业务中文和数值独立Text/TMP。既有天雷符固定朱砂装饰印记另行标注。
- 战斗小物/粒子/拾取物：通常256²；武器与发射器512×256，已标物理握点建议。预警笔触512×128，默认中心Pivot；源Charge的根点/长度缩放逻辑接入时应按实际prefab再核实，不以单张图宣称行为已绑定。
- 角色/怪物：静态1024²，脚根左上坐标(512,896)、Unity归一化Pivot(0.5,0.125)。正式行走每身份统一画布和缩放，按真实接地面/躯干注册，漂浮灯笼使用固定身体挂点；具体元数据和逐帧时长见clip.json。
- 爆裂/火区：各6帧512²，分别530ms一次与660ms循环，Pivot分别(0.5,0.5)/(0.5,0.3125)。这是本项目手绘阶段替换方案，原源码没有强制6帧要求。PNG序列和APNG用于美术交接，控制与播放由下一阶段实现。
- 引力井：512²中心Pivot，覆盖GravityThrowable实际落地井槽；不能把普通爆裂动画当引力井。方向环256²中心。阴影512×256透明，原图最高Alpha133，若需更浅可用实例颜色Alpha，未在设备验证。
- 白闪4²纯白为基础几何，不是AI画作；按源全屏Sprite/淡出语义接入。伤害数字保持文字。

上述Pivot均建议，SpriteRenderer/Sorting/碰撞/特效范围与像素世界比例需要真实工程验证。可先以统一PPU和清单身高比例做角色/普通怪/Boss对照，不凭预览像素直接认定世界单位。

## 纹理与透明

透明Sprite建议Full Rect、Bilinear、Clamp、关闭Mipmap、开启Alpha Is Transparency。Max Size至少容纳实际源画布；初验无压缩，再按目标平台比较压缩与边缘。压缩、显存、帧率、Safe Area和移动设备未测试。

战斗地面为原生1254²不透明纹理，建议Default/Repeat U,V/Bilinear；未放大为2048。3×3视觉平铺已审，对边不是逐像素相同，详细差值/阈值见`records/ground-tile-review.json`。源InfiniteTile材质允许世界偏移混合，需后续用实际Shader确认世界缩放、反重复、磁铁Shockwave、Mip与压缩。

256²噪声是确定性PRNG技术数据，应按数据用途检查sRGB/Linear设置（建议Linear）；不是手绘地面，不复制上游WhiteNoise像素。源shader参数4.5只作功能证据，未在本项目Unity验证。

## 文字与许可

运行时正文采用包内Noto Sans CJK SC，装饰标题可用Ma Shan Zheng。标题缺字时整条回退正文；已有PNG不会因此重绘。实际语料覆盖/缺字和两套OFL、版权通知见`docs/FONTS.md`与`records/font-sources.json`，不分发Windows微软雅黑或楷体字体文件。

## 状态与逻辑边界

源身体动作最小为walk，停走沿用静态首帧、左右flipX；受击白材质、死亡粒子/隐藏、宝箱三态的代码缩放无需另外强制body hurt/run/倒地片。行走动作使用逐姿势独立AI原画，不称I2V、连续视频或8方向动作。完整游戏美术验收仍需全部11身份循环实际播放通过。

自动攻击、弹道/重力、投射物旋转、环绕/回旋、武器挥刺、伤害与击退、生成/掉落、解锁/存档/本地化、按钮点击及UI状态切换均由后续Unity接入承担。本轮没有C#、Prefab、Scene、网页游戏替代或Git发布。
