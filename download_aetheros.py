#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AetherOS 安装包下载器
=====================
功能：
  1. 每次运行时联网校验仓库里的最新版本；
  2. 若发现比本地已安装版本更新，则自动拉取分卷；
  3. 下载完成后自动合并为一个完整的 APK；
  4. 用 SHA-256 校验完整性，确保合并结果无误。

仅依赖 Python 3 标准库，跨 Windows / macOS / Linux。
用法：
  python3 download_aetheros.py            # 检查并在有更新时下载合并
  python3 download_aetheros.py --force    # 忽略本地版本，强制重新下载
  python3 download_aetheros.py --check    # 仅检查是否有更新，不下载
  python3 download_aetheros.py --out 目录 # 指定输出目录（默认当前目录）
说明：
  若所在网络访问 GitHub 受限，可设置系统代理后运行，例如：
  Linux/macOS:  export HTTPS_PROXY=http://127.0.0.1:7890
  Windows(cmd): set HTTPS_PROXY=http://127.0.0.1:7890
  Windows(pwsh): $env:HTTPS_PROXY="http://127.0.0.1:7890"
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.request

# ===== 仓库配置（按需修改）=====
REPO_OWNER = "sitong-zhang"
REPO_NAME = "AetherOS-Release"
BRANCH = "main"
# ==============================

VERSION_URL = (
    f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/version.json"
)
CACHE_FILE = ".aetheros_installed_version"

CHUNK = 1024 * 1024  # 1 MiB


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "aetheros-downloader"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def local_version():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""
    return ""


def save_local_version(v):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(v)
    except Exception:
        pass


def download_file(url, dest, label):
    req = urllib.request.Request(url, headers={"User-Agent": "aetheros-downloader"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        total = int(resp.headers.get("Content-Length", 0) or 0)
        downloaded = 0
        with open(dest, "wb") as out:
            while True:
                buf = resp.read(CHUNK)
                if not buf:
                    break
                out.write(buf)
                downloaded += len(buf)
                if total:
                    pct = downloaded * 100 // total
                    bar = "#" * (pct // 4)
                    sys.stdout.write(
                        f"\r  {label}: [{bar:<25}] {pct:3d}% "
                        f"({downloaded//1024//1024}/{total//1024//1024} MiB)"
                    )
                    sys.stdout.flush()
    sys.stdout.write("\n")
    return downloaded


def merge_parts(parts, out_path):
    written = 0
    with open(out_path, "wb") as out:
        for p in parts:
            with open(p, "rb") as f:
                while True:
                    buf = f.read(CHUNK)
                    if not buf:
                        break
                    out.write(buf)
                    written += len(buf)
    return written


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            buf = f.read(CHUNK)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="AetherOS 安装包下载合并工具")
    parser.add_argument("--force", action="store_true", help="强制重新下载")
    parser.add_argument("--check", action="store_true", help="仅检查更新")
    parser.add_argument("--out", default=".", help="输出目录（默认当前目录）")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    print("> 正在校验仓库最新版本 ...")
    try:
        manifest = fetch_json(VERSION_URL)
    except Exception as e:
        print(f"[错误] 无法读取版本信息：{e}")
        print("  若网络访问 GitHub 受限，请设置 HTTPS_PROXY 后重试。")
        sys.exit(1)

    latest = manifest.get("version", "")
    tag = manifest.get("tag", f"v{latest}")
    parts = manifest.get("parts", [])
    expect_sha = manifest.get("sha256", "")
    expect_size = manifest.get("size", 0)

    print(f"  最新版本：{latest}  (发布于 {manifest.get('updated', '未知')})")
    print(f"  本地版本：{local_version() or '未安装'}")

    if args.check:
        if latest != local_version():
            print("> 发现可用更新，运行不带 --check 的参数即可下载。")
        else:
            print("> 当前已是最新版本。")
        return

    if latest == local_version() and not args.force:
        print("> 当前已是最新版本，无需下载。如需重下可加 --force。")
        return

    print(f"> 开始下载 {len(parts)} 个分卷并合并 ...")
    part_paths = []
    try:
        for i, name in enumerate(parts, 1):
            url = (
                f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
                f"/releases/download/{tag}/{name}"
            )
            dest = os.path.join(args.out, name)
            print(f"  分卷 {i}/{len(parts)}: {name}")
            download_file(url, dest, f"卷{i}")
            part_paths.append(dest)

        out_name = f"AetherOS-{latest}.apk"
        out_path = os.path.join(args.out, out_name)
        print(f"> 合并为 {out_name} ...")
        size = merge_parts(part_paths, out_path)
        print(f"  合并完成，大小 {size} 字节")

        if expect_sha:
            print("> 校验完整性 (SHA-256) ...")
            actual = sha256_file(out_path)
            if actual.lower() != expect_sha.lower():
                print(f"[错误] 校验失败！\n  期望 {expect_sha}\n  实际 {actual}")
                sys.exit(1)
            print("  校验通过，文件完整。")

        save_local_version(latest)
        print(f"\n[完成] 安装包已生成：{out_path}")
        print("  请通过『设置 → 允许未知来源应用』或 adb install 安装。")
    except Exception as e:
        print(f"[错误] 下载或合并失败：{e}")
        sys.exit(1)
    finally:
        # 清理分卷，仅保留合并后的 APK
        for p in part_paths:
            try:
                os.remove(p)
            except Exception:
                pass


if __name__ == "__main__":
    main()
