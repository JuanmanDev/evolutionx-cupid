# Evolution X 17 for Xiaomi 12 (cupid) — unofficial build

An unofficial Evolution X 17 (Android 17) build for the Xiaomi 12 (`cupid`,
SM8450), with a handful of device-specific fixes that are not in the official
build. Everything documented here was measured on a real device, and the notes
say plainly what works, what does not, and why.

**This is not an official Evolution X release.** Do not report bugs from this
build to the Evolution X team.

## Screenshots

| Evolution X | Customization | Dolby Atmos |
|---|---|---|
| [<img src="screenshots/01-evolution-x.png" width="230">](screenshots/01-evolution-x.png) | [<img src="screenshots/02-customization.png" width="230">](screenshots/02-customization.png) | [<img src="screenshots/03-dolby-atmos.png" width="230">](screenshots/03-dolby-atmos.png) |

## What is different from a stock build

| Change | Why |
|---|---|
| Camera HAL logging turned off | It shipped at full verbosity **and dumping to disk**. With the camera open it went from hundreds of log lines per second to 6 lines in 8 seconds. It cost CPU and writes during every recording. |
| Correct audio calibration (`Forte_elus`) | The audio HAL always opens `acdbdata/Forte/Forte_acdb_cal.acdb`. This unit needs the `elus` set; loading the generic one leaves the DSP without data (`No calibration found`) and **without echo cancellation** — the person on the other end hears themselves. |
| 15 volume steps for notifications and ringtone | They shipped with 7 (media has 15), so the lowest step was already loud. |
| Lower volume curve for notifications and ringtone | Their curve started at −29.7 dB while media starts at −58 dB. The first step now lands around −45 dB instead of −26 dB. Maximum volume is unchanged. |
| `ro.debuggable=0` | The build presents itself as a user build with release-keys; shipping `ro.debuggable=1` on top of that is detected by Play Integrity and banking apps, and costs performance. |
| Root from KernelSU | Root comes from KernelSU-Next (v3.0.1 + SuSFS), built into the kernel. Its `su` lives at `/system/bin/su` and is visible to apps — hide it per-app with the KernelSU denylist; see "Known limits". |
| 50 MP camera app (`Cam50Test`) | The only way to get real full-sensor stills on this device (see below). |

## About the 50 MP mode — read this before asking

The sensor is 50 MP (8192x6144) but **the HAL does not advertise any still size
above 4208x3120**. Full size only appears in RAW formats and in Xiaomi's private
`qcfa_dimension` tag. That is why GCam offers "50 MP", asks for something that
was never advertised, and crashes.

The HAL *does* accept the size if you ask for it directly, which is what the
bundled app does. Measured results, same scene, tripod-still device:

| Version | real detail | notes |
|---|---|---|
| upscaled 12.6 MP (reference) | 0.0246 | correct colour |
| standard Android path (`SENSOR_PIXEL_MODE_MAXIMUM_RESOLUTION`) | 0.0197 | **below the reference**: the HAL returns an upscale |
| Xiaomi path (`xiaomi.remosaic.enabled`) | 0.0475 | the only one with real extra detail |

The Xiaomi path is also the one with a pink cast and colour aliasing on fine
patterns, and it cannot be corrected from the app: the HAL ignores colour gains
in that route, and the deviation depends on tone. The root cause is that this
module's EEPROM declares its `CrossTalk` region with **size 0** — the remosaic
runs without its calibration data.

There is an experimental switch that advertises the full size to every app:

    setprop persist.sys.camera.qcfa_jpeg 1     # then restart cameraserver

It is **off by default on purpose**. With it on, CameraX picks 8192x6144 and
reserves four buffers of that size (~400 MB); the camera HAL then dies and the
system camera closes on shutter. Apps that request a single full-size image work
fine.

## Honest status

Working: boot with SELinux **enforcing**, telephony with VoLTE, Wi-Fi,
Bluetooth, fingerprint, NFC, camera, video, audio with working echo cancellation,
KernelSU root.

Known limits: 50 MP only through the bundled app and with the colour caveats
above; GCam cannot do 50 MP on this device; the build is signed with public AOSP
test keys; and root is visible to apps — KernelSU-Next's `su` sits at
`/system/bin/su` (it *is* the root entry point, so it can't just be deleted).
Hide it from the apps that care (banking, integrity checks) with the KernelSU-Next
**denylist / App Profiles**, backed by the **SuSFS** already in the kernel. See
`docs/RECOMMENDATIONS.md` → "Hiding root".

## Two variants: with or without KernelSU

The ROM is the same; only the **boot image** differs:

  - **`boot-ksu.img`** — kernel with **KernelSU** built in (root). *Default.*
  - **`boot-noksu.img`** — clean kernel, **no root**.

Root is compiled into the kernel (KernelSU-Next + SuSFS). The latest KernelSU
(v3.3.0) is **not** shipped: it dropped the kprobes-hook and SuSFS integration
this kernel uses, and adopting it would mean rewriting the kernel hooks — high
bootloop risk for no real gain. This build stays on the proven **v3.0.1 + SuSFS
v2.0.0**.

## What a release contains

Big images are attached to the GitHub **Release** (GitHub blocks files over
100 MB in the repo and 2 GB per release asset):

    rom.zip.part-*      the ROM (Evolution X OTA), split; join with unir_rom.sh
    boot-ksu.img        boot WITH KernelSU (root)
    boot-noksu.img      boot WITHOUT KernelSU (clean)
    dtbo.img  vbmeta.img  vbmeta_system.img  vendor_boot.img  recovery.img

In the repo:

    scripts/     flashear_todo.sh (all-in-one), unir_rom.sh, instalar_modulo.sh, ...
    modules/     cupid_ajustes  (KernelSU module, survives OTAs)
    patches/     the AOSP framework patches (camera 50 MP support, etc.)
    docs/        install guide (EN/ES), 50 MP write-up, recommendations, changes

Quick install: join the ROM, then `scripts/flashear_todo.sh --ksu --wipe`.

## Documentation

English is the primary language; every doc has a Spanish version (`*.es.md`, or
`LEEME.md` / `INSTALACION.md` / `RECOMENDACIONES.md`).

| Doc | About |
|---|---|
| [`docs/INSTALL.md`](docs/INSTALL.md) | Step-by-step flashing (manual). |
| [`docs/RECOMMENDATIONS.md`](docs/RECOMMENDATIONS.md) | Camera (50 MP), GCam setup, Lawnchair, 0.5× animations, status bar. |
| [`docs/50MP.md`](docs/50MP.md) | The full 50 MP story — and why GCam can't do it. |
| [`docs/CAMERA-50MP.md`](docs/CAMERA-50MP.md) | Deep camera notes (modes, remosaic, colour). |
| [`docs/CHANGES.md`](docs/CHANGES.md) | Every change vs the official tree. |
| [`docs/NOTES.md`](docs/NOTES.md) | Performance/power notes measured on-device. |
| [`docs/BANK.md`](docs/BANK.md) | Deutsche Bank apps: no-root fixes the main app; 2FA is blocked by hardware attestation. |
| [`patches/`](patches/) | The AOSP framework patches. |

## Credits

See [`CREDITOS.md`](CREDITOS.md). In short: thanks to the **Evolution X team**,
to **everyone who has maintained the Xiaomi 12 (cupid)** device/kernel trees, to
**[KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next)** and
**[SuSFS](https://gitlab.com/simonpunk/susfs4ksu)**, to **LineageOS** and to the
community that documents and shares.
