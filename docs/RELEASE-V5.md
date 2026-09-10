Evolution X 17.0 for Xiaomi 12 (**cupid**, sm8450, SKU ukee, main sensor IMX766) — **production `user` build**.
`ro.build.type=user` · **`ro.debuggable=0`** · **no root by default** (clean, Play-Integrity-friendly).

Full ROM: `EvolutionX-17.0-20260909--12.1-Unofficial.zip` (3.34 GiB, split in 2 parts below).
SHA-256 (full zip): `6c9629a29c774922a907ecce289c29eb5a534637b5e58f9f4cc0a08abe2515c1`

> **English first, Español después (secciones separadas).**

---

# 🇬🇧 English

## ✅ What works (verified on this flashed build)
- **Boots clean** (slot _a), **`user` / `debuggable=0`** → Play Integrity friendly, optimized ART, adb secure.
- **7 cameras** enumerate natively (Xiaomi + stock camera apps). Wide/macro auxiliaries exposed to 3rd-party apps.
- **Wi-Fi** (802.11ax, 5 GHz), **audioserver / cameraserver / system_server** alive, **0 crashes** in the crash buffer.
- **Calls / echo fixed** — dual-mic echo cancellation (`ENDFIRE`, `0xAD000009`) from source PAL/AGM/HAL.
- **Mic in apps** (GBoard / YouTube / Gemini voice) fixed.
- **Media audio** (YouTube etc.).
- **Dolby**: pumping/volume-leveler removed (the "volume goes up/down every 2-3 s" bug). The adaptive DV-Leveler steering is disabled on the *Dynamic* profile while keeping the speaker-protection compressor (no clipping at max volume). Persisted in `/data`.
- **Min media volume** very low (30 steps + speaker curve to −96 dB). **Min brightness** at the panel floor.
- **Proximity** works (hardware `TMD3719ALSPRX`, screen off in calls).

## ⚠️ Known issues / not included
- **No root by default** — by design (see "How to root" below). Enabling root will **fail Play Integrity** unless hidden.
- **KSU LKM modules don't mount** on this source ROM → every fix is integrated natively in vendor, not as a module.
- Minor: `vendor_tcmd` minijail `lseek` blocked every ~5 s (harmless log noise).
- A full **wipe/format** re-seeds the Dolby DB → the anti-pumping tweak resets (re-apply, or ask).

## 🔓 How to root (optional — KernelSU-Next)
This ROM's kernel branch **`bka-ksun`** integrates **KernelSU-Next**. To enable root:
1. Download the **KernelSU-Next Manager v3.0.1** APK from https://github.com/KernelSU-Next/KernelSU-Next/releases (the manager version **must match** the built-in kernel KSU version **32974** — newer managers show a version mismatch and root won't work).
2. Install + open it. If it reports **"Working"**, root is active — grant apps (enable "Shell" for adb root).
3. **If the stock `user` boot does not expose KSU**, flash the provided **`boot-ksu.img`**:
   `fastboot flash boot boot-ksu.img` → reboot → install Manager v3.0.1.
4. ⚠️ Root breaks **Play Integrity** (banking apps) unless you hide it. For daily banking use, keep the stock (no-root) boot.

## 🧬 Kernel source & credits (for XDA attribution)
- **ROM:** Evolution X — https://evolution-x.org
- **Kernel used:** `Evolution-X-Devices/kernel_xiaomi_sm8450`, branch **`bka-ksun`** — https://github.com/Evolution-X-Devices/kernel_xiaomi_sm8450/tree/bka-ksun (adds KernelSU-Next on top of the cupid kernel).
- **Kernel base:** `cupid-development/android_kernel_xiaomi_sm8450` — https://github.com/cupid-development/android_kernel_xiaomi_sm8450 (community cupid kernel, derived from Xiaomi's official GPL kernel source for cupid/sm8450 + Qualcomm CLO/CAF).
- **Kernel modules / devicetrees:** `Evolution-X-Devices/kernel_xiaomi_sm8450-modules` and `-devicetrees` (branch `bka`).
- **Root:** KernelSU-Next — https://github.com/KernelSU-Next/KernelSU-Next
- **Device trees:** `Evolution-X-Devices/device_xiaomi_cupid` & `device_xiaomi_sm8450-common` (branch `bka`).
- **Vendor blobs:** `TheMuppets/proprietary_vendor_xiaomi_cupid` (lineage-23.2) & `Evolution-X-Devices/vendor_xiaomi_sm8450-common` (bka).
- **MIUI camera port:** `AviumUI-Devices/device_xiaomi_miuicamera-cupid` & `vendor_xiaomi_miuicamera-cupid` (branch `avium-16.2`).
- **Upstream credits:** Xiaomi (GPL kernel source), Qualcomm / CLO (CAF), LineageOS, Google / AOSP.

## 📷 Recommended GCam (Google Camera port)
- **APK:** BSG GCam (MGC 9.x) or **LMC 8.4** — from the Celso Azevedo repo: https://www.celsoazevedo.com/files/android/google-camera/
- **Config (XML) for cupid:** https://hyperosupdates.com/hyperos/cupid/gcam and the XDA thread https://xdaforums.com/t/gcam-8-4-config-for-xiaomi-12.4503607/
- Install the APK, put the `.xml` config in the GCam configs folder, then load it from GCam settings.

## 💾 Install
1. **Reassemble** the ROM zip from the two parts:
   - Linux/Mac: `cat EvolutionX-cupid-user-20260909.zip.part-00 EvolutionX-cupid-user-20260909.zip.part-01 > EvolutionX-cupid-user-20260909.zip`
   - Windows: `copy /b EvolutionX-cupid-user-20260909.zip.part-00 + EvolutionX-cupid-user-20260909.zip.part-01 EvolutionX-cupid-user-20260909.zip`
   - Verify SHA-256 matches the value at the top.
2. Boot to **recovery** → `adb sideload EvolutionX-cupid-user-20260909.zip`
3. *(Optional — root)* `fastboot flash boot boot-ksu.img` + install KernelSU-Next Manager v3.0.1.
4. *(Optional)* `fastboot flash recovery recovery-insecure.img` — recovery with adb pre-authorized (easier rollbacks).

> Test-keys (unofficial build). Bootloader must be unlocked.

---

# 🇪🇸 Español

## ✅ Qué funciona (verificado en este build flasheado)
- **Arranca limpio** (slot _a), **`user` / `debuggable=0`** → apto para Play Integrity, ART óptimo, adb seguro.
- **7 cámaras** nativas (app de Xiaomi + apps stock). Auxiliares gran-angular/macro expuestas a apps de terceros.
- **Wi-Fi** (802.11ax, 5 GHz), **audioserver / cameraserver / system_server** vivos, **0 crashes**.
- **Llamadas / eco arreglado** — cancelación de eco de doble micro (`ENDFIRE`, `0xAD000009`) de fuente PAL/AGM/HAL.
- **Micro en apps** (GBoard / YouTube / Gemini voz) arreglado.
- **Audio multimedia** (YouTube, etc.).
- **Dolby**: eliminado el pumping/volume-leveler (el bug del "volumen sube y baja cada 2-3 s"). El DV-Leveler adaptativo se desactiva en el perfil *Dynamic* manteniendo el compresor de protección del altavoz (sin saturación al máximo). Persistido en `/data`.
- **Volumen mín. multimedia** muy bajo (30 pasos + curva a −96 dB). **Brillo mínimo** al tope del panel.
- **Proximidad** funciona (hardware `TMD3719ALSPRX`, pantalla se apaga en llamada).

## ⚠️ Problemas conocidos / no incluido
- **Sin root por defecto** — a propósito (ver "Cómo rootear" abajo). Activar root **rompe Play Integrity** salvo que lo ocultes.
- **Los módulos LKM de KSU no montan** en este ROM de fuente → todo va integrado nativo en vendor, no como módulo.
- Menor: `vendor_tcmd` bloquea `lseek` de minijail cada ~5 s (ruido de log inofensivo).
- Un **wipe/format** completo re-siembra la DB de Dolby → el ajuste anti-pumping se resetea (se reaplica, o me dices).

## 🔓 Cómo rootear (opcional — KernelSU-Next)
El kernel de este ROM (rama **`bka-ksun`**) integra **KernelSU-Next**. Para activar root:
1. Descarga el **gestor KernelSU-Next v3.0.1** (APK) de https://github.com/KernelSU-Next/KernelSU-Next/releases (la versión del gestor **debe coincidir** con la del KSU del kernel **32974** — gestores más nuevos dan mismatch y el root no funciona).
2. Instálalo y ábrelo. Si dice **"Working"/"Funcionando"**, el root está activo — concede apps (activa "Shell" para adb root).
3. **Si el boot `user` de serie no expone KSU**, flashea el **`boot-ksu.img`** incluido:
   `fastboot flash boot boot-ksu.img` → reinicia → instala el gestor v3.0.1.
4. ⚠️ El root rompe **Play Integrity** (apps de banca) salvo que lo ocultes. Para uso diario con banca, deja el boot de serie (sin root).

## 🧬 Fuente del kernel y créditos (para atribución en XDA)
- **ROM:** Evolution X — https://evolution-x.org
- **Kernel usado:** `Evolution-X-Devices/kernel_xiaomi_sm8450`, rama **`bka-ksun`** — https://github.com/Evolution-X-Devices/kernel_xiaomi_sm8450/tree/bka-ksun (añade KernelSU-Next sobre el kernel de cupid).
- **Base del kernel:** `cupid-development/android_kernel_xiaomi_sm8450` — https://github.com/cupid-development/android_kernel_xiaomi_sm8450 (kernel comunitario de cupid, derivado del código GPL oficial de Xiaomi para cupid/sm8450 + Qualcomm CLO/CAF).
- **Módulos / devicetrees del kernel:** `Evolution-X-Devices/kernel_xiaomi_sm8450-modules` y `-devicetrees` (rama `bka`).
- **Root:** KernelSU-Next — https://github.com/KernelSU-Next/KernelSU-Next
- **Device trees:** `Evolution-X-Devices/device_xiaomi_cupid` y `device_xiaomi_sm8450-common` (rama `bka`).
- **Blobs de vendor:** `TheMuppets/proprietary_vendor_xiaomi_cupid` (lineage-23.2) y `Evolution-X-Devices/vendor_xiaomi_sm8450-common` (bka).
- **Port de cámara MIUI:** `AviumUI-Devices/device_xiaomi_miuicamera-cupid` y `vendor_xiaomi_miuicamera-cupid` (rama `avium-16.2`).
- **Créditos upstream:** Xiaomi (código GPL del kernel), Qualcomm / CLO (CAF), LineageOS, Google / AOSP.

## 📷 GCam recomendada (port de Google Camera)
- **APK:** BSG GCam (MGC 9.x) o **LMC 8.4** — del repo de Celso Azevedo: https://www.celsoazevedo.com/files/android/google-camera/
- **Config (XML) para cupid:** https://hyperosupdates.com/hyperos/cupid/gcam y el hilo de XDA https://xdaforums.com/t/gcam-8-4-config-for-xiaomi-12.4503607/
- Instala el APK, pon el `.xml` en la carpeta de configs de GCam y cárgalo desde los ajustes de GCam.

## 💾 Instalación
1. **Reensambla** el zip del ROM desde las dos partes:
   - Linux/Mac: `cat EvolutionX-cupid-user-20260909.zip.part-00 EvolutionX-cupid-user-20260909.zip.part-01 > EvolutionX-cupid-user-20260909.zip`
   - Windows: `copy /b EvolutionX-cupid-user-20260909.zip.part-00 + EvolutionX-cupid-user-20260909.zip.part-01 EvolutionX-cupid-user-20260909.zip`
   - Verifica que el SHA-256 coincide con el de arriba.
2. Arranca a **recovery** → `adb sideload EvolutionX-cupid-user-20260909.zip`
3. *(Opcional — root)* `fastboot flash boot boot-ksu.img` + instala el gestor KernelSU-Next v3.0.1.
4. *(Opcional)* `fastboot flash recovery recovery-insecure.img` — recovery con adb autorizado por defecto (rollbacks más fáciles).

> Firmada con test-keys (build no oficial). El bootloader debe estar desbloqueado.
