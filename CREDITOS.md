# Créditos y agradecimientos · Credits

Esta compilación no existiría sin el trabajo de mucha gente. Gracias de verdad.
· *This build would not exist without the work of many people. Thank you.*

## Evolution X

Al **equipo de [Evolution X](https://github.com/Evolution-X)** por la ROM base:
por mantener un Android 17 limpio, rápido y con buen gusto, y por hacer todo su
trabajo público para que cualquiera pueda partir de él. Esta es una compilación
**no oficial**; todo mérito de la base es suyo, y los fallos de esta variante no
son responsabilidad suya — no les reportéis bugs de aquí.

· *Thanks to the **Evolution X team** for the base ROM and for keeping their work
open. This is an **unofficial** build; the base is their credit, and bugs in this
variant are not their responsibility — do not report them upstream.*

## Mantenedores del Xiaomi 12 (cupid)

A **quienes han mantenido el árbol de dispositivo del Xiaomi 12 (`cupid`)** antes
que nadie: el device tree, el vendor y el kernel de `cupid`/`sm8450` sobre los que
se apoya todo esto vienen de su esfuerzo, muchas veces sin reconocimiento y en su
tiempo libre. Sin ese trabajo previo no habría por dónde empezar.

· *To **everyone who has maintained the Xiaomi 12 (`cupid`) device tree** before —
the `cupid`/`sm8450` device, vendor and kernel trees this builds on are their work,
often unpaid and in their free time. None of this starts without them.*

## Fuente del kernel · Kernel source (GPLv2)

Cumplimiento GPLv2 — código fuente del kernel usado para compilar esta ROM/kernel:
· *GPLv2 compliance — kernel source used to build this ROM/kernel:*

- **Kernel usado · Kernel used:** [`Evolution-X-Devices/kernel_xiaomi_sm8450`](https://github.com/Evolution-X-Devices/kernel_xiaomi_sm8450/tree/bka-ksun) — rama/branch **`bka-ksun`** (integra KernelSU-Next · integrates KernelSU-Next).
- **Base del kernel · Kernel base:** [`cupid-development/android_kernel_xiaomi_sm8450`](https://github.com/cupid-development/android_kernel_xiaomi_sm8450) — derivado del código GPL oficial de Xiaomi para cupid/sm8450 + Qualcomm CLO/CAF · *derived from Xiaomi's official GPL kernel source for cupid/sm8450 + Qualcomm CLO/CAF.*
- **Módulos y devicetrees · Kernel modules & devicetrees:** [`kernel_xiaomi_sm8450-modules`](https://github.com/Evolution-X-Devices/kernel_xiaomi_sm8450-modules) · [`kernel_xiaomi_sm8450-devicetrees`](https://github.com/Evolution-X-Devices/kernel_xiaomi_sm8450-devicetrees) (rama/branch `bka`).
- **Device trees:** [`device_xiaomi_cupid`](https://github.com/Evolution-X-Devices/device_xiaomi_cupid) · [`device_xiaomi_sm8450-common`](https://github.com/Evolution-X-Devices/device_xiaomi_sm8450-common) (rama/branch `bka`).
- **Blobs de vendor · Vendor blobs:** [`TheMuppets/proprietary_vendor_xiaomi_cupid`](https://github.com/TheMuppets/proprietary_vendor_xiaomi_cupid) (lineage-23.2) · [`vendor_xiaomi_sm8450-common`](https://github.com/Evolution-X-Devices/vendor_xiaomi_sm8450-common) (bka).
- **Port de cámara MIUI · MIUI camera port:** [`AviumUI-Devices/device_xiaomi_miuicamera-cupid`](https://github.com/AviumUI-Devices/device_xiaomi_miuicamera-cupid) · [`vendor_xiaomi_miuicamera-cupid`](https://github.com/AviumUI-Devices/vendor_xiaomi_miuicamera-cupid) (avium-16.2).
- **Upstream:** Xiaomi (código GPL del kernel · GPL kernel source), Qualcomm / CLO (CAF), LineageOS, Google / AOSP.

## Root y ocultación · Root & hiding

- **[KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next)** — el root
  integrado en el kernel. · *the root integrated in the kernel.*
- **[SuSFS](https://gitlab.com/simonpunk/susfs4ksu)** — la base para ocultar el
  root a las apps que lo detectan. · *the base for hiding root from apps that detect it.*

## Base de dispositivo

- **[LineageOS](https://github.com/LineageOS)** — el árbol de dispositivo de
  `cupid` del que parte el de esta ROM.
- **Qualcomm CAF / CodeAurora** — HAL de cámara (CamX/CHI) y blobs de la
  plataforma sm8450.

## Y a la comunidad

A los foros (XDA, Telegram) y a la gente que documenta, mide y comparte: buena
parte de lo que hay en `docs/` se apoya en pistas de otros que se molestaron en
escribir lo que encontraron. Aquí se ha intentado devolver el favor midiéndolo
todo y contándolo sin adornos.

· *And to the community — XDA, Telegram, and everyone who documents and shares.
Much of what is in `docs/` builds on other people's notes. This repo tries to pay
it back by measuring everything and writing it down plainly.*
