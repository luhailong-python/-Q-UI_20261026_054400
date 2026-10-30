# 一符镇万妖 · Unity资源接入工程 v1

当前已进入原约定的下一阶段。工程目标是把已验收美术变成Unity可用的Sprite、动画、Prefab和可操作审片场景。本批不把美术预览页面冒充游戏，也不将接入预览说成已实现生存战斗业务。

## 已落盘

- 242张正式PNG已复制到 `Assets/Resources/DaoArt/`，逐文件SHA与美术统一清单一致。
- 11身份/44帧的动作与静态尺度、真实Pivot、逐帧时长、9宫格Border已转成 `Assets/Resources/DaoArtCatalog.json`。
- 两套中文字体及OFL已复制；运行预览用包内Noto CJK，不依赖Windows系统字体。
- `DaoArtImporter.cs`：Sprite/透明/原生尺寸/PPU128/九宫格，地面与噪声分开按Repeat Texture导入。
- `DaoProjectBuilder.cs`：Unity首次编译导入后生成11个Actor Prefab、11个Animator Controller、11个Walk和11个停走首帧Clip，以及1个ArtIntegration场景。
- `ArtIntegrationPreview.cs`：原风格主标和三名角色选择、全部11动作正常/半速预览、WASD/方向键/触屏拖动移动、停走与左右翻转、相机跟随和重复地面。

**生成器尚未在Unity中执行，所以未声称Prefab/Clip/场景已经生成。** 编辑器输出会写入 `IntegrationReports/editor-import.json`，只有真实运行后才有该报告；磁盘准备记录与C#语法检查不等于Unity编译或播放通过。

## 本机环境与打开方法

Hub记录的版本为6000.4.5f1（Unity6.4），工程按该兼容基线准备；`E:\u3d\6000.4.5f1` 当前只有安装记录，没有Editor/Unity.exe，Hub可执行程序记录也已失效。需要一个实际可运行的Unity6编辑器才能继续验证。若安装在其他目录，直接用其打开本工程。

1. 在Unity Hub中添加本目录 `unity-project-v1`。
2. 等待Packages与C#完成导入。首次自动执行生成器；也可用菜单“一符镇万妖 → 生成资源接入场景与预制体”。
3. 打开生成的 `Assets/Scenes/ArtIntegration.unity`，按Play，检查选角、全身份动作、半速和移动页。
4. 横向1920×1080、竖向1080×1920分别检查；真实设备与Safe Area仍需后续验收。

批处理入口（将路径替换为真实Unity.exe）：

```powershell
& '实际编辑器目录\Unity.exe' -batchmode -quit -projectPath 'E:\work\image\道家Q版UI_20261026_054400\unity-project-v1' -executeMethod YifuArt.Editor.DaoProjectBuilder.BuildAndValidate -logFile 'E:\work\image\道家Q版UI_20261026_054400\unity-project-v1\IntegrationReports\unity-batch.log'
```

## 当前未完成的下一阶段工作

真实Unity编译/导入与播放、场景视觉复核、移动端触控/旋转/设备表现。之后再接入怪物波次与伤害、经验/掉落/升级选卡、能力实现、Boss、任务与原UI业务状态、存档和完整胜负闭环。本批代码只有资源接入审片，不含上述战斗业务。

本次C#与工程设置为本项目新写；没有复制上游图片、代码或第三方场景。原美术与131张设计图保持不变。Git仅版本化源文件与美术，Library/Temp/Obj/Logs/本地构建/工具bin、obj必须忽略，LFS缓存可在远端验证后清理。
