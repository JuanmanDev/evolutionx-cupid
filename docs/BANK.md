# Banking apps (Deutsche Bank) on a custom ROM

*Spanish version: [`BANCO.es.md`](BANCO.es.md).*

This is a field report, measured on this device, about running the two Deutsche
Bank apps on this ROM:

- **`com.db.pbc.mibanco`** — the main banking app ("DB mibanco").
- **`com.db.coo.secureauthenticator`** — the 2FA companion ("DB Secure
  Authenticator"), used to approve logins and transfers.

The short version: **removing root makes the main app work again; the 2FA app is
blocked by hardware attestation, not by root, and that barrier cannot be lifted
on an unlocked bootloader without tampering with the bank's integrity checks —
which this project will not do.**

## Why root was the first suspect, and why it is now ruled out

With the **KernelSU** boot the apps failed. The reason is the app's own
anti-tamper layer (RASP — Runtime Application Self-Protection). The main app
prints its verdicts to the log, and with root present it flagged the device.

On the **no-root boot** (`boot-noksu.img`) the same RASP now reports a clean
device. Measured, live, on this phone:

```
RASPPlugin: notify: ROOTING Detected at observable
Json Result rooting: {"eventType":"ROOTING","data":"{DeviceRootingChanges=5, DeviceRooted=false}"}
Json Result rooting: {"eventType":"FILESYSTEM_SCANNING","data":"{SuspiciousFileDetected=false, SUPermissionDetected=false, SuidOrSgidDetected=false}"}
```

`DeviceRooted=false`, no `su`, no suspicious files, no SUID/SGID. The bank's own
detector agrees the device is not rooted. **That was the thing being detected,
and it is gone.**

`su` itself confirms it — on the no-root boot the shell has no `su` at all:

```
$ su
/system/bin/sh: su: inaccessible or not found
```

## What works

**`com.db.pbc.mibanco` (main app): works.** It launches, its RASP runs the full
sweep (root, filesystem, screen-mirroring, screen-reader, keyboard), calls
SafetyNet, and proceeds to load the user profile and its normal screens. No crash,
no block. The window is `FLAG_SECURE` (screenshots come out black — that is the
app hiding itself from capture, not a fault).

Two **advisory** flags the RASP raises — neither blocks the app:

- `UntrustedScreenreaderPresent=true` — caused by **Lawnchair's accessibility
  service** (`app.lawnchair/...LawnchairAccessibilityService`), the only enabled
  accessibility service. Lawnchair uses it for gestures such as double-tap to
  lock. If you want that flag gone, disable Lawnchair's accessibility service in
  *Settings → Accessibility* (you lose the gesture). The app runs either way.
- `KeyboardTrusted=false` for **Gboard** — the RASP does not trust third-party
  keyboards for sensitive entry and prefers its own in-app keypad. Nothing to fix;
  it is informational.

## What does not work, and why

**`com.db.coo.secureauthenticator` (2FA app): blocked.** It launches and stays on
its splash screen indefinitely. It never crashes and never shows a login screen.
The cause is **not** root — it is the app's attestation layer failing:

- Its Google Play Services attestation call returns
  `ConnectionResult{statusCode=DEVELOPER_ERROR}`.
- It runs a native security sandbox in an **isolated process** that is repeatedly
  reaped; the main process then loops on a one-way binder call that fails with
  `error -74` (`EBADMSG`) — "Too many transaction errors, throttling".
- Its anti-bypass code specifically watches for **TrickyStore** (an attestation
  spoofing tool) across GMS, Play Store and the bank packages, and refuses to
  proceed when the environment cannot produce a genuine, passing attestation.

On an **unlocked bootloader** — which every custom ROM requires — Play Integrity /
key attestation cannot return a *device*-integrity verdict. The main app tolerates
that and falls back to its own checks; the 2FA app does not. It hard-requires a
passing hardware attestation.

### Why it "worked on EvolutionX 16"

Most likely the Secure Authenticator was an **older version** then, before
Deutsche Bank tightened it to hard-require device integrity, or 2FA was being
done another way (photoTAN by a different route, or SMS). Same unlocked bootloader,
stricter app today. Worth confirming by comparing the installed app version.

## What this project will not do

Making the 2FA app pass would require **faking hardware attestation** — installing
TrickyStore plus a valid (usually leaked) keybox so the app believes the bootloader
is locked. That is deliberately circumventing a bank's integrity control on a
financial app, and it is out of scope here. Not patching the APK either.

## Realistic options

1. **Use the main app for viewing/most operations**, and complete 2FA by a method
   that does not depend on the Secure Authenticator's attestation (e.g. photoTAN
   on a second, stock device, or SMS-TAN if your account allows it).
2. **A second, stock (locked-bootloader) phone** for the Secure Authenticator only.
   This is the clean way to keep both a custom ROM here and working DB 2FA.
3. **Return this phone to stock MIUI/HyperOS and relock the bootloader** if full DB
   support on *this* device is a hard requirement. That gives up the custom ROM.
4. **Certify this device with Google** (submit the GSF Android ID at
   `google.com/android/uncertified`). This can fix *basic* integrity and some GMS
   errors, but **not** the device/strong integrity the 2FA app needs on an unlocked
   bootloader. Harmless to try; do not expect it to unblock the authenticator.

## Which boot am I on?

- On the **no-root boot** (`boot-noksu.img`), `su` prints
  `inaccessible or not found`, and the main DB app's RASP reports
  `DeviceRooted=false`. This is the boot to use for banking.
- To switch: `fastboot flash boot boot-noksu.img` (or use
  `scripts/flashear_todo.sh --no-ksu`). To go back to root:
  `fastboot flash boot boot-ksu.img`. Your apps and data are untouched; only the
  boot image (kernel) changes.
