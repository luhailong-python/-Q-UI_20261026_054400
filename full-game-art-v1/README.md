# 道家Q版全游戏美术收口

**当前完整交付已合并Logo：242张正式图片、131张设计图、11组44帧动作。** [统一交付说明](docs/COMPLETE_DELIVERY.md) · [统一完整ZIP](delivery/yifu_zhen_wanyao_complete_art_20261029.zip)。下方235张/旧ZIP为上一批次记录，继续保留。

游戏中文名已定为 **《一符镇万妖》**。新制作的透明Logo与符印徽记见 [品牌补充包](branding-v1/README.md)；此前131张UI原图继续保留。

当前固定范围已完成美术验收：**235张正式图片、131张横竖设计/状态图、11身份44帧原创行走**。131张既有UI与原E盘图逐字节一致。最终判定见 [验收记录](docs/ACCEPTANCE.md) 与 `records/final-acceptance.json`；后者 `allGameArtComplete=true` 只表示本次美术范围。

- [独立完整ZIP](delivery/dao_full_game_art_20261028.zip)（SHA在同名 `.zip.sha256`；逐文件校验在 `records/delivery-package.json`）
- [预览入口](previews/index.html) · [11身份动作总览](previews/all-actors-walk-contact.jpg)
- [正式资源清单](assets/asset-list.csv) · [Unity导入建议](docs/UNITY_IMPORT.md)

动作是4姿势分格循环，不是图生视频；轻微原画差异和1254²地面视觉重复限制已在验收记录公开。Unity接入、设备验证与Git上传按约定留下一阶段。

本目录统一承接本对话全部已采用美术。功能基线为VampireSurvivorsClone固定commit的实际配置：1个可玩生存战斗场景、3名角色、6种普通怪、2个Boss、21类能力、4档经验、5档钱币、4类消耗品、共用宝箱三态，以及已确认的任务等演示扩展。正式项目远端未提供；不提交或上传Git。

现有109张UI及后来新增22张功能图共131张保持原像素、原样式。其当前必要控件及图鉴缩略图仅为保持旧UI而从本对话E盘已有成果复制；新游戏人物、怪物、动作、物件、场景及特效没有重新读取或使用F盘/上游图片。

| 内容 | 位置 |
|---|---|
| 全量资源清单、来源映射、尺寸、Pivot及Border | `records/final-resource-manifest.json`、`assets/asset-list.csv` |
| 131张冻结界面 | `designs/preserved/`、`designs/functional/` |
| 保留UI、原创基础素材、21能力图标、战斗物件 | `assets/final/` |
| 两种新增近战怪、头像和目标缩略图 | `assets/actors/`、`assets/portraits/`、`assets/targets/` |
| 战斗地面及重复采样数据 | `assets/environment/`、`assets/technical/` |
| 引力井、方向标记、阴影、白闪基础图 | `assets/effects/`、`assets/utility/` |
| 行走原画与正式帧（完成数以最终验收为准） | `assets/motion-native/`、`assets/motion/` |
| 字体文件、SIL OFL及版权通知 | `assets/fonts/`、`docs/FONTS.md` |
| 逐图提示词、真实参数和来源 | `records/prompts/`、PNG旁`.generation.json`、`sources/` |
| 固定commit全量审计 | `docs/ACTOR_OBJECT_SCOPE.md`、`docs/ENVIRONMENT_UI_SCOPE.md` |
| 行走原画制作方法 | `docs/ANIMATION_METHOD.md` |
| 导入、切片及接入建议 | `docs/UNITY_IMPORT.md` |

只有最终验收记录明确`allGameArtComplete=true`时才能称全游戏美术完成；原画文件存在、静态图、工单或部分循环不能替代动作验收。Unity导入、材质、Prefab、场景、动画控制、业务逻辑及设备表现都留下一阶段，不在本次完成声明内。

新图使用宿主内置image_gen，配置目标`gpt-image-2.5-sunburst/max`；型号/质量选择器及真实返回未披露，实际字段未确认。来源原生图、AI编辑、切片、缩小、补边、基础几何及技术噪声分别记录，不把加工当新增原生细节。部分原图有Alpha1边像素；浅/深底实际合成判断可见边缘，不拿黑底显示的低Alpha RGB当透明失败。
