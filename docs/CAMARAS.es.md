# Cámaras — qué app para cada lente

Verificado en el móvil. Para el modo de 50 MP mira `50MP.es.md`; esto es qué
aplicación usar para cada lente física.

## Hardware (4 sensores reales — NO hay teleobjetivo)

| Sensor | Lente | Res |
|---|---|---|
| `imx766` | Principal (gran angular normal) | 50MP (12.6MP binned) |
| `ov13b10` | Ultra gran angular (0.6×) | 13MP |
| `s5k5e9` | **Macro** ("rearMacro2x") | 5MP (2592×1944) |
| `ov32b40` | Frontal | 32MP |

El "2×/5×/10×" es **zoom digital** del principal, no lentes ópticas.

## Qué app para cada lente

- **MIUICamera** (`com.android.camera`) — la más completa, **las 4 lentes**. Usa el
  pipeline vendor de Xiaomi → la única que hace el macro y los 50 MP.
  - Principal / gran angular / frontal: directo.
  - **MACRO**: toca arriba en el visor → activa el toggle **"Supermacro"** (enciende
    el sensor `s5k5e9`; acércate ~4 cm; sale 2592×1944). Desactívalo para fotos
    normales o todo dispara con la lente de 5 MP.
- **Aperture** (`org.lineageos.aperture`) — 3 lentes con buena calidad: principal +
  gran angular (0.6×) + frontal. No hace macro. (`enable_aux_cameras` no ayuda en
  cupid; revertido.)
- **Open Camera** — cicla las cámaras públicas (principal/frontal/gran angular). No
  llega al macro (sensor oculto del HAL público).
- **GCam / LMC** — SOLO principal + frontal. Su motor solo tiene tuning del sensor
  primario; no puede con aux ni macro.
- **★ MGC (BSG) + HAL qcom** — Google Camera **con gran angular REAL**. Con el HAL en
  `qcom`, MGC abre el ultra gran angular real (`ov13b10`): barra 0.7/1.0/2.1, el
  **0.7 = gran angular real** (4208×3120, no recorte). Da principal + gran angular +
  frontal. Macro no (cámara oculta del HAL).

## El HAL de cámara: `xiaomi` vs `qcom` (trade-off)

`ro.hardware.camera` decide el pipeline. Es uno **O** el otro:

- **`xiaomi`** (por defecto): MIUICamera con 4 lentes (macro Supermacro + 50 MP);
  GCam limitada.
- **`qcom`**: MGC con 3 lentes (gran angular real); **sin macro ni 50 MP**.

Cambio manual (root KernelSU):

    su 0 /data/adb/ksu/bin/resetprop ro.hardware.camera qcom
    su 0 setprop ctl.restart vendor.camera-provider-2-7
    su 0 killall cameraserver

## Módulo KernelSU auto-switch

`qcom_camera_hal` (en `/data/adb/modules/`, zip en `modules/`): un daemon
(`service.sh`) mira la app en primer plano y **cambia el HAL solo** — MIUICamera →
`xiaomi` (macro + 50 MP), MGC/GCam/Aperture/OpenCamera/**Gemini** → `qcom`. Default
`xiaomi`. Re-afirma el HAL cada segundo (no-op si ya está bien), así corrige
deriva. **Apps de terceros (Gemini, etc.) necesitan `qcom`**: en `xiaomi` salen
negras. Por eso Gemini (`com.google.android.googlequicksearchbox` +
`com.google.android.apps.bard`) está en la lista qcom; si aún así sale negra al
abrirla justo tras MIUICamera, es el parpadeo del reinicio del provider — se
recupera sola en 2-3 s. (Nota: la preview de Gemini es SurfaceView; un screenshot
sale negro aunque funcione — comprueba con la foto guardada, no con captura.) ⚠️ Cambiar de familia reinicia el camera-provider (~2-3 s) y mata la app
que se abre: al **alternar** entre MIUICamera y MGC la 1ª apertura falla, reabres y
va; dentro de la misma app, sin problema. Desactívalo (KSU manager o
`touch .../disable`) para quedarte solo en `xiaomi`.

## Notas de ROM

- `fixGcamAuxRawMismatch()` en `CameraProviderManager.cpp`: capa el RAW full-res de
  las auxiliares al área activa → arregla el crash de GCam al enumerar la frontal.
  Revertir: `setprop persist.sys.camera.gcam_aux_fix 0`.
- Gate del HAL de lentes aux: `persist.vendor.camera.privapp.list` (MIUICamera y
  Aperture dentro; GCam no).

## Resumen

- **Todas las lentes** → MIUICamera (macro = Supermacro).
- **Google Camera con gran angular** → MGC + HAL qcom (auto-switch).
- **Calidad principal+UW+frontal** → Aperture.
- **GCam/LMC** → solo principal + frontal (tope de su motor).
