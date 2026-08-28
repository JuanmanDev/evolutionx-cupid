# Recommendations

Settings worth applying on this phone, with the exact commands. All optional —
none of this is required for the ROM to work. *(Spanish version:
[`RECOMENDACIONES.md`](RECOMENDACIONES.md).)*

## Camera

### For 50 MP: use the Xiaomi camera (or Aperture / Cam50Test), not GCam

On this phone **GCam cannot take 50 MP photos** — measured and explained in full
in [`50MP.md`](50MP.md) and [`CAMERA-50MP.md`](CAMERA-50MP.md). Short version:
GCam's HDR+ engine only knows how to ask for RAW/YUV at full resolution, and this
chip's HAL only delivers the 50 MP as a **JPEG** through Xiaomi's proprietary
remosaic path; through the RAW/YUV route the HAL returns black. It was pushed all
the way to patching the framework (active array set to 8192×6144, forcing the
remosaic mode onto GCam's RAW stream): GCam then configures the session and starts
HDR+, but the frames come back black. It is a hardware/HAL wall, not software.

**What does produce real 50 MP:**

| App | How |
|---|---|
| **Xiaomi camera** (`com.android.camera`) | Photo mode → **50 MP** selector. The native path, the most convenient. |
| **Aperture** (the ROM's camera) | With 50 MP support compiled in, normal shutter → 8192×6144 JPEG + DNG. |
| **Cam50Test** | The bundled app, built only for this (50 MP JPEG + RAW). |

Colour caveat: the real 50 MP comes out with a **magenta tint** that cannot be
corrected in-app (the module ships no crosstalk calibration; details in the
notes). Drop one EV step if highlights clip:

    adb shell su -c "setprop persist.cam50.ev -6"   # then reopen the 50 MP camera

**For everyday shots, GCam at 12.6 MP usually beats the magenta 50 MP** — unless
you need to crop a lot — because its HDR+ and processing are better. Use each for
what it is good at.

### Recommended GCam setup (at 12.6 MP)

Any modern GCam port (BSG/LMC 8.x, or the bundled `fishfood`) runs at 12.6 MP.
Recommended settings for the best results:

  - **HDR+ Enhanced** on (better dynamic range, slower).
  - **Google AWB** on (better white balance than the HAL's).
  - **RAW (DNG)** on if you want to edit later; larger files.
  - Leave the resolution at its default (12.6 MP): do not try to force 50 MP, it
    crashes.

Community XML configs (e.g. celsoazevedo) **tune the processing** (colour, noise,
tones) at 12.6 MP — which is where GCam beats the Xiaomi camera — they do **not**
unlock megapixels. Try them for colour taste.

## Extras that work (good to know)

  - **Dolby Atmos** works (`co.aospa.dolby.xiaomi`). Open **Dolby Atmos** from the
    app drawer to pick a profile (Music / Movie / …); it applies to speaker and
    headphones.
  - **Adjustable flashlight brightness.** Long-press the **Flashlight** quick
    settings tile to get a brightness slider (Evolution X feature; cupid's LED
    driver supports the current levels — the ROM tunes flash/torch currents in the
    camera HAL). Useful for a softer torch or a stronger camera flash.
  - **15 volume steps** for ringtone/notification with a lower first step (see
    [`CHANGES.md`](CHANGES.md)).

## Xiaomi camera: extra modes that need downloading may crash

The Xiaomi camera (MiuiCamera port) shows extra modes with a **download arrow**
(Clone, Panorama, VLOG, movie effects, long-exposure pro, …). Tapping one
**closes the app**. Diagnosed: those modes fetch a component via Google Play
Dynamic Delivery (the Clone module is ~77 MB), but this ROM **blocks MiuiCamera's
network with SELinux** — the `miuicamera_app` domain is denied socket creation, on
purpose, to kill Xiaomi's ad/telemetry process (`mi_ad_pubsub`). The blocked
network throws an uncaught `SecurityException` → crash:

    avc: denied { create } tclass=udp_socket ... app=com.android.camera
    java.lang.SecurityException: Permission denied (missing INTERNET permission?)

**Can it be fixed?** Partly. Allowing the domain's network (a KernelSU SELinux
rule, `permissive miuicamera_app` or a targeted `allow`) **stops the crash** —
tested. But: (1) it brings back Xiaomi's ad/telemetry network, and (2) the module
still isn't bundled (`Split clone … is not installed`, `no fused modules`) and
Google Play won't serve it to this system-installed port — so the mode fails to
download anyway. Net result: "no crash, download fails" rather than a working
mode. So it isn't really worth it.

**Can't I just install one APK with all modes?** No. Those modes are Android
Dynamic Feature Modules — you'd need Xiaomi's original app bundle (`.aab`, not
public) to fuse them into one APK, and the per-version split APKs aren't
distributed on their own. The generic "Xiaomi Camera" builds on APKMirror are the
**MIUI** version: they expect the MIUI framework and lack this port's AOSP
adaptations (50 MP, SELinux domain, property fixes), so installing one over this
port breaks the working camera. Some modes (Clone, AI watermark) also need MIUI
services AOSP doesn't have. **Use GCam for panorama and the other missing modes.**

**The core modes work**: Photo, **50 MP**, Video, Portrait, Night, Pro,
Slow-motion, Time-lapse, Documents, Dual video. For panorama and similar, use GCam
or another app.

## Launcher: Lawnchair (accent-insensitive app search)

Recommended launcher: **[Lawnchair](https://lawnchair.app/)**. Besides the clean
Pixel-style look and lots of tweaks, its **app search ignores accents** — typing
`camara` finds *Cámara*, `telefono` finds *Teléfono*. The stock launcher's search
is accent-sensitive and misses those. Install it, set it as default (Settings →
Apps → Default apps → Home app), and use the search bar in the app drawer.

## Animation speed at 0.5× (snappier UI)

The system feels faster with animations at half speed:

    adb shell settings put global window_animation_scale 0.5
    adb shell settings put global transition_animation_scale 0.5
    adb shell settings put global animator_duration_scale 0.5

(Use `0` to turn them off entirely, `1` to restore the default.) Also available
under Settings → Developer options → the three animation scales.

## Status bar (the Xiaomi 12 is tight on space because of the centred camera)

If you turn the clock seconds on, everything no longer fits and the signal icon
collapses into a dot or overlaps the Wi-Fi icon. This shows everything:

    adb shell settings put system status_bar_clock_seconds 0
    adb shell settings put system network_traffic_hidearrow 1

And make sure the status bar paddings are not negative (if they are, the first
character of the clock and of the carrier name is clipped):

    adb shell settings put system statusbar_extra_padding_start 0
    adb shell settings put system statusbar_extra_padding_end 0

## In-call audio (if the other party hears themselves)

This ROM ships the audio calibration of one specific unit (`elus`). If your unit
uses the generic one, there is echo. Check (must be 0):

    adb shell su -c "logcat -c; sleep 5; logcat -d | grep -c 'No calibration found'"

If it is above 0, switch the calibration set — see [`INSTALL.md`](INSTALL.md),
"If in-call audio sounds wrong".

## Hiding root from banking apps (optional, advanced)

The kernel ships **SuSFS**. To hide root from specific apps (banking,
authenticators) use the KernelSU app's denylist: **Settings → Configure
denylist**, tick the apps, and with the umount module active they stop seeing
root. USB debugging (`adb_enabled`) is a separate detection; turn it off
(Developer options → USB debugging) when using those apps if they flag it.
