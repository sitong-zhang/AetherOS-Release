# AetherOS 安装包分发仓库

本仓库用于分发 **AetherOS** 的 Android 安装包（APK）。由于安装包体积较大（约 3.8 GB），超过了常规单文件托管的大小限制，这里采用「分卷 + 下载器」的方式，让你无需手动拼接即可拿到完整可用的安装包。

## 这是什么

- **AetherOS**：一个运行在 Android 上的系统级试验台，内置可启动的 Linux 环境，提供桌面、应用商店等系统能力。
- 本仓库只负责**分发**安装包，不含源码（源码在另一个工程仓库）。

## 为什么要分卷

单一文件约 3.8 GB，直接托管会遇到平台单文件大小上限。因此安装包被拆分为 3 个分卷（`.001` / `.002` / `.003`），下载后再合并回一个完整 APK。合并是简单的顺序拼接，不会产生任何信息损失。

## 快速开始（推荐：用下载器）

下载器会**每次运行时联网检查仓库里的最新版本**；若发现比本地已安装版本更新，就自动拉取全部分卷、自动合并、并做完整性校验。

1. 安装 [Python 3.8+](https://www.python.org/)（Windows / macOS / Linux 均支持）。
2. 把本仓库的 `download_aetheros.py` 和 `version.json` 下载到同一目录。
3. 在该目录打开终端，运行：

   ```bash
   python3 download_aetheros.py
   ```

   常用参数：

   | 参数 | 作用 |
   | --- | --- |
   | （无参数） | 检查版本，有更新则下载并合并 |
   | `--force` | 忽略本地版本，强制重新下载 |
   | `--check` | 只检查是否有更新，不下载 |
   | `--out 目录` | 指定输出目录（默认当前目录） |

4. 运行结束后会生成 `AetherOS-<版本号>.apk`，并提示校验通过。

## 安卓下载器 App（推荐，最省事）

如果你直接在手机上操作，用安卓版下载器 App 最方便：不用装 Python，打开点一下就自动下载合并。

1. 到本仓库的 **Releases** 页下载 **`AetherOS-Downloader.apk`** 并安装（安装时按系统提示允许「未知来源应用」）。
2. 打开桌面上的「下载器」App。
3. 点「下载并合并」：App 会先**自动测速选出当前最快的下载镜像**，再依次下载 3 个分卷、后台自动合并成 `AetherOS-<版本>.apk`，并完成 SHA-256 校验；合并完成后点「安装 APK」即可。

> 为什么不用你手动配代理：国内直连 GitHub 常常卡住或超时。App 内置了一批 GitHub 加速镜像，启动时会并发测速择优使用；下载过程中若某个镜像中断，会自动切换到下一个，并支持断点续传，基本无需你干预。

## 手动方式（不使用下载器）

如果你不想运行脚本，也可以手动完成：

1. 到本仓库的 **Releases** 页面，下载 3 个分卷：
   - `AetherOS-2.0.2.apk.001`
   - `AetherOS-2.0.2.apk.002`
   - `AetherOS-2.0.2.apk.003`
2. 按顺序合并为一个文件：

   ```bash
   # Linux / macOS
   cat AetherOS-2.0.2.apk.001 AetherOS-2.0.2.apk.002 AetherOS-2.0.2.apk.003 > AetherOS-2.0.2.apk

   # Windows (cmd)
   copy /b AetherOS-2.0.2.apk.001 + AetherOS-2.0.2.apk.002 + AetherOS-2.0.2.apk.003 AetherOS-2.0.2.apk
   ```
3. 合并后的 `AetherOS-2.0.2.apk` 即为完整安装包。

## 校验完整性（可选）

合并完成后，可核对 SHA-256 是否与 `version.json` 中的 `sha256` 字段一致：

```bash
# Linux / macOS
sha256sum AetherOS-2.0.2.apk

# Windows (PowerShell)
Get-FileHash -Algorithm SHA256 AetherOS-2.0.2.apk
```

预期值：`4536764819f2edb6f054c0af453808b26e6f7d4760dec153b80a623c271b6fe7`

## 安装

- **方式一**：把 APK 传到手机，在「设置 → 安全 → 允许安装未知来源应用」开启后点击安装。
- **方式二**：通过电脑用 adb 安装：

  ```bash
  adb install AetherOS-2.0.2.apk
  ```

## 网络说明

若你的网络访问 GitHub 受限，下载器支持系统代理（自动读取 `HTTPS_PROXY` 环境变量）。设置代理后再运行脚本即可：

```bash
# Linux / macOS
export HTTPS_PROXY=http://127.0.0.1:7890
python3 download_aetheros.py

# Windows (PowerShell)
$env:HTTPS_PROXY="http://127.0.0.1:7890"
python3 download_aetheros.py
```

## 当前版本

| 版本 | 大小 | 说明 |
| --- | --- | --- |
| 2.0.2 | ~3.8 GB | 修复系统返回键退出应用商店、修复商店下载进度卡在 0% |

## 免责声明

本安装包仅供个人测试与研究使用。安装与使用前请确认设备已做好数据备份，作者不对使用过程中的任何数据丢失或设备损坏负责。
