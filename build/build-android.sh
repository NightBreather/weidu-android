#!/usr/bin/env bash
#
# build-android.sh — build WeiDU natively for Android/arm64 inside Termux.
#
# Produces: bin/weidu, bin/weinstall, bin/tolower (stripped, arm64 ELF).
#
# Tested with: Termux, arm64-v8a, OCaml 4.14.2, WeiDU v251.00.
#
# Usage:  bash build/build-android.sh
#
set -euo pipefail

WEIDU_TAG="${WEIDU_TAG:-v251.00}"
OCAML_VER="${OCAML_VER:-4.14.2}"
ARCH="${ARCH:-aarch64-linux-android}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$HOME/weidu-build}"
PREFIX_OCAML="$WORK/ocaml-$OCAML_VER"

mkdir -p "$WORK"
cd "$WORK"

echo "==> Installing Termux build dependencies"
pkg install -y git cmake bison flex make clang libandroid-shmem

# ---------------------------------------------------------------------------
# 1) OCaml 4.14.x with unsafe strings.
#
#    WeiDU needs mutable strings; OCaml 5.x dropped -unsafe-string, so the
#    Termux-packaged ocaml (5.x) cannot be used. We also need -landroid-shmem
#    because runtime/afl.c references shmat(), which Termux remaps to
#    libandroid_shmat in <sys/shm.h>.
# ---------------------------------------------------------------------------
if [ ! -x "$PREFIX_OCAML/bin/ocamlopt" ]; then
  echo "==> Building OCaml $OCAML_VER"
  if [ ! -d "ocaml-$OCAML_VER" ]; then
    curl -LO "https://github.com/ocaml/ocaml/archive/refs/tags/$OCAML_VER.tar.gz"
    tar xf "$OCAML_VER.tar.gz"
  fi
  cd "ocaml-$OCAML_VER"
  CC="gcc -landroid-shmem" ./configure \
      -prefix "$PREFIX_OCAML" \
      -host "$ARCH" \
      --disable-force-safe-string
  make -j"$(nproc)" world.opt
  make install
  cd "$WORK"
else
  echo "==> OCaml already built at $PREFIX_OCAML"
fi

# ---------------------------------------------------------------------------
# 2) Elkhound — parser generator used to generate part of WeiDU's parser.
# ---------------------------------------------------------------------------
if [ ! -x "$WORK/elkhound/build/elkhound/elkhound" ]; then
  echo "==> Building Elkhound"
  [ -d elkhound ] || git clone --depth 1 https://github.com/WeiDUorg/elkhound.git
  cmake -S elkhound/src -B elkhound/build \
        -DCMAKE_BUILD_TYPE=Release -DEXTRAS=OFF \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5
  cmake --build elkhound/build -j"$(nproc)"
else
  echo "==> Elkhound already built"
fi

# ---------------------------------------------------------------------------
# 3) WeiDU
# ---------------------------------------------------------------------------
echo "==> Building WeiDU $WEIDU_TAG"
[ -d weidu ] || git clone https://github.com/WeiDUorg/weidu.git
cd weidu
git fetch --tags
git checkout "$WEIDU_TAG"

export PATH="$PREFIX_OCAML/bin:$WORK/elkhound/build/elkhound:$PATH"
which ocaml; ocamlopt -version
which elkhound

make -j"$(nproc)" weidu weinstall tolower

# ---------------------------------------------------------------------------
# 4) Collect, strip and checksum.
# ---------------------------------------------------------------------------
echo "==> Collecting binaries"
mkdir -p "$REPO_ROOT/bin"
cp weidu.asm.exe     "$REPO_ROOT/bin/weidu"
cp weinstall.asm.exe "$REPO_ROOT/bin/weinstall"
cp tolower.asm.exe   "$REPO_ROOT/bin/tolower"
chmod 755 "$REPO_ROOT"/bin/*
strip "$REPO_ROOT"/bin/*

cd "$REPO_ROOT"
sha256sum bin/weidu bin/weinstall bin/tolower > SHA256SUMS

echo "==> Done. Binaries in $REPO_ROOT/bin"
"$REPO_ROOT/bin/weidu" --version
