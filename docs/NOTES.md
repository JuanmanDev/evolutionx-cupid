# Performance and power notes on cupid

Things measured on the device, with the reason, so they don't have to be
investigated again. *(Spanish: [`NOTAS.es.md`](NOTAS.es.md).)*

## The camera HAL shipped with logging maxed out (fixed)

`vendor/etc/camera/camxoverridesettings.txt` came with:

    logInfoMask=0x10098
    logConfigMask=0x80
    overrideLogLevels=0x1F      <- every level, VERBOSE included
    enableTxtLogging=1          <- also dumps to /data/vendor/camera
    offlineLogNumber=14

With that, every capture request wrote dozens of lines (CamX, GME, STATS_AEC,
STATS_AF...). While recording video that is dozens per frame, with the CPU and
disk writes that go with it. Xiaomi ships a `camxoverridesettingsOfCloseLog.txt`
right next to it, i.e. they turn it off themselves when they want.

It is now errors only (`overrideLogLevels=0x1`, masks at 0, `enableTxtLogging=0`).
Original kept as `camxoverridesettings.txt.con-logs`. **No image parameter
changes.** Measured with the camera open for 8 seconds: hundreds of lines/second
before, 6 lines total after. 98 MB the text dump had left in
`/data/vendor/camera/offlinelog` were also removed.

## /vendor is 100% full and won't accept live edits

    /dev/block/dm-4  1.9G  1.9G  6.0M  100%  /vendor

Even though `df` says 6 MB free, it won't write 10 KB: copying the HAL settings
file fails with "No space left on device" **and leaves the target at 0 bytes**.
Editing anything in /vendor on the phone doesn't just fail, it destroys the file.

If something in /vendor must change: change it in the tree, `m vendorimage`,
`fastboot flash vendor` from fastbootd. As a temporary patch it can be served from
/data with a `mount -o bind`, after labelling it
`u:object_r:vendor_configs_file:s0`; that undoes itself on reboot.

## The grid of dots in captures was Smart Pixels

Symptom: screenshots (and the screen itself) with a grid of black dots. Cause:
`Settings.Secure.smart_pixel_filter_enabled=1` with `smart_pixel_filter_percent=25`,
which turns off one pixel in four to save OLED power. Turn it off:

    adb shell settings put secure smart_pixel_filter_enabled 0

## /system was 100% full too (relevant if you rebuild boot/system)

The dynamic `/system` (dm-2) shipped at 100%. Writing a slightly larger
`cameraserver` failed until the ext4 was grown into the ~20 MB of unused space in
its device-mapper block: `resize2fs /dev/block/dm-2` (verity is off, so /system is
writable). Kept here because it bit hard during development.

## Volume: loud notifications and inconsistent screen-off media (fixed, 2026-09-02)

Symptom: notifications sometimes louder than the minimum set in Settings; media
with the screen off sometimes fine, sometimes not. **Not Dolby**
(`vendor.audio.dolby.ds2.enabled=false`).

Android stores volume PER OUTPUT DEVICE (mIndexMap in each `VolumeStreamState`).
`dumpsys audio`, e.g. NOTIFICATION: `speaker: 1, default (0x40000000): 7`. The
**AUDIO_DEVICE_OUT_DEFAULT** index is the fallback used before the route settles
(cold path). Measured: that index is **not controllable from Settings** —
`readSettings` iterates `DEVICE_OUT_ALL_SET`, which does not include DEFAULT; the
DEFAULT index is set at construction to `DEFAULT_STREAM_VOLUME[]` (music=5,
ring/notif=7) and only changes via `cmd audio set-device-volume`. Proven by
setting base and speaker settings to different values and rebooting: the default
stayed frozen.

Fix in `VolumeStreamState.getIndex(int device)`: for the DEFAULT/unconfigured
device, return the **DEVICE_OUT_SPEAKER** index (the one the slider controls)
instead of the frozen DEFAULT. Changes the returned value, not the stored one
(`dumpsys` still shows `default:5`). BT/headsets have their own index → untouched.
See `patches/parche_volumen_getindex.py`. 100% in-ROM, no KernelSU.

## Call echo: proximity lives in the DSP, not a userspace lib (2026-09-02)

The phone has no physical proximity sensor — it is virtual ultrasonic (Elliptic
Labs). The "missing `libelliptic_engine.so`" theory is FALSE (measured):
`sensors.ultrasoundproximity.so` links `libssc.so`/`sensors.ssc.so`, not
libelliptic; nothing on the device loads `libelliptic_engine.so`; the real engine
runs on the **DSP/ADSP (SLPI)** over FastRPC (`adsprpcd`); the calibration already
exists (`/mnt/vendor/persist/audio/us_cal_v2.txt`) and proximity registers fine.
So the echo is an **audio (routing/AEC) issue**, needing a live-call `logcat -b all`
+ `dumpsys audio` to diagnose. Ties into the pending `Forte_elus` audio-calibration
auto-selection work.
