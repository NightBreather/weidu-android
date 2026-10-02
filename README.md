# WeiDU for Android (Termux) — native arm64 build

> Türkçe: [README.tr.md](README.tr.md)

Unofficial **native Android (aarch64 / arm64-v8a)** builds of
[**WeiDU v251.00**](https://github.com/WeiDUorg/weidu/releases/tag/v251.00) —
the tool used to create, distribute and install mods for Infinity Engine games
(Baldur's Gate: Enhanced Edition, BG2:EE, IWD:EE, PST:EE, …).

These are built **on-device in Termux** with OCaml 4.14.2 and the Android NDK
toolchain. No emulation, no `proot`, no glibc — they are real Android ELF
binaries that run under Termux's `$PREFIX`.

> **Status:** built and smoke-tested on BGEE Android (Termux, arm64).
> Binaries are statically linked against OCaml's runtime and only depend on
> the Android system libs.

---

## Contents

| File | What it is |
|---|---|
| `bin/weidu` | **The main tool.** Installs mods, patches resources, edits TLKs, compiles scripts, etc. |
| `bin/weinstall` | Small convenience wrapper: finds `setup-<mod>.tp2` for you and calls `weidu`. |
| `bin/tolower` | Legacy case-folder utility + Wine `linux.ini` generator. **Not needed (and harmful) on EE games.** |
| `build/build-android.sh` | Reproducible build script for the whole toolchain. |
| `SHA256SUMS` | Checksums of the shipped binaries. |
| `COPYING` | WeiDU's license (GPL-2.0). |

All three binaries are the same WeiDU release (`25100`).

---

## Requirements

- **Termux** (F-Droid or GitHub build) on a **64-bit ARM (arm64-v8a)** device.
- Android 7.0+ (the binaries are built for the `Android 24` / API 24 ABI).

32-bit ARM is **not** provided here, and neither is x86. Only `aarch64`.

---

## Install

Copy the binaries into your Termux `$PREFIX/bin` and make them executable:

```bash
# from the folder where you cloned/downloaded this repo
cp bin/weidu bin/weinstall bin/tolower "$PREFIX/bin/"
chmod 755 "$PREFIX/bin/weidu" "$PREFIX/bin/weinstall" "$PREFIX/bin/tolower"
```

That's it. Because `$PREFIX/bin` is already on `PATH`, the commands are now
available:

```bash
weidu --version
# [weidu] WeiDU version 25100
```

If you previously had an older `weidu` (for example v24900), this **replaces**
it. Back up the old binary first if you want to keep it:

```bash
cp "$PREFIX/bin/weidu" "$PREFIX/bin/weidu.old"
```

> Git on Android storage often cannot keep the executable bit, so after cloning
> you may need `chmod 755 bin/weidu` even though the mode is set in the repo.

---

## Usage

**Always run WeiDU from the game directory** (the folder that contains
`chitin.key`). Use `--game` to point at it if you are elsewhere.

```bash
cd /path/to/game            # contains chitin.key
weidu /path/to/setup-my-mod.tp2 --language 0 --force-install-list 0
```

Common options:

```bash
weidu --version                          # print version
weidu --help                             # full option list
weidu --game /path/to/game setup-x.tp2   # explicit game dir
weidu --nogame setup-x.tp2               # do not load any game files
```

`weinstall` is a shortcut for the usual case (the mod folder holds
`setup-<name>.tp2`):

```bash
weinstall my-mod --language 0 --force-install-list 0
# is equivalent to
weidu my-mod/setup-my_mod.tp2 --language 0 --force-install-list 0
```

> Option order matters in current WeiDU: put the `.tp2` **first**, then the
> options (`weidu setup-x.tp2 --language 0 --force-install-list 0`).

### `tolower` — do not use it on EE

`tolower` lowercases every file name in a folder (for old case-sensitive
Windows→Linux ports) and builds a Wine `linux.ini`. Enhanced Edition games do
not need it, and running it on an EE game **breaks it**. The tool even refuses:

```text
This looks like an EE-type game. Tolower would break it.
```

It is included only for completeness with the upstream release.

---

## What's new vs. older builds (v249 → v251)

Highlights relevant to Android/Termux modding (full list in WeiDU's
`README-WeiDU-Changes.txt`):

- **Linux builds no longer require `tolower` or a case-insensitive file
  system.** WeiDU-Linux is expected to work on a plain case-sensitive FS.
- `ADD_KIT` / `COPY_KIT` now understand **filler lines in `KITLIST.IDS`**.
- `HANDLE_CHARSETS` gained inference support for **Turkish**, Hungarian,
  Norwegian, Ukrainian and others; `AUTO_TRA` gained a `subdir` option.
- `--force-install-list` and friends now **warn when a given component number
  does not exist**.
- `%MOD_FOLDER%` contents are case-exact; case-insensitive lookup fixes.
- New script helpers: `GET_RESOURCE_ARRAY`, `VARIABLE_IS_IN_ARRAY`,
  `OUTER_SPRINTF`, `DEFINED_AS_FUNCTION`, `REGISTER_UNINSTALL`, a `GLOBAL`
  option for `SET`/`SPRINT`, `--unbiff`, and clearer error messages.

---

## Build from source

Everything below runs **inside Termux**. See `build/build-android.sh` for the
automated version.

```bash
pkg install -y git cmake bison flex make clang libandroid-shmem
```

### 1. OCaml 4.14.2 (with unsafe strings)

WeiDU still requires mutable ("unsafe") strings, and **OCaml 5.x removed the
`-unsafe-string` option**, so a 4.x compiler is mandatory. Termux's packaged
`ocaml` is 5.5 and does *not* work — build 4.14.2 from source:

```bash
curl -LO https://github.com/ocaml/ocaml/archive/refs/tags/4.14.2.tar.gz
tar xf 4.14.2.tar.gz && cd ocaml-4.14.2

# -landroid-shmem resolves libandroid_shmat referenced by runtime/afl.c
CC="gcc -landroid-shmem" ./configure \
    -prefix "$HOME/opt/ocaml-4.14.2" \
    -host aarch64-linux-android \
    --disable-force-safe-string

make -j"$(nproc)" world.opt
make install
```

### 2. Elkhound (parser generator used by WeiDU)

```bash
git clone --depth 1 https://github.com/WeiDUorg/elkhound.git
cmake -S elkhound/src -B elkhound/build \
      -DCMAKE_BUILD_TYPE=Release -DEXTRAS=OFF \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build elkhound/build -j"$(nproc)"
```

### 3. WeiDU v251.00

```bash
git clone https://github.com/WeiDUorg/weidu.git
cd weidu && git checkout v251.00

export PATH="$HOME/opt/ocaml-4.14.2/bin:$PWD/../elkhound/build/elkhound:$PATH"
make -j"$(nproc)" weidu weinstall tolower

strip weidu.asm.exe weinstall.asm.exe tolower.asm.exe
```

The `make` output files are named `*.asm.exe` (WeiDU's Makefile convention for
native code). They are ordinary Linux/Android ELF executables — the `.exe`
suffix is **not** a Windows PE. Rename them to `weidu`, `weinstall`, `tolower`.

### Why OCaml 5 fails

Termux ships `ocaml 5.5.0`, which no longer accepts `-unsafe-string`, and the
WeiDU source uses `String.create` / `String.uppercase` etc. A 4.x compiler
configured **without** forced safe strings is the reliable path, hence the
from-source OCaml step above. (`--disable-force-safe-string` is OCaml 4.x's
equivalent of "unsafe strings by default"; WeiDU's Makefile also passes
`-unsafe-string` explicitly.)

---

## Verify

```bash
sha256sum -c SHA256SUMS
file bin/weidu        # ARM aarch64, /system/bin/linker64
./bin/weidu --version # WeiDU version 25100
```

---

## Source & licensing

- WeiDU: <https://github.com/WeiDUorg/weidu> (GPL-2.0, see `COPYING`)
- Elkhound: <https://github.com/WeiDUorg/elkhound>

This repository only repackages **unmodified upstream source** compiled for
Android/arm64. It is not affiliated with or endorsed by the WeiDU authors.
Because WeiDU is GPL-2.0, the corresponding source is the upstream repository
at the `v251.00` tag; the exact build recipe is in `build/build-android.sh`.
