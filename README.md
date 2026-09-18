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

## Estado de los sistemas y calibraciones (18-09-2026)

| Sistema / Componente | Estado | Detalle técnico |
|---|---|---|
| **Calibración de Audio (ACDB)** | **En ROM** | `Forte_elus` instalado como `Forte/Forte_acdb_cal.acdb` en `device.mk` (bloque `CUPID_PUBLIC`). Evita que el HAL cargue el set genérico y el DSP arroje `No calibration found`, eliminando por completo el eco acústico en llamadas. |
| **Calibración Altavoz Smart PA (`spkcal`)** | **En ROM** | Prebuilt en `system_ext/bin` (añadido en `cupid-vendor.mk` y `Android.bp`). Permite calibrar la impedancia del amplificador Cirrus CS35L41/45 (`su -c spkcal -c`) y leer su estado (`spkcal -m`). |
| **Proximidad Ultrasónica (Elliptic Labs)** | **En ROM (`/vendor`)** | cupid carece de sensor óptico; usa ultrasonidos (`sensors.ultrasoundproximity`). Integrados: `libelliptic_engine.so`, `libelliptic_serializer.so`, `engine_runner`, `elliptic_uscal.sh`, `audio-factory-test`, `mi_ultrasound_test`, `ultrasound.wav` e `init.elliptic.rc` (crea `/mnt/vendor/persist/audio/us_cal_v2` y `/data/elliptic` con permisos 0775). **Ya no se necesita el módulo externo de KernelSU**. |
| **Calibración de Huella Óptica (Goodix FOD)** | **En ROM** | Permisos fijados a `0770 system system` para `/mnt/vendor/persist/goodix` en `init.xiaomi_sm8450.rc` para blindar los datos de calibración de fábrica. Coordenadas UDFPS `540|2163|107` y handler LHBM para iluminación de desbloqueo. |
| **Volumen y Curvas de Audio** | **En ROM** | 30 pasos multimedia (`ro.config.media_vol_steps=30`) y curva inferior a −96 dB en `audio_policy_engine_stream_volumes.xml`. Efecto Dolby DAP por software (`libswdap`) para evitar saltos bruscos de volumen provocados por el nivelador dinámico. |
| **Cámara 50 MP y CamX** | **En ROM** | Parche de offset JNI (`08 A9 40 F9` en `libcamera_algoup_jni.xiaomi.so` para resolver fotos verdes), logging de CamX a `0x1` (ahorra CPU, batería y 100 MB de logs residuales) y `privapp.list` configurado con `com.cupid.cam50,org.lineageos.aperture,com.android.camera`. |
| **Cámara Virtual (`misys@2.0`)** | **En ROM** | Servicio + rc + vintf en `camera-fix-libs`, sepolicy en `sm8450-common` para procesado paralelo en MiuiCamera. |
| **Datos Móviles (`librmnetctl`)** | **En ROM** | Prebuilt de HyperOS stock en `vendor/qcom/opensource/dataservices` (exporta `rmnetctl_init`). |
| **Integridad (`ro.debuggable`)** | **En ROM** | Resuelto en user build (`ro.debuggable=0`, `ro.force.debuggable=0`) sin imágenes debug. Permite pasar Play Integrity manteniendo root vía KernelSU si se flashea `boot-ksu.img`. |
| **Texto de Operador en Lockscreen** | **En ROM** | Parche en `frameworks/base` cambiando `marquee` por `ellipsize=end` (evita que se corte la primera letra del operador). |

## Pruebas en el móvil tras flashear

```bash
# 1. Comprobar depuración e integridad
adb shell getprop ro.debuggable; adb shell getprop ro.force.debuggable   # ambos deben ser 0

# 2. Comprobar directorios de calibración
adb shell ls -ld /debug_ramdisk /data/elliptic /mnt/vendor/persist/audio/us_cal_v2 /mnt/vendor/persist/goodix

# 3. Comprobar sensor ultrasónico de proximidad
adb shell dumpsys sensorservice | grep -i prox                          # debe listar el sensor ultrasónico
adb shell 'su -c "logcat -d | grep -iE \"elliptic|ultrasound|acdb.*Error\""'  # sin 'No calibration found'

# 4. Probar lectura de calibración Smart PA Cirrus
adb shell 'su -c spkcal -m'                                              # lee la calibración del altavoz

# 5. Comprobar servicio MiSys
adb shell 'su -c "lshal | grep misys"'                                   # vendor.xiaomi.hardware.misys@2.0::IMiSys
adb shell 'su -c "logcat -d -b all | grep avc | grep -E \"misys|sensors\""'  # verificar si hay denials
```

Llamada de prueba: acercar y alejar el teléfono de la cara debe apagar y encender la pantalla con el sensor ultrasónico.

---

## Continuidad, Respaldo en GitHub y Ahorro de Tiempo

Lo que hace que el siguiente build sea reproducible **no** es almacenar los 150-400 GB de `out/`. `out/` lleva rutas absolutas y no es portable entre máquinas ni admisible en repositorios.

La estrategia de respaldo en GitHub divide el sistema en dos capas:
1. **La Receta y Fuentes (Git — rama `cupid-mirror`):** Ocupa pocos megabytes y clava los 1.251 proyectos al SHA exacto junto con los 27 parches del sistema.
2. **Los Binarios Compilados (GitHub Releases):** Hospedados en [JuanmanDev/evolutionx-cupid Releases](https://github.com/JuanmanDev/evolutionx-cupid/releases), donde no hay coste de almacenamiento local.

### Recuperar imágenes compiladas desde GitHub en segundos

Cuando necesites cualquier binario sin compilar:

```powershell
# Descargar el boot con KernelSU (v5):
gh release download v5 -R JuanmanDev/evolutionx-cupid -p "boot-ksu.img"

# Descargar el recovery pre-autorizado con adb:
gh release download v5 -R JuanmanDev/evolutionx-cupid -p "recovery-insecure.img"

# Descargar la ROM completa lista para flashear:
gh release download v5 -R JuanmanDev/evolutionx-cupid -p "EvolutionX-cupid-user-20260909.zip.part-*"
copy /b EvolutionX-cupid-user-20260909.zip.part-00 + EvolutionX-cupid-user-20260909.zip.part-01 EvolutionX-cupid-user-20260909.zip
```

### Reproducir o restaurar el árbol completo desde cero

Si necesitas compilar en otra máquina o tras vaciar el entorno local:

```bash
# 1. Clonar el repositorio espejo en la rama cupid-mirror:
git clone -b cupid-mirror https://github.com/JuanmanDev/evolutionx-cupid.git
cd evolutionx-cupid

# 2. Restaurar el árbol Evolution X al snapshot exacto (1.251 proyectos clavados a su SHA):
./scripts/restore-tree.sh snapshots/manifest-cupid-20260918.xml /home/android/evolution-x

# 3. Aplicar los 27 parches del sistema:
cd patches && ./apply-patches.sh /home/android/evolution-x

# 4. Compilar:
/home/android/build_prod.sh
```

---

## Gestión de Disco y Limpieza Segura

Para liberar espacio físico en el disco NVMe:

### 1. Borrado local seguro (recuperable desde GitHub)
- En `C:\Users\Juanm\Downloads\evo17\`: se pueden eliminar las carpetas `release-assets\`, `release-v2\` y `evo-0820.zip` (libera más de **11 GB**). Todos los zips e imágenes correspondientes están respaldados en las Releases `v1`, `v2` y `v5` de GitHub.
- En `modest-bell\Recovery_Images\`: imágenes auxiliares ya presentes en releases.

### 2. Limpieza intermedia en WSL (`out/`)
Tras publicar un build, no hace falta conservar los objetos temporales:
```bash
cd /home/android/evolution-x
m installclean
```
Esto recupera más de 100 GB en WSL manteniendo la configuración de Soong y la base para compilaciones incrementales.

### 3. Mantener CCache siempre en disco local
El caché de Ccache (`/home/android/.ccache`) ocupa ~50 GB y sobrevive al borrado de `out/`. **No debe borrarse**, ya que reduce el tiempo de compilación limpia de 6 horas a solo 45 minutos.

```bash
export USE_CCACHE=1
export CCACHE_DIR=/home/android/.ccache
ccache -M 50G
ccache -s            # ver tasa de acierto
```

### 4. Compactar el archivo VHDX de WSL
WSL expande dinámicamente el disco virtual `E:\AOSP-Build\ext4.vhdx`, pero tras borrar archivos grandes no se reduce solo. Para recuperar el espacio físico en Windows:
1. En PowerShell: `wsl --shutdown`
2. En PowerShell como Administrador:
   ```powershell
   Optimize-VHD -Path "E:\AOSP-Build\ext4.vhdx" -Mode Full
   ```
   *(o `wsl --manage Ubuntu-AOSP --resize` en versiones recientes de WSL)*.
