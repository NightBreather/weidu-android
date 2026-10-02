#!/usr/bin/env python3
"""Generate the forum-post images for the weidu-android repo using ffmpeg.

No ImageMagick / PIL needed; ffmpeg's drawtext/drawbox/gradients filters do
all the work. Fonts are taken from the Android system.

Usage:  python3 docs/make-images.py
Output: docs/banner.png, docs/terminal.png, docs/toolchain.png, docs/features.png
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(HERE, ".txt")
FB = "/system/fonts/DroidSans-Bold.ttf"
FR = "/system/fonts/DroidSans.ttf"
FM = "/system/fonts/DroidSansMono.ttf"

C_BG0 = "0x0b1020"
C_BG1 = "0x24306a"
C_ACC = "0x7fd1ff"
C_ACC2 = "0xffb454"
C_WHITE = "0xf5f7ff"
C_GRAY = "0xb8c0d0"
C_DIM = "0x7a8398"
C_GREEN = "0x5ee38a"
C_PANEL = "0x1b2236"
C_TERM = "0x1e1e2e"
C_TBAR = "0x313244"

_seq = [0]


def tfile(s: str) -> str:
    os.makedirs(TXT, exist_ok=True)
    _seq[0] += 1
    p = os.path.join(TXT, "t%03d.txt" % _seq[0])
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)
    return p


def dt(s, font, size, color, x, y, extra=""):
    return ("drawtext=fontfile=%s:textfile=%s:fontsize=%d:fontcolor=%s:"
            "expansion=none:x=%s:y=%s%s" % (font, tfile(s), size, color, x, y, extra))


def box(x, y, w, h, color, t="fill"):
    return "drawbox=x=%d:y=%d:w=%d:h=%d:color=%s:t=%s" % (x, y, w, h, color, t)


def grad(w, h, c0=C_BG0, c1=C_BG1):
    return ("gradients=s=%dx%d:c0=%s:c1=%s:x0=0:y0=0:x1=%d:y1=%d:nb_colors=2"
            % (w, h, c0, c1, w, h))


def solid(w, h, c):
    return "color=c=%s:s=%dx%d" % (c, w, h)


def render(name, src, filters):
    out = os.path.join(HERE, name)
    vf = ",".join(filters)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error",
           "-f", "lavfi", "-i", src, "-vf", vf, "-frames:v", "1", "-y", out]
    subprocess.run(cmd, check=True)
    print("wrote", name, os.path.getsize(out), "bytes")


# ------------------------------------------------------------------ banner
def banner():
    W, H = 1280, 480
    f = [box(0, 0, 12, H, C_ACC)]
    f += [
        dt("NightBreather / weidu-android", FM, 24, C_ACC, 64, 60),
        dt("WeiDU v251", FB, 110, C_WHITE, 60, 150),
        dt("for Android arm64  \u00b7  Termux", FB, 46, C_ACC2, 64, 292),
        dt("Install Infinity Engine mods on-device - no PC required", FR, 30, C_GRAY, 66, 366),
        dt("$ weidu --version   ->   WeiDU version 25100", FM, 27, C_WHITE, 66, 420,
           ":box=1:boxcolor=0xffffff@0.08:boxborderw=20"),
    ]
    render("banner.png", grad(W, H), f)


# ---------------------------------------------------------------- terminal
def terminal():
    W, H = 1280, 620
    f = [
        box(0, 0, W, H, "0x0a0e17"),
        box(40, 40, 1200, 520, C_TERM),
        box(40, 40, 1200, 52, C_TBAR),
        box(70, 59, 14, 14, "0xff5f56"),
        box(96, 59, 14, 14, "0xfebc2e"),
        box(122, 59, 14, 14, "0x28c840"),
        dt("weidu - Termux", FM, 22, "0xa6adc8", 560, 54),
    ]
    lines = [
        (130, C_GREEN, "$ weidu --version"),
        (172, C_GRAY,  "[weidu] WeiDU version 25100"),
        (236, C_GREEN, "$ weidu setup-my-mod.tp2 --language 0 --force-install-list 0"),
        (278, C_GRAY,  "Installing [My Mod]"),
        (320, C_GREEN, "SUCCESSFULLY INSTALLED      My Mod"),
        (384, C_GRAY,  "override/ synced to the game folder"),
        (440, C_GREEN, "$"),
    ]
    for y, c, s in lines:
        f.append(dt(s, FM, 26, c, 80, y))
    render("terminal.png", solid(W, H, "0x0a0e17"), f)


# --------------------------------------------------------------- toolchain
def toolchain():
    W, H = 1400, 520
    f = [dt("How it is built - fully on-device", FB, 42, C_WHITE, 60, 54)]
    labels = ["OCaml 4.14.2", "Elkhound", "WeiDU v251", "arm64 ELF", "Termux bin"]
    bw, bh, gap = 240, 120, 40
    total = len(labels) * bw + (len(labels) - 1) * gap
    x0 = (W - total) // 2
    yb = 210
    for i, lab in enumerate(labels):
        bx = x0 + i * (bw + gap)
        f.append(box(bx, yb, bw, bh, C_PANEL))
        f.append(box(bx, yb, bw, 6, C_ACC))
        f.append(dt(lab, FB, 30, C_WHITE, "%d+(%d-text_w)/2" % (bx, bw), yb + 44))
        if i < len(labels) - 1:
            ax = bx + bw + 6
            f.append(dt("->", FB, 30, C_ACC2, "%d+(%d-text_w)/2" % (ax, gap - 12), yb + 46))
    f += [
        dt("OCaml with unsafe strings  +  Elkhound parser generator", FR, 26, C_GRAY, 60, 400),
        dt("result: weidu / weinstall / tolower  (no proot, no glibc)", FM, 24, C_DIM, 60, 442),
    ]
    render("toolchain.png", grad(W, H), f)


# ---------------------------------------------------------------- features
def features():
    W, H = 1240, 560
    f = [box(0, 0, 12, H, C_ACC2),
         dt("What changed: v249  ->  v251", FB, 42, C_WHITE, 60, 50)]
    items = [
        "Linux: no more tolower / case-insensitive filesystem",
        "ADD_KIT and COPY_KIT understand KITLIST.IDS filler lines",
        "HANDLE_CHARSETS infers Turkish and more languages",
        "--force-install-list warns on unknown component numbers",
        "%MOD_FOLDER% is case-exact",
        "New: GET_RESOURCE_ARRAY, OUTER_SPRINTF, --unbiff",
    ]
    y = 150
    for it in items:
        f.append(dt(">", FB, 30, C_ACC, 64, y))
        f.append(dt(it, FR, 28, C_GRAY, 100, y - 2))
        y += 60
    render("features.png", grad(W, H, "0x0b1020", "0x1a2140"), f)


if __name__ == "__main__":
    banner()
    terminal()
    toolchain()
    features()
