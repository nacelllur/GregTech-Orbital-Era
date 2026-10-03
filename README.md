<div align="center">

# 格雷科技：星环纪元
### GregTech: Orbital Era

**Minecraft 1.20.1 · Forge 47.4.18 · 88 Mods**

格雷科技深空工业整合包 · 太空主题主菜单美化版

</div>

---

## 简介

「星环纪元」是一个以 **GregTech CEu Modern (GTCEu 7.5.3)** 为核心的 Minecraft 1.20.1 工业整合包，融合了应用能源 2、末影 IO、植物魔法、Ad Astra 太空探索等模组，围绕**深空工业**主题打造长期沉浸式科技生存体验。

整合包自带全套 **FancyMenu 太空 HUD 主菜单美化**——从标题界面到设置页、世界选择、加载界面，全部统一为青色科技 HUD 风格。

## 环境要求

| 项目 | 要求 |
|---|---|
| Minecraft | 1.20.1 |
| 加载器 | Forge 47.4.18 |
| Java | 17（推荐 17.0.8+） |
| 内存 | 最低 6GB，推荐 8GB+ |
| 显存 | 2GB+（使用光影时 4GB+） |

## 安装指南

### 方式一：从 GitHub 克隆（推荐）

```bash
git clone https://github.com/nacelllur/GregTech-Orbital-Era.git GT-New
```

将克隆下来的文件夹放到你的 Minecraft 启动器实例目录中（如 HMCL / Prism Launcher / PCL2）。

**然后还需一步**：前往 [Releases](../../releases) 页面下载 **`GTOE-third-party-mods-*.zip`** 附件
（第三方 86 个 mod，体积 235MB，因仓库体积限制不入库），解压到 `mods/` 文件夹。
自研 mod（`gtoecore` / `packcompanion`）已随仓库自带，无需重复放置。

最后用启动器安装 **Forge 1.20.1-47.4.18**，启动游戏即可。

### 方式二：下载 Release 完整压缩包

前往 [Releases](../../releases) 页面下载完整压缩包（含全部 mod），解压到启动器实例目录即可。

## 整合包亮点

- **格雷科技 CEu Modern 7.5.3**：完整的电压等级体系（LV → UV → MAX），数百台机器与多方块结构
- **应用能源 2 + 扩展**：ME 网络、自动合成、量子存储
- **Ad Astra 太空探索**：月球、火星、金星、水星——真正的深空工业
- **FancyMenu 全局 HUD 美化**：22 个界面统一太空主题
- **中文优化**：JEI 搜索中文支持、汉字显示修复
- **性能优化**：Embeddium + Oculus，中低端机器也能流畅运行

## 目录结构

```
GT-New/
├── mods/              # 仅自研 mod（gtoecore / packcompanion）；第三方 86 个走 Releases 附件
├── config/            # 全部 mod 配置（含 FancyMenu 美化）
│   └── fancymenu/     # 主菜单 HUD 贴图与布局
├── defaultconfigs/    # 默认配置
├── options.txt        # 游戏设置（含全局按钮/滑杆皮肤）
├── shaderpacks/       # 7 款光影包
├── tlm_custom_pack/   # 东方女仆自定义包
└── schematics/        # 建筑蓝图
```

> **为什么 mods 里只有两个 jar？** 第三方 mod 合计 235MB，放在 git 里会让仓库膨胀近 10 倍、clone 极慢。
> 因此改走 Releases 附件分发（见上方安装指南），仓库只保留自研 mod（271KB）以便追踪版本。

## FancyMenu 美化说明

整合包使用 FancyMenu 3.9.6 实现全局界面美化：

- **主菜单**：地球夜景背景 + 青色 HUD 按钮 + 三层标题排版
- **世界选择页**：HUD 面板 + 地球背景
- **设置/暂停/死亡等 22 个界面**：统一太空背景 + 页签标识
- **加载界面**：泥土背景替换为地球夜景
- **全局按钮/滑杆皮肤**：所有原版按钮统一 HUD 风格

美化资产位于 `config/fancymenu/assets/`，布局文件位于 `config/fancymenu/customization/`。

> 如需修改配色，编辑 `orbital-menu/gen_assets.py` 中的颜色值后重新运行即可。

## 协作指南

欢迎好友通过 Pull Request 贡献内容：

1. **克隆仓库**到本地
2. 创建分支：`git checkout -b feature/your-feature`
3. 提交改动：`git commit -m "描述你的改动"`
4. 推送分支：`git push origin feature/your-feature`
5. 在 GitHub 上发起 **Pull Request**

### 常见协作场景

- **添加新 mod**：把 `.jar` 放入 `mods/`，如有配置则放入 `config/`
- **调整配方**：修改对应 mod 的配置文件
- **更新 FancyMenu 美化**：修改 `config/fancymenu/` 下的布局文件
- **添加光影**：放入 `shaderpacks/`

## 致谢

- [GregTech CEu Modern](https://github.com/GregTechCEu/GregTech) — 核心科技模组
- [FancyMenu](https://github.com/Keksuccino/FancyMenu) — 界面美化框架
- [Applied Energistics 2](https://github.com/AppliedEnergistics/Applied-Energistics-2) — 物品网络
- [Ad Astra](https://github.com/terrarium-earth/Ad-Astra) — 太空探索
- 以及所有前置模组的开发者们

## License

本整合包的配置与美化资产采用 [MIT License](LICENSE)。

模组文件版权归各自作者所有，请遵循各模组的开源协议。
