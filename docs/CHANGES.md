# Changes from the official tree

Everything that was touched, with the file it lives in and a one-line reason. The
full detail with measurements is in [`NOTES.md`](NOTES.md). *(Spanish:
[`CAMBIOS.es.md`](CAMBIOS.es.md).)*

## Device tree (`device/xiaomi/cupid`)

| File | Change |
|---|---|
| `device.mk` | `Forte_elus` audio calibration installed at the path the HAL opens (`acdbdata/Forte/`). Without it there is no echo cancellation. |
| `device.mk` | `ro.debuggable=1` removed. |
| `device.mk` | `persist.vendor.camera.privapp.list` includes the 50 MP camera package. |
| `device.mk` | `Cam50Test` added to the product packages. |
| `evolution_cupid.mk` | Attempt (**no effect yet**) to filter the AOSP `su` out of the debug packages. See "Pending". |
| `overlay/.../config.xml` | 15 volume steps for notification and ringtone instead of 7. |
| `apps/Cam50Test/` | 50 MP camera (new app). |
| `apps/MedidorNivel/` | Sound level meter, to check volumes with numbers. |

## Vendor blobs (`vendor/xiaomi/cupid`)

| File | Change |
|---|---|
| `vendor/etc/camera/camxoverridesettings.txt` | Camera HAL log down to errors only, no disk dump. Original kept as `.con-logs`. |

## AOSP

| File | Change |
|---|---|
| `frameworks/av/.../audio_policy_volumes.xml` | Notification/ringtone speaker volume curve: low end reaches −50 dB instead of −29.7. |
| `frameworks/av/.../CameraProviderManager.{cpp,h}` | New `addQuadCfaFullSizeJpeg()`: advertises the full sensor size as a photo size. **Off by default** (`persist.sys.camera.qcfa_jpeg`), since with it on, apps that reserve several buffers kill the HAL. |
| `frameworks/av/.../Camera3Device.cpp` | `tagFullSizeQuadCfaRequestLocked()`: switches the session to the `0x80F3` mode and injects `xiaomi.remosaic.enabled` for full-size JPEG requests — the real 50 MP path. |
| `frameworks/av/.../{Aidl,Hidl}ProviderInfo.cpp` | Call the functions above. |

The framework patches are in [`../patches/`](../patches/).

## Kernel / root

| What | Detail |
|---|---|
| KernelSU-Next **v3.0.1 + SuSFS v2.0.0** | Root compiled into the kernel (kprobes hook). The latest KSU (v3.3.0) was tested and **not** adopted: it dropped the kprobes hook and the SuSFS this kernel uses, which would mean rewriting the kernel integration (bootloop risk). |
| Two boot variants | `boot-ksu.img` (root) and `boot-noksu.img` (clean) — only `CONFIG_KSU` differs. |

## Outside the tree (lives on the phone)

| Where | What |
|---|---|
| `/data/adb/modules/cupid_ajustes` | KernelSU module that replays the `vendor`/`odm` tweaks and forces `ro.debuggable=0`. This is what keeps everything alive across OTAs. |

## Tried and dropped

  - **Standard Android 50 MP path** (`SENSOR_PIXEL_MODE_MAXIMUM_RESOLUTION`): the
    HAL accepts the session but returns an upscale, with less detail than an
    enlarged 12.6 MP shot.
  - **GCam at 50 MP**: impossible — see [`50MP.md`](50MP.md).
  - **Installing both audio calibration sets under their own names**: looks
    correct, but the HAL always opens `Forte/` and ended up loading the generic
    one, reintroducing in-call echo.
  - **Correcting the 50 MP colour with gains**: the deviation is tone-dependent
    and the HAL ignores gains on that route.

## Root visibility (`/system/bin/su`)

`/system/bin/su` is **KernelSU-Next's own `su`** (it *is* `ksud`; in its source,
`if arg0 == "su" || arg0 == "/system/bin/su"`). It is the root entry point, so it
can't be deleted without losing root. It is visible to apps, so it is a root
indicator. There is **no** stray AOSP `su` at `/system/xbin/su` (an earlier note
said so — inaccurate). To hide root from apps that check for it (banking,
integrity), use the KernelSU-Next **denylist / App Profiles**, backed by the
**SuSFS** already compiled into the kernel — a per-app hide, done from the
KernelSU-Next app. See [`RECOMMENDATIONS.md`](RECOMMENDATIONS.md) → "Hiding root".
