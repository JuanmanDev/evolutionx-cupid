# Conocimiento ROM cupid (Xiaomi 12) EvolutionX 17 / A16 — todo lo aprendido

Base de conocimiento de la sesión. Árbol: `/home/android/evolution-x` (WSL Ubuntu-AOSP).
Device: cupid, SoC sm8450 (SD8Gen1), SKU **ukee**, sensor principal **IMX766** (no IMX707).

---

## 1. ARQUITECTURA DE AUDIO (el eco)

### Causa del eco
- EvoX16 (rama vic, A15) compilaba audio de FUENTE (`hardware/qcom-caf/sm8450/audio`: PAL+AGM+HAL) → sin eco.
- EvoX17 (rama bka, A16) cambió a **blobs prebuilt de marble** (POCO F5) → marble usa `DEVICEPP_TX_VOICE_FLUENCE_SMECNS` (1 micro, 0xAD000008); cupid necesita **ENDFIRE** (2 micros, 0xAD000009). Mics de marble ≠ cupid → EC mal → eco.

### Fix del eco (aplicado)
1. Audio de FUENTE (source PAL/AGM/HAL) — requiere el ROM completo de fuente (system+vendor, sepolicy/vintf casan). Solo vendor NO basta (sepolicy mismatch → bootloop).
2. `usecaseKvManager.xml` (proprietary, el autoritativo — md5 casa): voice call handset+speaker `DEVICEPP_TX_VOICE_FLUENCE_SMECNS 0xAD000008` → `ENDFIRE 0xAD000009` (4 entradas).
3. `feature_ec_ref_capture=true` → compila ECRefDevice (referencia de eco).
4. La ACDB de cupid (Forte) tiene la calibración ENDFIRE (stock cupid la usa) → funciona.

### GKV / graph key vectors (clave para el audio)
- El PAL pide un **GKV** (graph key vector) por usecase. La **ACDB** (Forte_acdb_cal.acdb) tiene grafos indexados por GKV. Si el GKV no está → `pal_stream_start -19 (ENODEV)` + `ACDB AcdbGetUsecaseSubgraphList Error[19]: Unable to find the graph key vector`.
- GKV = 4 claves: STREAMPP (0xb1xxxxxx) + stream_config (0xab) + DEVICETX (0xa3xxxxxx) + DEVICEPP_TX (0xadxxxxxx). CKV (calibración) = sample rate (0xa5) + channels (0xa4).
- Valores clave DEVICETX: HANDSET_MIC = 0xa3000004. DEVICEPP_TX: SMECNS_voice=0xAD000008, ENDFIRE_voice=0xAD000009, ENDFIRE=0xad000003, SMECNS=0xad000002, VOICE_RECOGNITION=0xad000017.

### Fix del micro apps (GBoard/YouTube voz)
- El micro HAL va (grabadora local + transcripción sistema). Pero el reconocimiento **cloud** de Google pedía GKV `{STREAMPP 0xb1000011 + DEVICEPP 0xad000017 VOICE_RECOGNITION}` que la ACDB de cupid NO tiene → `-19` → "No se ha podido recibir el audio".
- Comparé con la grabadora que funciona: GKV `{STREAMPP 0xb1000001 + DEVICEPP 0xad000003 ENDFIRE}` → SÍ en ACDB.
- FIX: en usecaseKvManager.xml, mapear recognition a ese GKV: STREAMPP `0xB1000011`→`0xB1000001` (línea ~122, stream VOICE_RECOGNITION), DEVICEPP `0xAD000017`→`0xAD000003` (5x DevicePP VOICE_RECOGNITION). Grafo garantizado en ACDB → funciona.
- MÉTODO para depurar audio: `setprop log.tag.PAL VERBOSE; log.tag.AGM VERBOSE; log.tag.ACDB VERBOSE` → reproducir → `logcat` → ver GKV (`AGM metadata_print key:0x.. value:0x..`) + el `-19` + el ACDB error. Comparar GKV que funciona vs el que falla.

### Efectos de audio (media/DAP)
- `/vendor/etc/audio/sku_ukee/audio_effects.xml`: DAP=`libswdap.so` (CPU, NO libhwdap que necesita firmware fábrica + libdapparamstorage → dlopen falla `dolby::DapParamCache::setModified`). Spatializer=`libspatialaudio.so`. Todo bien config → media va.
- ATS (Audio Tuning Service, QACT): `libmcs` es prebuilt marble; con source osal crashea (`mcs_init->ar_log->snprintf(NULL)` SIGSEGV) → mata audioserver. FIX: gatear `ats_init_thread` en `agm/service/src/agm.c` tras `persist.vendor.audio.ats.enable` (default off) usando `__system_property_get`. ATS no es necesario.

---

## 2. CÁMARA

- Sensores los ve el KERNEL (boot-ksu, kernel bueno). Con boot de fuente NO probaban el IMX766 → boot-ksu necesario.
- El userspace (chi Xiaomi `chxcameraplatforminfoxiaomi`) construye las cámaras lógicas multicámara usando **vendor-tags Xiaomi** que proveen `vendor.xiaomi.hardware.misys@1.0/2.0.so` + `libmivsock_utils.so` + `libmicuttlefish_fs/utils.so`. Sin ellas: `Failed to get multicamera metadata tagID 851989` → 0 cámaras.
- FIX: esas 5 libs de v3 via **cc_prebuilt_library_shared** (NO PRODUCT_COPY_FILES — rechaza ELF). name `cupidcam_*`, stem=nombre real, `vendor:true`, `check_elf_files:false`. + PRODUCT_PACKAGES. En `device/xiaomi/cupid/camera-fix-libs/` (Android.bp + camera_fix_libs.mk).
- Las 10 libs AOSP (camera.device@3.x-impl, provider@2.4) YA las construye el source → NO meter (choca "multiple rules generates").
- `ro.hardware.camera=xiaomi` (default, cámara Xiaomi nativa) + `vendor.camera.aux.packagelist` (auxiliares gran-angular/macro en apps 3rd-party: aperture,GCam,snapcam,opencamera).
- El dolby C2 fantasma en VINTF NO era la causa (el análisis se equivocó; el vendor ya lo tenía quitado y seguía en 0).
- Resultado: 7 cámaras, nativo, sin el módulo KSU `qcom_camera_hal`.

---

## 3. KERNELSU

- **BUILT-IN (GKI2)** en el kernel de boot-ksu (v3.0.1, 32974). NO es LKM.
- Mismatch de versión rompe todo: kernel 32974 vs gestor v3.3.0 → sin root, módulos no montan. FIX: instalar gestor **v3.0.1 (32967)** que coincide (github.com/KernelSU-Next/KernelSU-Next release v3.0.1). Downgrade bloqueado → uninstall completo + install (módulos en /data/adb sobreviven).
- Los MÓDULOS KSU **NO montan** en este source ROM ("Metamódulo: No instalado", `ksud post-fs-data` no monta, `ksud install` falla "Text file busy"). Por eso TODO se integra NATIVO en vendor.img, no por módulos.
- Módulos KSU: **TODOS eliminados** (qcom_camera_hal, fix_media_c2, elliptic_proximity). Todo integrado nativo en vendor.img. 0 módulos = 0 bucles ksud = menos batería.
- **PROXIMIDAD FUNCIONA sin elliptic**: el sensor es hardware `TMD3719ALSPRX` (chip combo ALS+proximidad, no ultrasónico). Eventos confirmados: 5.00 (lejos)→0.00 (cerca) al tapar + confirmado en llamada real. El motor elliptic ultrasónico era proximidad REDUNDANTE → **port elliptic NO necesario** (se evita la opt más arriesgada, no se toca audio/eco).
- resetprop KSU: `/data/adb/ksu/bin/resetprop`. su binario: KSU lo da a apps concedidas (Superusuario → activar "Shell" para adb).

---

## 4. BUILD SYSTEM / GOTCHAS

- Combo lunch: `evolution_cupid-cp2a-userdebug` (producto=evolution_cupid, release=cp2a). NO lineage_cupid/bp2a.
- **PRODUCT_COPY_FILES NO admite .so** (ELF): `error: found ELF prebuilt in PRODUCT_COPY_FILES, use cc_prebuilt_library_shared`. Para libs → cc_prebuilt_library_shared + PRODUCT_PACKAGES.
- **Límite props: BUILD=120 bytes, RUNTIME=~92 bytes** (PROP_VALUE_MAX). Un valor de 104 pasa el build pero no carga en runtime (getprop vacío). Recortar a <92.
- **VINTF check** (empaquetado): caza HALs duplicados/no-declarados que bootloopearían. Ej: soundtrigger dup (manifest_ukee + manifest_non_qmaa) → vaciar el non_qmaa; dolby c2 → dolby_framework_matrix.xml debe estar en DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE.
- **/vendor 100% lleno**: no se puede editar en vivo. `sed -i`/`cp` sobre /vendor lleno TRUNCA el fichero y falla el write (ext4 delayed alloc) → config vacío → audio roto. TODO cambio va por build+flash. Restaurar solo por reflash.
- **soong RAM**: análisis soong ~24GB RSS. Host 31GB, ~13-18GB libres → thrashea swap (48GB en .wslconfig) ~1h/build. Cambio de solo un .c/prop → soong CACHEADO → build rápido (~7min). Cambio de Android.bp/BoardConfig/mk → soong re-analiza (thrash ~1h).
- **.wslconfig**: memory=26GB, swap=48GB. Liberar RAM host (cerrar apps) ayuda a que soong quepa.

## 5. FLASHEO / SEGURIDAD

- Particiones: system/vendor/product/system_ext = LÓGICAS (dinámicas, super) → fastbootd. boot/dtbo/vendor_boot/recovery/vbmeta = físicas → bootloader o fastbootd.
- Vendor: `adb reboot fastboot` → fastbootd → `fastboot flash vendor vendor.img`.
- **Recovery adb-auto** (evita "unauthorized" en recovery para rollbacks): recovery = partición dedicada (recovery_a/b), ramdisk lz4-LEGACY. Repack: unpack_bootimg → `lz4 -d` → cpio → `prop.default` `ro.adb.secure=1`→`0` + adbkey.pub en product/etc/security/adb_keys → `mkbootfs` (uid 0) → `lz4 -l -9` → `mkbootimg --header_version 4 --os_version 17.0.0 --os_patch_level 2026-08`. Flash recovery_b.
- Rollback: `vendor_working_backup.img` (v3 funcional) en scratchpad. boot-ksu.img (Ago 28, kernel bueno + KSU) en /home/android.
- vbmeta con `--disable-verity --disable-verification` (verity ya off en el device).
- Combo ROM bueno: system/vendor/product de FUENTE + boot-ksu (kernel cámara) + recovery adb-auto.

## 6. WSL GOTCHAS
- `$VAR` / `$(...)` dentro de `wsl.exe -- bash -lc '...'` frecuentemente se los come la capa Git Bash→WSL → usar scripts en fichero (Write tool) o Python inline sin `$`.
- Paths `/sdcard`, `/data` en adb desde Git Bash → MSYS los traduce a `C:/Program Files/Git/...` → usar `MSYS_NO_PATHCONV=1`.
- Mount loop de /tmp/v3 se cae entre llamadas wsl separadas → remontar en el mismo comando atómico.
