![WeiDU v251 for Android arm64](https://raw.githubusercontent.com/NightBreather/weidu-android/main/docs/banner.png)

# WeiDU v251 for Android (arm64 / Termux) — prebuilt native binaries

Hi everyone,

I couldn't find a recent WeiDU build that runs on modern Android, so I built the
latest stable release (**v251.00**) natively on-device — no PC, no proot, no Wine.
Sharing it in case it's useful.

**What it is**
A native **arm64 Android ELF** build of WeiDU (the same tool used on desktop to
install Infinity Engine mods), running inside **Termux**. It installs mods directly
against the game data folder.

**Download**
<https://github.com/NightBreather/weidu-android>

Contents: `weidu`, `weinstall`, `tolower` (all 25100), plus a reproducible build script.

---

## Install

Download the repo, then in Termux:

```bash
cp bin/weidu bin/weinstall bin/tolower "$PREFIX/bin/"
chmod 755 "$PREFIX/bin/weidu" "$PREFIX/bin/weinstall" "$PREFIX/bin/tolower"
weidu --version
```

![terminal](https://raw.githubusercontent.com/NightBreather/weidu-android/main/docs/terminal.png)

## Usage

Run it from the game directory (the folder that contains `chitin.key`):

```bash
cd /path/to/game
weidu /path/to/setup-my-mod.tp2 --language 0 --force-install-list 0
```

Or with the shortcut wrapper:

```bash
weinstall my-mod --language 0 --force-install-list 0
```

---

## How it's built (on the phone)

![toolchain](https://raw.githubusercontent.com/NightBreather/weidu-android/main/docs/toolchain.png)

WeiDU still requires OCaml with "unsafe strings", and OCaml 5.x removed
`-unsafe-string`. So the toolchain is: OCaml 4.14.2 (from source) + Elkhound →
WeiDU v251.00 → arm64 Android ELF. Full recipe in `build/build-android.sh`.

## v249 → v251 highlights relevant to mobile / Linux

![features](https://raw.githubusercontent.com/NightBreather/weidu-android/main/docs/features.png)

- Linux builds no longer need `tolower` or a case-insensitive filesystem
- `ADD_KIT` / `COPY_KIT` understand filler lines in `KITLIST.IDS`
- `HANDLE_CHARSETS` infers Turkish and more languages
- `--force-install-list` warns on unknown component numbers
- New: `GET_RESOURCE_ARRAY`, `OUTER_SPRINTF`, `--unbiff`, …

---

**Notes / caveats**

- arm64 only (no 32-bit, no x86)
- `tolower` is included for completeness but is **not** for EE games — it even refuses on them
- Unofficial build, GPL-2.0; source is the upstream repo at tag v251.00

Feedback and test reports welcome.
