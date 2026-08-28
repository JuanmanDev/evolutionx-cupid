# Installation guide

For the **Xiaomi 12 (cupid)** only. Do not flash this on any other model.

## Before you start

You need an unlocked bootloader, `adb` and `fastboot` on your computer, and the
phone above **50 % battery**. Back up your data: coming from another ROM you will
have to format.

One warning that matters: **the bundled audio calibration belongs to one specific
unit**. The HAL always opens the same calibration file, and this build ships the
`elus` set, which is the one this phone needs. If your unit uses the generic set,
in-call audio will be wrong (the other party hears an echo). See "If in-call
audio sounds wrong" below.

## Flashing

Unpack the release and open the `images/` folder. With the phone booted and
connected over USB:

    adb reboot fastboot

Wait for the fastbootd menu and check the computer sees it:

    fastboot devices

Flash the four partitions:

    fastboot flash system     system.img
    fastboot flash system_ext system_ext.img
    fastboot flash vendor     vendor.img
    fastboot flash odm        odm.img

Coming from another ROM, format data now:

    fastboot -w

Then reboot:

    fastboot reboot

First boot takes a few minutes.

## After first boot

Install the KernelSU module. This is what keeps the device-specific fixes alive
across ROM updates. With the phone unlocked:

    adb push modules/cupid_ajustes /data/local/tmp/
    adb shell su -c "cp -r /data/local/tmp/cupid_ajustes /data/adb/modules/ && chmod 755 /data/adb/modules/cupid_ajustes/post-fs-data.sh"
    adb reboot

The module takes care of:

  - the correct audio calibration (in-call echo cancellation),
  - camera HAL logging kept off (battery),
  - 15 volume steps,
  - forcing `ro.debuggable` to 0 on every boot.

Finally, for the 50 MP camera:

    adb install apps/Cam50Test.apk

## Recommended settings

The Xiaomi 12 status bar is tight on space because of the centred camera. Turn
the clock seconds on and something has to give: the signal icon gets collapsed
into a dot, or overlaps the Wi-Fi icon. This fits everything:

    adb shell settings put system status_bar_clock_seconds 0
    adb shell settings put system network_traffic_hidearrow 1

Also make sure the status bar paddings are not negative — if they are, the first
character of the clock and of the carrier name gets clipped:

    adb shell settings put system statusbar_extra_padding_start 0
    adb shell settings put system statusbar_extra_padding_end 0

## If in-call audio sounds wrong

Symptom: the person you call hears themselves. Check whether the DSP is running
without calibration:

    adb shell su -c "logcat -c; sleep 5; logcat -d | grep -c 'No calibration found'"

Anything above zero means your unit needs the other calibration set. Both sets
ship with the ROM, so switch it like this:

    adb shell su -c "cp /vendor/etc/acdbdata/waipio_mtp/Forte_elus_acdb_cal.acdb /data/adb/modules/cupid_ajustes/system/vendor/etc/acdbdata/Forte/Forte_acdb_cal.acdb"

or the other way round if yours needs the generic one. Reboot and check the
counter again: it must be 0.

## Going back

Always keep the images of your previous ROM. To go back, flash those four
partitions the same way. KernelSU modules live in `/data/adb/modules`; remove the
folder or drop an empty file named `disable` inside it.

## FAQ

**Can I use GCam at 50 MP?** Not on this phone. The system advertises no still
size above 4208x3120; GCam offers 50 MP because of a private Xiaomi tag, asks for
something that does not exist, and crashes. Details in the technical notes.

**Do I lose root when updating?** No: KernelSU is in the kernel and the module
lives in `/data`. What an OTA does wipe are the partition changes, which is why
the module carries copies of the important ones.

**Do banking apps work?** Depends on the app. `ro.debuggable` is 0, which was the
most obvious giveaway, but root is still visible. The kernel ships SUSFS for
hiding it, though it is not configured here.
