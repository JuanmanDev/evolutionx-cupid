# Cambios respecto al árbol oficial

Lista de todo lo tocado, con el fichero donde vive y el porqué en una línea. El
detalle completo, con las medidas, está en `NOTAS.md`.

## Árbol de dispositivo (`device/xiaomi/cupid`)

| Fichero | Cambio |
|---|---|
| `device.mk` | Calibración de audio `Forte_elus` instalada en la ruta que abre el HAL (`acdbdata/Forte/`). Sin esto no hay cancelación de eco. |
| `device.mk` | `ro.debuggable=1` retirado. |
| `device.mk` | `persist.vendor.camera.privapp.list` con el paquete de la cámara de 50 MP. |
| `device.mk` | `Cam50Test` añadido a los paquetes del producto. |
| `evolution_cupid.mk` | Intento (**sin efecto todavía**) de filtrar el `su` de AOSP de los paquetes de depuración. Ver "Pendientes". |
| `overlay/Frameworks/res/values/config.xml` | 15 pasos de volumen para notificación y timbre, en vez de 7. |
| `apps/Cam50Test/` | Cámara de 50 MP (aplicación nueva). |
| `apps/MedidorNivel/` | Medidor de nivel de sonido, para comprobar volúmenes con números. |
| `NOTAS-RENDIMIENTO.md` | Todo lo medido y aprendido, para no repetir investigaciones. |

## Blobs del vendor (`vendor/xiaomi/cupid`)

| Fichero | Cambio |
|---|---|
| `vendor/etc/camera/camxoverridesettings.txt` | Log del HAL de cámara a solo errores y sin volcado a disco. El original queda como `.con-logs`. |

## AOSP

| Fichero | Cambio |
|---|---|
| `frameworks/av/.../audio_policy_volumes.xml` | Curva de volumen de notificación y timbre por altavoz: el tramo bajo llega a −50 dB en vez de −29,7. |
| `frameworks/av/.../CameraProviderManager.{cpp,h}` | Función nueva `addQuadCfaFullSizeJpeg()`: anuncia el tamaño completo del sensor como tamaño de foto. **Apagada por defecto** (`persist.sys.camera.qcfa_jpeg`), porque con ella las apps que reservan varios búferes tumban el HAL. |
| `frameworks/av/.../{Aidl,Hidl}ProviderInfo.cpp` | Llamada a la función anterior. |

## Fuera del árbol (viven en el móvil)

| Dónde | Qué |
|---|---|
| `/data/adb/modules/cupid_ajustes` | Módulo de KernelSU que replica los ajustes de `vendor` y `odm` y fuerza `ro.debuggable=0`. Es lo que hace que nada de esto se pierda al actualizar. |

## Cambios que se probaron y se descartaron

  - **Vía estándar de Android para 50 MP** (`SENSOR_PIXEL_MODE_MAXIMUM_RESOLUTION`):
    el HAL acepta la sesión pero devuelve un reescalado, con menos detalle que una
    foto de 12,6 MP ampliada.
  - **Instalar los dos juegos de calibración de audio con su nombre propio**: parece
    lo correcto, pero el HAL abre siempre `Forte/` y acabó cargando el genérico,
    lo que reintrodujo el eco en llamada.
  - **Parchear el reloj y el nombre del operador** para que no se cortaran: el
    recorte venía de un ajuste del usuario con relleno negativo, no del layout.
  - **Corregir el color de los 50 MP con ganancias**: el desvío depende del tono y
    el HAL ignora las ganancias en esa ruta.

## Pendientes

  - **Quitar el `su` de AOSP.** Se intento filtrarlo con
    `PRODUCT_PACKAGES_DEBUG := $(filter-out su,$(PRODUCT_PACKAGES_DEBUG))`, primero
    en `device.mk` y luego al final de `evolution_cupid.mk`, y en ninguno de los dos
    sitios surte efecto: sigue apareciendo en `installed-files.txt` y en el movil.
    Lo anade `base_system.mk` (solo cuando `LINEAGE_BUILD` esta vacio) y la
    combinacion de variables de producto se resuelve despues. Vias que quedan:
    compilar la variante `user` en vez de `userdebug`, definir `LINEAGE_BUILD`, o
    taparlo desde el modulo de KernelSU montando un fichero vacio encima.
  - **Ocultar el root** para las apps que lo detectan. El kernel ya trae SUSFS
    (`CONFIG_KSU_SUSFS=y`), pero no esta configurado.
  - **Medir el consumo en reposo** con el movil quieto una hora y sin ADB
    conectado; las medidas hechas hasta ahora estaban falseadas por la propia
    instrumentacion.
  - **Seleccion automatica de la calibracion de audio**, en vez de fijar la de esta
    unidad. Es lo unico que impide compartir la ROM sin riesgo de que a otro le
    salga el eco en llamada.

## 26 de agosto: los 50 MP funcionan, en JPEG y en RAW

La cámara que trae la ROM hace fotos de 8192×6144 con su botón normal, y el DNG
que guarda es un RAW de verdad (0 % de ceros, las 6144 filas con datos). Hasta
ahora ese mismo fichero salía con tres cuartas partes en negro.

Hicieron falta cuatro piezas, todas en el servicio de cámara. La receta completa,
con las mediciones, está en `docs/50MP.md`. En resumen:

- **Modo de sesión `0x80F3`**, no el `36868` que da por bueno la comunidad: en
  este modelo ese valor hace que el HAL rechace la sesión.
- **Estar en `persist.vendor.camera.privapp.list`**: fuera de esa lista el HAL
  entrega 1920×1440 con el mismo código.
- **El búfer del JPEG bien dimensionado**: el HAL declaraba 19,8 MB para fotos
  que ocupan hasta 42. De paso, esto desmonta el supuesto límite de "cuatro
  imágenes en vuelo", que nunca existió.
- **Duraciones por debajo del umbral de 20 fps**, o el tamaño queda fuera de la
  lista que consultan las aplicaciones. El HAL ya publicaba RAW a resolución
  completa de fábrica, pero a 100 ms por fotograma.

### Lo que sigue sin poder hacerse

- Google Camera a 50 MP: pide RAW y YUV, nunca JPEG, y reserva entre 22 y 37
  imágenes. A esa resolución no se sostiene, y su código no es público.
- YUV a resolución completa: el HAL muere.
- La cámara de Xiaomi: arranca y se cierra. La causa **no** es la que estaba
  documentada (binarios de Android 15) sino SELinux, que le deniega ejecutar el
  enlazador para precargar sus librerías. Queda a medio resolver; el detalle
  está en `device/xiaomi/miuicamera-cupid/NOTAS.md` del árbol.
