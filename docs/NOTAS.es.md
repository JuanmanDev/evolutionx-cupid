# Notas de rendimiento y consumo en cupid

Cosas medidas en el movil, con el porque. Sirven para no volver a investigarlas.

## El HAL de camara venia con el log a tope (arreglado)

`vendor/etc/camera/camxoverridesettings.txt` traia de fabrica:

    logInfoMask=0x10098
    logConfigMask=0x80
    overrideLogLevels=0x1F      <- todos los niveles, VERBOSE incluido
    enableTxtLogging=1          <- vuelca ademas a /data/vendor/camera
    offlineLogNumber=14

Con eso, cada peticion de captura escribia decenas de lineas (CamX, GME,
STATS_AEC, STATS_AF...). Grabando video son decenas por fotograma, con su CPU y
su escritura a disco. Xiaomi tiene al lado un `camxoverridesettingsOfCloseLog.txt`,
o sea que ellos mismos lo apagan cuando quieren.

Ahora esta en solo errores (`overrideLogLevels=0x1`, mascaras a 0,
`enableTxtLogging=0`). El original quedo en
`camxoverridesettings.txt.con-logs`. **No cambia ningun parametro de imagen.**

Medido con la camara abierta 8 segundos:
  - antes: cientos de lineas por segundo
  - despues: 6 lineas en total

Ademas se borraron 98 MB que el volcado de texto habia dejado en
`/data/vendor/camera/offlinelog` (14 ficheros de ~7 MB).

Queda una duda: aparecieron ficheros `Camx_OfflineLog_*.txt` con hora posterior
al cambio, y no encontre en los blobs de vendor la clave que gobierna ese
registro "offline" (`offlineLoggerEnableRealTimeLog` y
`offlineLoggerEnableBackupLog` ya estan en FALSE, y ningun binario de vendor
contiene la cadena `OfflineLog`). Conviene mirar tras usar la camara si
`/data/vendor/camera/offlinelog` vuelve a crecer.

## /vendor esta al 100% y no admite editar nada en caliente

    /dev/block/dm-4  1.9G  1.9G  6.0M  100%  /vendor

Aunque `df` diga que quedan 6 MB, no acepta escribir ni 10 KB: al intentar
copiar el fichero de ajustes del HAL, `cp` y `cat` fallan con "No space left on
device" **y dejan el destino a 0 bytes**. Es decir, editar algo de /vendor en el
movil no solo no funciona: destruye el fichero.

Si hace falta cambiar algo de /vendor:
  1. cambiarlo en el arbol,
  2. `m vendorimage`,
  3. `fastboot flash vendor` desde fastbootd (`adb reboot fastboot`).
Como parche temporal se puede servir el fichero desde /data con
`mount -o bind`, poniendole antes la etiqueta
`u:object_r:vendor_configs_file:s0`; eso se deshace al reiniciar.

## La rejilla de puntos en las capturas era Smart Pixels

Sintoma: las capturas de pantalla (y la pantalla misma) con una rejilla de
puntos negros. Causa: `Settings.Secure.smart_pixel_filter_enabled=1` con
`smart_pixel_filter_percent=25`, que apaga uno de cada cuatro pixeles para
ahorrar bateria en OLED. La capa se ve en SurfaceFlinger como
`VRI-SmartPixelFilter` a pantalla completa, y por eso sale tambien en las
capturas.

Medido en una captura: una de las cuatro posiciones (fila par, columna par)
estaba negra al 100 % (30,5 % de negros en total). Tras apagarlo, las cuatro
posiciones quedan igual (7,3 %) y la capa desaparece.

No se activa solo con la bateria baja: no hay ninguna regla de ahorro que lo
enciendan en el codigo. Se enciende desde su tesela de ajustes rapidos
("Smart Pixels"), asi que si vuelve la rejilla es que se ha pulsado.

## Iconos de la barra de estado (en investigacion)

  - El nombre del operador se ve cortado ("odafone ES") porque
    `keyguard_carrier_text` usa `ellipsize="marquee"`: el texto no cabe y se
    desplaza. Es solo la pantalla de bloqueo y es cosmetico.
  - El punto rojo que parpadea rapido junto a los iconos encaja con el
    `PulsingDot` de la barra dinamica de AX (`RedAccent 0xFFFF3B30`, pulso de
    550 ms), que se usa para grabacion, temporizador y alarma. Pendiente de
    confirmar viendolo en marcha.
  - El solape entre el icono de cobertura y el de wifi: pendiente de reproducir
    con la pantalla desbloqueada. La barra va justa de espacio (de ahi la
    marquesina del operador), y `StatusIconContainer` convierte iconos en puntos
    cuando no caben, animando las traslaciones; ahi es donde puede haber pisada.

## La barra de estado no da para tanto (medido)

En la pantalla de inicio caben, como mucho, cuatro de estos cinco: velocidad de
red, icono de alarma, cobertura, wifi, bateria y reloj. Cuando no cabe algo,
`StatusIconContainer` degrada iconos a un punto, y lo que caia era **el icono de
cobertura**: por eso se veia un punto donde deberian estar las barras de senal.
Ademas el reloj con segundos cambia de ancho cada segundo, asi que la barra se
recolocaba continuamente y el punto aparecia y desaparecia muy rapido, que es
justo el sintoma del que se quejaba el usuario.

Medido, con el reloj a la derecha:

  - segundos ON  + flechas del indicador de red ON  -> la cobertura pasa a punto
    y desaparecen la alarma y la velocidad de red
  - segundos OFF + flechas ON                       -> se ve todo menos el reloj
  - segundos OFF + flechas OFF                      -> **se ve todo**

Los segundos cuestan unos 70 px ("0:28:06" frente a "0:28") y las flechas del
indicador de red 12dp (el ancho de esa vista pasa de 30dp a 18dp, y sigue
mostrando la velocidad). Configuracion que deja verlo todo:

    settings put system status_bar_clock_seconds 0
    settings put system network_traffic_hidearrow 1

El reloj se puede mover con LineageSettings `status_bar_clock`
(0 = derecha, 1 = centro, 2 = izquierda), pero a la izquierda compite con el
nombre del operador, asi que no gana nada.

## El primer caracter se cortaba en dos vistas

  - **Reloj a la izquierda**: se leia "):25" en vez de "0:25". La medida
    `status_bar_left_clock_starting_padding` estaba a 0dp, y como el reloj va con
    `includeFontPadding` a false, el glifo se sale del ancho medido y el
    contenedor lo recorta. Subida a 2dp.
  - **Nombre del operador en la pantalla de bloqueo**: se leia "odafone ES". No
    era falta de margen (16dp, y el contenido empieza en la columna 52 de 1080)
    ni una marquesina en movimiento (el texto esta quieto en seis capturas
    seguidas): era `ellipsize="marquee"`, que enciende los bordes de desvanecido
    del TextView y se come el principio del texto. Cambiado a `ellipsize="end"`.

## El punto rojo que pulsa

Encaja con el `PulsingDot` de la barra dinamica de AX (`RedAccent 0xFFFF3B30`,
pulso de 550 ms), que se usa para grabacion, temporizador y alarma. El punto
gris/blanco que sale donde deberia estar la cobertura es otra cosa: el de
`StatusIconContainer` por falta de sitio (ver arriba).

## Los 50 MP tienen una via estandar, sin hacks de Xiaomi

Este sensor se declara con la capacidad `ULTRA_HIGH_RESOLUTION_SENSOR` y publica
`android.scaler.availableStreamConfigurationsMaximumResolution` con 8192x6144 en
RAW10 (37), RAW16 (32) y RAW privado (36), ademas de `android.sensor.pixelMode` y
`activeArraySizeMaximumResolution`. O sea que se puede pedir la resolucion
completa por el camino oficial de Android (API 31): sesion **normal** y
`SENSOR_PIXEL_MODE_MAXIMUM_RESOLUTION` en la peticion, sin operating mode 0x80F3
ni etiquetas propietarias.

Probado ya en el movil (`persist.cam50.pixelmode 1`): la sesion se configura y
guarda un JPEG de 8192x6144. Queda comparar con luz si tiene el detalle real y
si el color sale bien, que es lo que falla por la via propietaria (el remosaico
del HAL no tiene los datos de crosstalk del modulo). Por esa via el remosaico lo
hace el sensor y el color lo procesa el ISP como en cualquier foto, asi que es la
candidata a ser la buena.

Nota: en modo `pixelmode` la sesion de previa no se recupera bien despues del
disparo ("no se configuro la sesion de previa"); hay que arreglarlo en la app.

Ah, y el flujo RAW de 8192x6144 **por la via propietaria 0x80F3 el HAL lo
rechaza** (`onConfigureFailed`), asi que si se quiere RAW hay que pedirlo por la
via estandar.

## Que dan de si los 50 MP (medido con luz, 24-08)

Tres versiones de la misma escena (movil fijo, interior con ventana):

| version                                   | dif. tras reescalar | detalle | luz media | quemado |
|-------------------------------------------|--------------------:|--------:|----------:|--------:|
| reescalado (sin la etiqueta de remosaico)  |              0,0044 |  0,0246 |      89,3 |  2,73 % |
| via estandar (SENSOR_PIXEL_MODE maximo)    |              0,0040 |  0,0197 |      86,4 |  2,03 % |
| via de Xiaomi (xiaomi.remosaic.enabled)    |              0,0097 |  0,0475 |     137,8 |  3,19 % |

Lecturas:

  - **La via estandar de Android no sirve para lo que buscamos.** El HAL declara
    `ULTRA_HIGH_RESOLUTION_SENSOR` y acepta la sesion, pero lo que devuelve no
    tiene mas informacion que una foto de 12,6 MP ampliada: se queda incluso por
    debajo de la referencia. Eso si, el color y la exposicion salen bien.
  - **La via de Xiaomi es la unica que sube**, pero al mirar al 100% la misma
    zona (una rejilla de aire acondicionado, que es lo que mas textura tiene de
    la escena) se ve que buena parte de ese "detalle" son **artefactos**: la
    rejilla sale con franjas azules y moradas, mientras que en la version
    reescalada la misma rejilla se ve limpia y gris. Y toda la foto lleva un
    tinte rosa/lila: una pared que la otra via saca beige (R/G 1,23, B/G 0,86)
    ella la saca rosa (R/G 1,38, B/G 1,05).
  - `xiaomi.pureView.enabled` **no aporta nada**: quitandola y dejando solo
    `xiaomi.remosaic.enabled` sale exactamente igual (detalle 0,0455, luz 137,2).
    O sea que quien manda es la etiqueta de remosaico.
  - El color de esa ruta **no se puede corregir desde la app**: copiar las
    ganancias y la matriz de la vista previa no cambia el resultado (el HAL las
    ignora), y con ganancias globales en post tampoco, porque el desvio depende
    del tono (en los blancos casi no hay, en los medios es del 14-21 %).
  - Lo unico que si responde es la **compensacion de exposicion**: con
    `persist.cam50.ev -6` (un paso de EV menos) el quemado baja del 3,19 % al
    0,74 %, mejor que ninguna de las otras dos, y la resolucion no se resiente.

Conclusion practica: para el dia a dia sigue siendo mejor la camara normal de
12,6 MP; el modo de 50 MP se queda como experimento util (funciona, guarda
8192x6144 en 1,3 s y aguanta disparos seguidos) pero con un color que no es de
fiar. Si algun dia aparecen los datos de crosstalk del modulo (la region
CrossTalk de su EEPROM esta declarada con tamano 0) esto cambiaria.

## Quitar ro.debuggable sin perder el root (24-08)

Estaba puesto para depurar, pero la ROM se presenta como compilacion de usuario
con release-keys y con `ro.debuggable=1` encima: eso lo detectan Play Integrity y
las apps de banca, y ademas cuesta rendimiento.

Quitarlo del arbol y reflashear `system` **no basta**. El `/system/build.prop`
instalado ya dice `ro.debuggable=0` (comprobado en el movil), pero el sistema
seguia arrancando con 1, y no estaba en ningun fichero: ni en el build.prop de
ninguna particion, ni en el del ramdisk (`system/etc/ramdisk/build.prop`), ni en
el cmdline, ni en el bootconfig. La causa es que **el init del ramdisk esta
parcheado por KernelSU** y activa el mecanismo de AOSP `INIT_FORCE_DEBUGGABLE`
(las cadenas `INIT_FORCE_DEBUGGABLE` y `/force_debuggable` estan dentro del
binario de init); ese mecanismo fija las propiedades antes de que se lea
build.prop y, como las `ro.*` son inmutables una vez fijadas, gana el 1.

Tocar el boot para quitar ese parche es justo donde vive KernelSU, asi que la
via elegida fue otra: un modulo de KernelSU en
`/data/adb/modules/sin_debuggable` que en `post-fs-data` vuelve a fijarlas con
`resetprop`:

    resetprop ro.debuggable 0
    resetprop ro.force.debuggable 0

Comprobado tras reiniciar: `ro.debuggable=0`, `ro.force.debuggable=0`, SELinux
Enforcing, telefonia en servicio y **KernelSU intacto** (`su -v` responde
`3.0.1:KernelSU`). Se pierde `adb root`, que es lo esperado; `adb shell` y `su`
siguen funcionando. Para desactivarlo, basta crear un fichero `disable` dentro
de la carpeta del modulo.

Nota: el root sigue siendo visible para las apps (hay `su` en /system/bin y
/system/xbin ademas del de KernelSU). Si algun dia molesta con la banca, el
kernel ya trae SUSFS (`CONFIG_KSU_SUSFS=y`), que es por donde habria que ir.

## Volumen de notificaciones: mas pasos y minimo mas bajo (24-08)

Dos limites distintos, medidos en el movil:

  - **Pasos**: notificacion y timbre tenian 7 (multimedia y alarma, 15).
    AudioService los lee de `config_audio_notif_vol_steps` y
    `config_audio_ring_vol_steps`, asi que no hace falta tocar el framework:
    se ponen a 15 en el RRO del dispositivo (`FrameworksResCupid`, que vive en
    la particion odm), junto con los valores por defecto, que suben de 5 a 7
    para que el volumen inicial quede parecido dentro de la escala nueva.
  - **Curva**: la curva de esos dos flujos por altavoz empezaba en -29,70 dB,
    mientras que la de multimedia empieza en -58 dB. Con 7 pasos, el nivel 1
    caia en el 14 % de la curva: unos -26 dB, de ahi que el minimo ya sonara
    fuerte. Se baja el tramo inferior a -50 dB en
    `frameworks/av/services/audiopolicy/config/audio_policy_volumes.xml`
    (se instala en /vendor/etc), con puntos intermedios para que suba suave y
    dejando el tramo alto igual, asi que el maximo no cambia. No se copian los
    -58 dB de multimedia a proposito: un aviso inaudible no sirve.

Resultado comprobado con `dumpsys audio`: `STREAM_NOTIFICATION` y `STREAM_RING`
pasan de Max 7 a Max 15, y la curva instalada en /vendor empieza en -5000.

Aparte, la sensacion de que las notificaciones sonaban mas fuerte de lo
configurado tenia su propia causa: **el nivelador dinamico de Dolby**, que sube
la ganancia segun el ruido ambiente. Se desactivo desde su app
(`co.aospa.dolby.xiaomi`); comprobado con `vendor.audio.dolby.ds2.enabled=false`.

## Ojo con las actualizaciones

Casi todo lo ajustado vive en particiones que una OTA de Evolution X
sobrescribe. Tras cada actualizacion habria que rehacer:

  - el log del HAL de camara apagado (vendor),
  - la curva de volumen (vendor),
  - los 15 pasos de volumen (odm),
  - `ro.debuggable=0` del build.prop (system) -- aunque el modulo de KernelSU
    que lo fuerza vive en /data y **si** sobrevive.

Y recordar que /vendor, /system_ext y /odm estan al 100 % de ocupacion: cualquier
cambio ahi obliga a reconstruir la imagen entera, no se puede editar en caliente.
