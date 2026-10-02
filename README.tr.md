# Android (Termux) için WeiDU — native arm64 derlemesi

> English: [README.md](README.md)

![Android arm64 için WeiDU v251](docs/banner.png)

Infinity Engine oyunları için mod kurma/geliştirme aracı
[**WeiDU v251.00**](https://github.com/WeiDUorg/weidu/releases/tag/v251.00)'ün
resmî olmayan **native Android (aarch64 / arm64-v8a)** derlemesi
(Baldur's Gate: Enhanced Edition, BG2:EE, IWD:EE, PST:EE, …).

Bu binary'ler **Termux içinde, cihaz üzerinde** OCaml 4.14.2 ve Android NDK
araç zinciriyle derlendi. Emülasyon yok, `proot` yok, glibc yok — doğrudan
Termux `$PREFIX` altında çalışan gerçek Android ELF dosyalarıdır.

> **Durum:** BGEE Android (Termux, arm64) üzerinde derlendi ve denendi.
> Binary'ler OCaml çalışma zamanına statik bağlı; yalnız Android sistem
> kütüphanelerine ihtiyaç duyar.

---

## İçerik

| Dosya | Açıklaması |
|---|---|
| `bin/weidu` | **Ana araç.** Mod kurar, kaynakları yamar, TLK düzenler, script derler vb. |
| `bin/weinstall` | Kolaylık sarmalayıcısı: `setup-<mod>.tp2` dosyasını kendisi bulup `weidu`'yu çağırır. |
| `bin/tolower` | Eski case-folder aracı + Wine `linux.ini` üreticisi. **EE oyunlarında gerekmez (ve zararlıdır).** |
| `build/build-android.sh` | Tüm araç zincirini tekrarlanabilir şekilde derleyen script. |
| `SHA256SUMS` | Gönderilen binary'lerin sağlama toplamları. |
| `COPYING` | WeiDU lisansı (GPL-2.0). |

Üç binary de aynı WeiDU sürümüdür (`25100`).

---

## Gereksinimler

- **64-bit ARM (arm64-v8a)** cihazda **Termux** (F-Droid veya GitHub sürümü).
- Android 7.0+ (binary'ler `Android 24` / API 24 ABI için derlendi).

Burada 32-bit ARM **yok**, x86 da yok. Yalnız `aarch64`.

---

## Kurulum

Binary'leri Termux `$PREFIX/bin` içine kopyalayıp çalıştırılabilir yapın:

```bash
# bu repoyu klonladığınız/indirdiğiniz klasörde
cp bin/weidu bin/weinstall bin/tolower "$PREFIX/bin/"
chmod 755 "$PREFIX/bin/weidu" "$PREFIX/bin/weinstall" "$PREFIX/bin/tolower"
```

Hepsi bu. `$PREFIX/bin` zaten `PATH` içinde olduğu için komutlar hazırdır:

```bash
weidu --version
# [weidu] WeiDU version 25100
```

Daha önce eski bir `weidu` (örneğin v24900) varsa bu onun **üzerine yazar**.
Eskisini saklamak isterseniz önce yedekleyin:

```bash
cp "$PREFIX/bin/weidu" "$PREFIX/bin/weidu.old"
```

> Android depolamasında git genellikle çalıştırma bitini koruyamaz; klonladıktan
> sonra repo'da ayarlı olsa bile `chmod 755 bin/weidu` gerekebilir.

---

## Kullanım

**WeiDU'yu her zaman oyun dizininden** çalıştırın (`chitin.key` dosyasının
bulunduğu klasör). Başka yerdeyseniz `--game` ile oyunu gösterin.

```bash
cd /oyun/dizini            # chitin.key burada
weidu /yol/setup-modum.tp2 --language 0 --force-install-list 0
```

Sık kullanılan seçenekler:

```bash
weidu --version                          # sürümü yazdır
weidu --help                             # tüm seçenekler
weidu --game /oyun/dizini setup-x.tp2    # oyun dizinini açıkça ver
weidu --nogame setup-x.tp2               # hiçbir oyun dosyasını yükleme
```

`weinstall`, olağan durum (mod klasöründe `setup-<ad>.tp2` var) için kısayoldur:

```bash
weinstall modum --language 0 --force-install-list 0
# şuna eşdeğerdir:
weidu modum/setup-modum.tp2 --language 0 --force-install-list 0
```

> Güncel WeiDU'da seçenek sırası önemlidir: önce `.tp2`, sonra seçenekler
> (`weidu setup-x.tp2 --language 0 --force-install-list 0`).

### `tolower` — EE'de kullanmayın

`tolower`, bir klasördeki tüm dosya adlarını küçük harfe çevirir (eski
Windows→Linux portları için) ve Wine `linux.ini` üretir. Enhanced Edition
oyunları buna ihtiyaç duymaz ve EE oyununda çalıştırmak **oyunu bozar**. Araç
zaten reddeder:

```text
This looks like an EE-type game. Tolower would break it.
```

Yalnız upstream sürümle bütünlük için dahil edilmiştir.

---

## Eski sürümlere göre yenilikler (v249 → v251)

Android/Termux modlamasını ilgilendiren öne çıkanlar (tam liste WeiDU'nun
`README-WeiDU-Changes.txt` dosyasında):

- **Linux derlemeleri artık `tolower` veya case-insensitive dosya sistemi
  gerektirmiyor.** WeiDU-Linux düz case-sensitive FS'te çalışmalı.
- `ADD_KIT` / `COPY_KIT` artık **`KITLIST.IDS` içindeki filler (dolgu)
  satırlarını** anlıyor.
- `HANDLE_CHARSETS` **Türkçe**, Macarca, Norveççe, Ukraynaca ve daha fazlası
  için charset çıkarımı kazandı; `AUTO_TRA` bir `subdir` seçeneği kazandı.
- `--force-install-list` ve benzerleri artık **verilen bileşen numarası var
  değilse uyarıyor**.
- `%MOD_FOLDER%` içeriği case-exact; case-insensitive arama düzeltmeleri.
- Yeni script yardımcıları: `GET_RESOURCE_ARRAY`, `VARIABLE_IS_IN_ARRAY`,
  `OUTER_SPRINTF`, `DEFINED_AS_FUNCTION`, `REGISTER_UNINSTALL`, `SET`/`SPRINT`
  için `GLOBAL` seçeneği, `--unbiff` ve daha anlaşılır hata mesajları.

---

## Kaynaktan derleme

Aşağıdaki her şey **Termux içinde** çalıştırılır. Otomatik sürüm için
`build/build-android.sh` dosyasına bakın.

```bash
pkg install -y git cmake bison flex make clang libandroid-shmem
```

### 1. OCaml 4.14.2 (unsafe string'lerle)

WeiDU hâlâ değiştirilebilir ("unsafe") string'ler gerektirir ve **OCaml 5.x
`-unsafe-string` seçeneğini kaldırdı**; bu yüzden 4.x derleyici zorunludur.
Termux'un paketlediği `ocaml` 5.5'tir ve *işe yaramaz* — 4.14.2'yi kaynaktan
derleyin:

```bash
curl -LO https://github.com/ocaml/ocaml/archive/refs/tags/4.14.2.tar.gz
tar xf 4.14.2.tar.gz && cd ocaml-4.14.2

# -landroid-shmem, runtime/afl.c'nin başvurduğu libandroid_shmat'ı çözer
CC="gcc -landroid-shmem" ./configure \
    -prefix "$HOME/opt/ocaml-4.14.2" \
    -host aarch64-linux-android \
    --disable-force-safe-string

make -j"$(nproc)" world.opt
make install
```

### 2. Elkhound (WeiDU'nun kullandığı parser üreticisi)

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

`make` çıktı dosyalarının adı `*.asm.exe`'dir (WeiDU Makefile'ının native kod
adlandırması). Bunlar sıradan Linux/Android ELF dosyalarıdır — `.exe` uzantısı
**Windows PE anlamına gelmez**. `weidu`, `weinstall`, `tolower` olarak
yeniden adlandırın.

### OCaml 5 neden olmuyor

Termux `ocaml 5.5.0` ile gelir; bu sürüm artık `-unsafe-string` kabul etmez ve
WeiDU kaynağı `String.create` / `String.uppercase` vb. kullanır. Güvenilir yol,
safe string'e zorlamayan bir 4.x derleyicidir; yukarıdaki kaynaktan OCaml adımı
bu yüzden gerekir. (`--disable-force-safe-string`, OCaml 4.x'in "varsayılan
unsafe string" karşılığıdır; WeiDU Makefile'ı ayrıca açıkça `-unsafe-string`
geçer.)

---

## Doğrulama

```bash
sha256sum -c SHA256SUMS
file bin/weidu        # ARM aarch64, /system/bin/linker64
./bin/weidu --version # WeiDU version 25100
```

---

## Kaynak ve lisans

- WeiDU: <https://github.com/WeiDUorg/weidu> (GPL-2.0, bkz. `COPYING`)
- Elkhound: <https://github.com/WeiDUorg/elkhound>

Bu repo yalnızca **değiştirilmemiş upstream kaynağı** Android/arm64 için
derleyip yeniden paketler. WeiDU yazarlarıyla bağlantılı veya onlar tarafından
onaylanmış değildir. WeiDU GPL-2.0 olduğundan karşılık gelen kaynak, upstream
repodaki `v251.00` etiketidir; tam derleme tarifi `build/build-android.sh`
içindedir.
