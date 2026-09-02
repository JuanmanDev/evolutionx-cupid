# Cameras — which app for which lens

Verified on the device. For the 50 MP mode see `50MP.md`; this is which app to use
for each physical lens.

## Hardware (4 real sensors — NO telephoto)

| Sensor | Lens | Res |
|---|---|---|
| `imx766` | Main (normal wide) | 50MP (12.6MP binned) |
| `ov13b10` | Ultra-wide (0.6×) | 13MP |
| `s5k5e9` | **Macro** ("rearMacro2x") | 5MP (2592×1944) |
| `ov32b40` | Front | 32MP |

"2×/5×/10×" is **digital zoom** of the main sensor, not optical lenses.

## Which app for which lens

- **MIUICamera** (`com.android.camera`) — the most complete, **all 4 lenses**. Uses
  Xiaomi's vendor pipeline → the only one that does macro and 50 MP.
  - Main / wide / front: direct.
  - **MACRO**: tap the top of the viewfinder → enable the **"Supermacro"** toggle
    (turns on `s5k5e9`; get ~4 cm close; output 2592×1944). Turn it off for normal
    shots or everything fires with the 5 MP lens.
- **Aperture** (`org.lineageos.aperture`) — 3 lenses, good quality: main + wide
  (0.6×) + front. No macro. (`enable_aux_cameras` doesn't help on cupid; reverted.)
- **Open Camera** — cycles the public cameras (main/front/wide). No macro (hidden
  HAL sensor).
- **GCam / LMC** — main + front ONLY. Its engine only has tuning for the primary
  sensor; no aux, no macro.
- **★ MGC (BSG) + qcom HAL** — Google Camera **with a REAL ultra-wide**. With the HAL
  set to `qcom`, MGC opens the real ultra-wide (`ov13b10`): zoom bar 0.7/1.0/2.1,
  **0.7 = real wide** (4208×3120, not a crop). Gives main + wide + front. No macro
  (hidden HAL camera).

## The camera HAL: `xiaomi` vs `qcom` (trade-off)

`ro.hardware.camera` picks the pipeline. It's one **OR** the other:

- **`xiaomi`** (default): MIUICamera with 4 lenses (Supermacro + 50 MP); GCam limited.
- **`qcom`**: MGC with 3 lenses (real wide); **no macro, no 50 MP**.

Manual switch (KernelSU root):

    su 0 /data/adb/ksu/bin/resetprop ro.hardware.camera qcom
    su 0 setprop ctl.restart vendor.camera-provider-2-7
    su 0 killall cameraserver

## KernelSU auto-switch module

`qcom_camera_hal` (in `/data/adb/modules/`, zip under `modules/`): a daemon
(`service.sh`) watches the foreground app and **switches the HAL by itself** —
MIUICamera → `xiaomi` (macro + 50 MP), MGC/GCam/Aperture/OpenCamera/**Gemini** →
`qcom`. Default `xiaomi`. Re-asserts the HAL every second (no-op if already right),
so it corrects drift. **Third-party apps (Gemini, etc.) need `qcom`**: on `xiaomi`
they come out black. That's why Gemini (`com.google.android.googlequicksearchbox` +
`com.google.android.apps.bard`) is in the qcom list; if it's still black right
after using MIUICamera, that's the provider-restart flicker — it recovers in 2-3 s.
(Note: Gemini's preview is a SurfaceView; a screenshot looks black even when it
works — check the saved photo, not a screencap.) ⚠️ Switching families restarts the camera-provider (~2-3 s) and kills the
opening app: when **alternating** between MIUICamera and MGC the 1st open fails,
reopen and it works; within the same app, no issue. Disable it (KSU manager or
`touch .../disable`) to stay on `xiaomi`.

## ROM notes

- `fixGcamAuxRawMismatch()` in `CameraProviderManager.cpp`: caps the aux cameras'
  full-res RAW to the active array → fixes the GCam crash when enumerating the
  front camera. Revert: `setprop persist.sys.camera.gcam_aux_fix 0`.
- Aux-lens HAL gate: `persist.vendor.camera.privapp.list` (MIUICamera and Aperture
  in; GCam not).

## Summary

- **All lenses** → MIUICamera (macro = Supermacro).
- **Google Camera with wide** → MGC + qcom HAL (auto-switch).
- **Best main+UW+front quality** → Aperture.
- **GCam/LMC** → main + front only (engine limit).
