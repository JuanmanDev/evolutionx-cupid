# Evolution X para Xiaomi 12 (cupid) — espejo Windows

La fuente de verdad es el arbol de WSL (`Ubuntu-AOSP`, `/home/android/evolution-x`).
Este repo guarda una copia navegable de los arboles propios y los parches que
la ROM lleva sobre los proyectos de Evolution X.

## Layout

| Ruta | Que es |
|---|---|
| `evolution-x-cupid/device/xiaomi/{cupid,sm8450-common,miuicamera-cupid}` | arboles device, rama `cupid-prod` (remoto `wsl` apunta al repo de WSL) |
| `evolution-x-cupid/vendor/xiaomi/{cupid,sm8450-common,miuicamera-cupid}` | blobs, rama `cupid-prod` (`miuicamera-cupid` es clon superficial) |
| `evolution-x-cupid/kernel/xiaomi/sm8450` | **obsoleto**: fork distinto al de WSL. Los cambios del kernel van en `patches/kernel_xiaomi_sm8450` |
| `patches/` | `git format-patch` de cada proyecto de Evolution X modificado (27). `MAP.txt` = directorio, ruta, commit base. `apply-patches.sh` los reaplica |
| `Recovery_Images/` | imagenes de recovery (no versionado) |
| `_legacy/` | scripts sueltos del intento de compilar en Windows (agosto), sin uso |

## Sincronizar desde WSL

```bash
# en WSL, tras commitear en la rama cupid-prod del proyecto X:
git -C /mnt/c/Users/Juanm/Documents/antigravity/modest-bell/evolution-x-cupid/X fetch wsl cupid-prod
git -C /mnt/c/Users/Juanm/Documents/antigravity/modest-bell/evolution-x-cupid/X checkout -B cupid-prod FETCH_HEAD
```

## Compilar (WSL)

```bash
/home/android/build_prod.sh          # lunch evolution_cupid-user, preflight, m evolution
tail -f /home/android/build_prod_latest.log
```

Variante `user` (la del build del 09/09): release-keys, `ro.debuggable=0`, sin
imagenes `*-debug.img` (`PRODUCT_BUILD_DEBUG_*_IMAGE := false`). adb queda
autorizado con la clave de `device/xiaomi/cupid/adb_keys`.

## Estado de los puntos del plan (14-09-2026)

| Punto | Estado |
|---|---|
| ACDB `Forte_elus` como `Forte/Forte_acdb_cal.acdb` | en ROM (`device.mk`, bloque `CUPID_PUBLIC`) |
| `spkcal` | prebuilt en `system_ext/bin` (blob stock A15 contra `libaudioclient` de A17: probar `spkcal -m`) |
| Goodix `/mnt/vendor/persist/goodix` 0770 | en `init.xiaomi_sm8450.rc` |
| Elliptic ultrasonido | en ROM: libs + `engine_runner`, `elliptic_uscal.sh`, `mi_ultrasound_test`, `audio-factory-test`, `ultrasound.wav`, `init.elliptic.rc`. Ya no hace falta el modulo KernelSU |
| Parche JNI 50 MP, camx logs, `privapp.list` | en ROM |
| misys@2.0 | servicio + rc + vintf en `camera-fix-libs`, sepolicy en sm8450-common |
| Dolby | se queda `libswdap` (hwdap necesita el `libdapparamstorage` stock, ver `audio_effects.xml`) |
| Volumen 30 pasos, curva | en ROM (overlay + `audio_policy_engine_stream_volumes.xml`) |
| `librmnetctl` stock | prebuilt en `vendor/qcom/opensource/dataservices` |
| `ro.debuggable` | `ro.force.debuggable=1` en el movil venia de un `vendor_boot-debug.img` flasheado; la ROM ya no genera esas imagenes. Flashear `vendor_boot.img` normal y retirar el modulo `sin_debuggable` |
| Texto de operador `ellipsize=end` | parche en `frameworks/base` (`patches/frameworks_base`) |

## Pruebas en el movil tras flashear

```bash
adb shell getprop ro.debuggable; adb shell getprop ro.force.debuggable   # ambos 0
adb shell ls -ld /debug_ramdisk /data/elliptic /mnt/vendor/persist/audio/us_cal_v2
adb shell dumpsys sensorservice | grep -i prox                          # sensor ultrasonico presente
adb shell 'su -c "logcat -d | grep -iE \"elliptic|ultrasound|acdb.*Error\""'  # sin 'No calibration found'
adb shell 'su -c spkcal -m'                                              # lee la calibracion del altavoz
adb shell 'su -c "lshal | grep misys"'                                   # vendor.xiaomi.hardware.misys@2.0::IMiSys
adb shell 'su -c "logcat -d -b all | grep avc | grep -E \"misys|sensors\""'  # denials pendientes
```

Llamada de prueba: acercar/alejar el telefono de la cara debe apagar/encender la pantalla.

## Continuidad entre builds

Lo que hace que el siguiente build sea reproducible **no** es guardar `out/`.
`out/` ocupa 150-400 GB, lleva rutas absolutas de `/home/android/evolution-x`
dentro de los `.ninja` y del cache de `soong_build`, y restaurado en otra ruta
se reconstruye entero igual. Ademas ningun producto de GitHub lo admite: 5 GB
por repo, 100 MB por fichero en git, 2 GB por fichero en LFS, y el cache de
Actions son 10 GB por repo que ademas caducan a los 7 dias.

Lo que si se versiona aqui es la receta, que ocupa unos pocos MB:

| Que | Donde | Para que |
|---|---|---|
| Manifest fijado | `snapshots/manifest-cupid-<fecha>.xml` | clava los ~800 proyectos a su SHA exacto |
| Parches propios | `patches/` (27) | los cambios que la ROM lleva encima de Evolution X |
| ROM compilada | GitHub Release, no git | asset de hasta 2 GB, con su sha256 |

```bash
# tomar snapshot del arbol actual (en WSL)
./scripts/snapshot-manifest.sh

# recrear ese arbol exacto en cualquier maquina
./scripts/restore-tree.sh snapshots/manifest-cupid-20260917.xml
cd patches && ./apply-patches.sh /home/android/evolution-x

# publicar la ROM ya compilada
./scripts/publish-release.sh /home/android/evolution-x/out/target/product/cupid/evolution-*.zip
```

### Velocidad del siguiente build

La que acorta el build es **ccache**, no GitHub. Sobrevive al borrado de `out/`
y baja un build limpio de ~6 h a ~45 min. Son decenas de GB de ficheros
diminutos con rutas absolutas: se queda siempre en disco local.

```bash
export USE_CCACHE=1
export CCACHE_DIR=/home/android/.ccache
ccache -M 50G
ccache -s            # ver tasa de acierto
```

### Disco (1 NVMe de 1908 GB, particiones C: 1011 + E: 894)

C: y E: son el mismo SSD, asi que mover cosas entre ellas reparte, no amplia.
El arbol y el vhdx de `Ubuntu-AOSP` viven en `E:\AOSP-Build\ext4.vhdx`.

- El swap de WSL y el pagefile de Windows van **siempre en el SSD**, nunca en
  Z: (`\192.168.0.209\Data`): Windows no admite pagefile en red y un corte
  cuelga o corrompe el sistema.
- Z: sirve para archivar (videos, descargas, zips de ROM ya publicados).
- El vhdx de WSL crece pero no encoge solo; se compacta con
  `wsl --manage Ubuntu-AOSP --resize` o `Optimize-VHD` tras un `wsl --shutdown`.
