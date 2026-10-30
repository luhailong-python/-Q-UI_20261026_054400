# 动态中文字体交付

本批补充未来Unity动态文字的可再分发字体，不修改已确认UI成图。两份字体均从官方仓库固定commit下载，原字节未修改，无系统安装，无Windows或F盘字体复制。字体文件合计22,295,300字节，小于25MB。

| 用途 | 文件 | 来源与版本 | 字节 | SHA256 |
|---|---|---|---:|---|
| 正文、数字、姓名、英文、简繁中文 | `assets/fonts/noto-cjk-sc/NotoSansCJKsc-Regular.otf` | [notofonts/noto-cjk固定commit](https://github.com/notofonts/noto-cjk/blob/165c01b46ea533872e002e0785ff17e44f6d97d8/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf) | 16,437,364 | `2c76254f6fc379fddfce0a7e84fb5385bb135d3e399294f6eeb6680d0365b74b` |
| 可选装饰标题 | `assets/fonts/ma-shan-zheng/MaShanZheng-Regular.ttf` | [GoogleFonts固定commit](https://github.com/google/fonts/blob/406197b91ff39a93061c2c2eeaee67ddf2ae1f0d/ofl/mashanzheng/MaShanZheng-Regular.ttf) | 5,857,936 | `6d2546bb189c732a8ca29af9e22457b152387d158aa459e4ac2ce1e51788b7fb` |

两字体随各自目录交付完整`OFL.txt`、`NOTICE-FONT-METADATA.txt`。官方许可为[SIL OFL1.1 · Noto](https://raw.githubusercontent.com/notofonts/noto-cjk/165c01b46ea533872e002e0785ff17e44f6d97d8/LICENSE)及[SIL OFL1.1 · MaShanZheng](https://raw.githubusercontent.com/google/fonts/406197b91ff39a93061c2c2eeaee67ddf2ae1f0d/ofl/mashanzheng/OFL.txt)。可随软件打包、嵌入和再分发，须保留许可与版权通知，不单独出售字体，字体软件本身继续适用OFL；本包未修改字形或名称。

## 实际覆盖检查

读取29份现存布局/内容记录，抽取3349个文本值，加入可打印ASCII、常见简繁样本及新怪物名称，共746个可见字符。正文缺字0，正文加标题回退后缺字0；标题字体单独缺32个字符，完整清单见`records/font-sources.json`的`titleMissing`。正文通过此次项目实际文案和样本覆盖检查。

现有Python入口未安装fontTools，遵守不安装要求，使用标准库直接读取字体SFNT的Unicode cmap4/12并排除glyphID0；保留方法与字库计数。实际排版预览使用Pillow/FreeType直接加载下载字体，见`assets/fonts/font-preview.png`。这不是OCR替换现有图片，也未把字体工具或许可当成Unity验证。

## 后续Unity建议

正文默认Noto Sans CJK SC Regular；Ma Shan Zheng只用于全部字符均有覆盖的标题；只要出现缺字，优先整条标题回退正文，以免书写体与黑体混排。逐字fallback仅作技术兜底，不作为唯一动态或繁体字体。SC字体覆盖已测繁体码位，但并不等于默认采用台湾/香港地区偏好的所有字形，地区字形需求可在正式本地化阶段另行指定。玩家自由输入的全部Unicode字符超出此次有限语料验收范围。

可在后续TextMeshPro按实际文案生成静态图集，动态姓名/新文案使用动态字库及正文fallback。采样尺寸、SDF padding、图集容量和设备内存须实际Unity接入验证，本阶段只提供字体、许可、字集与排版样张。正文与标题字体不直接烘焙进已有UI图片。
