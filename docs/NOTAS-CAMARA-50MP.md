# Camara de 50 MP en cupid (Xiaomi 12, IMX766 Quad-Bayer)

Resumen de lo averiguado analizando el firmware de HyperOS y midiendo en el
movil. Todo lo de aqui esta comprobado; lo que no lo esta se dice.

## Como se consiguen los 8192x6144 reales

Cuatro piezas, y hacen falta todas:

1. **El paquete en la lista de apps privilegiadas de camara**:
   `persist.vendor.camera.privapp.list=com.cupid.cam50,...` (se fija en
   `device.mk`). Sin eso, la misma sesion devuelve 1920x1440.
2. **Operating mode 0x80F3** en `CameraDevice.createCustomCaptureSession()`
   (@SystemApi, de ahi `platform_apis` en `Android.bp`). 0x80F3 es
   `SESSION_OPERATION_MODE_NORMAL_ULTRA_PIXEL_PHOTOGRAPHY`, constante sacada de
   `Lcom/xiaomi/engine/CameraOperationMode;` en el `classes4.dex` del APK de
   MiuiCamera. Con 0x8001 (MIUI_BACK) se obtienen 4096x3072.
3. **Dos flujos**: uno pequeno mas el grande de 8192x6144. Con solo el grande,
   `onConfigureFailed`.
4. **La etiqueta `xiaomi.remosaic.enabled`** en la peticion de captura. Es la
   que trae resolucion de verdad: sobre cuatro disparos de la misma escena, la
   diferencia al reducir a la mitad y volver a ampliar (medida de detalle real)
   cae de 0,037 con la etiqueta a 0,004 sin ella, y la energia laplaciana de
   0,175 a 0,023. Es decir, **sin la etiqueta el HAL entrega un reescalado** de
   12,6 MP aunque el fichero mida 8192x6144. `xiaomi.pureView.enabled` no
   cambia la resolucion.

El motivo de que haga falta la ruta propia de Xiaomi: `IFEMaxLineWidth=7296` es
menor que 8192, o sea que la ISP no procesa ese ancho de una pasada, y Xiaomi lo
resuelve por tiras en su tuberia offline (MIVI), que es la que selecciona ese
operating mode.

## Por que la app usa dos sesiones

La vista previa **no puede** vivir dentro de la sesion 0x80F3. Su tuberia
(`RealTimeFeatureZSLPreviewRaw`) mantiene reservada memoria del banco SMMU
`icp`; al disparar, el HAL levanta a la vez `QuadCFAFullSizeStatsParse`,
`RealtimeFeatureSWRemosaic` y `ZSLSnapshotYUVHAL`, y la reserva de IOVA se
agota:

    CAM-SMMU: cam_smmu_map_buffer_validate: IOVA alloc failed for shared
              memory, size=9179136, idx=2, cb:icp
    CSLAllocHW() Allocating CSL Buffer failed for len = 9175040
    camxcmdbuffermanager.cpp:432 InitializePool() Out of memory

y la camara muere con `ERROR_CAMERA_DEVICE` (4). Llamar a `stopRepeating()` no
arregla nada porque la tuberia sigue en marcha: hay que **cerrar** la sesion.
Por eso la previa va en una sesion normal y la de 0x80F3 se crea solo para el
disparo, se usa una vez y se cierra. Asi salen JPEG de 16-18 MB, tres disparos
seguidos sin fallo, ~1,3 s de disparo a fichero guardado.

## Lo que sigue mal: el color

Con `xiaomi.remosaic.enabled` la imagen tiene el detalle real (se leen letras de
2 mm a 3 m) pero sale con **tinte magenta y una rejilla fina**, y las medias de
canal quedan tipo R=71 G=49 B=79: el verde a la mitad. La causa esta en el log
del HAL:

    E/BASS: DevFile_GetSize() open file err
    E/REMOSAIC-NODE: GetPackData() get file err
    E/REMOSAIC-NODE: LibInit() REMOSAIC XTALK DATA GET Err
    E/Remosaic: runGainmapGen:217 pd_xtc_status(2), SPAF xtalk EEPROM data is
                invalid

`com.qti.node.remosaic.so` busca `/data/vendor/camera/remosaic_crosstalk_data.bin`
(no existe: se genera en caliente, no viene en ninguna particion) y el EEPROM
del modulo tampoco da datos de crosstalk validos. Sin el mapa de ganancias el
remosaico **no recoloca** los pixeles, asi que el ISP demosaica bloques 2x2 del
mismo color como si fueran Bayer normal. En el HAL esta ademas la pista de por
que no se compensa por otro lado:

    isHWRemosaic = true, set WB gain
    isHWRemosaic = false, not to set WB gain

Corregirlo en post con ganancias por canal **no funciona** (probado: las
ganancias globales dejan el violeta igual), porque no es un desbalance sino un
patron mal colocado.

Vias abiertas, por orden de interes:

1. **Reordenar el Quad-Bayer nosotros.** Con `persist.cam50.raw=1` la app pide
   `RAW_SENSOR` de 8192x6144 y guarda el fichero crudo en `Download/cam50`. La
   herramienta `remosaico.py` (en el directorio de trabajo, fuera del arbol)
   hace el reordenado 4x4 -> Bayer RGGB y el revelado; validada con datos
   sinteticos: error de 0,4-9 % por canal y canales en su sitio, frente a un
   error 8 veces mayor sin reordenar. Falta comprobarlo con un RAW real del
   movil.
2. **Conseguir los datos de crosstalk.** Estan en el EEPROM del modulo
   (`com.qti.eeprom.cupid_semco_imx766_p24c128f_wide_eeprom.so` los lee, y
   `libremosaiclib.so` los valida con CRC: `Tc_spaf_xtc_v3`, `CTC_CFA_XTC_v5`).
   Habria que ver si el HAL los descarta por version o si el modulo no los
   trae.

## Ojo con `exposeFullSizeForQCFA`

Esta puesto en `vendor/etc/camera/camxoverridesettings.txt`. Es lo que hace que
el tamano de 8192x6144 aparezca en las configuraciones de flujo, y por tanto lo
que permite que esta app lo pida, pero tambien lo que enreda a GCam y a Aperture
(escriben DNG de ~96 MiB con solo 12,58 MP de datos dentro y ceros al final).
**No quitarlo sin volver a comprobar que la app sigue viendo 8192x6144.**

## Propiedades de la app

    persist.cam50.raw       1 = guarda RAW en vez de JPEG
    persist.cam50.dng       1 = ademas del RAW crudo, escribe un DNG
    persist.cam50.pureview  1 = pone xiaomi.pureView.enabled (por defecto si)
    persist.cam50.remosaic  1 = pone xiaomi.remosaic.enabled (por defecto si)
    persist.cam50.ae/awb/af 1 = copia ese trozo del 3A de la previa
    persist.cam50.espera    ms de espera tras cerrar la previa (250)
    persist.cam50.modo      operating mode en decimal (33011 = 0x80F3)

Copiar el 3A **empeora** y por eso viene desactivado: con AE en OFF y los
valores de la previa la foto sale casi negra (medias 8/1/7 frente a 67/36/55 con
AE automatico).

## Calidad: que se puede mejorar y que no (25-08)

El problema que se veia: la resolucion era real (se leen letras de un cartel a
varios metros) pero el detalle fino se emborronaba, sobre todo los textos
pequenos, y el color salia desviado.

**Lo que si tenia arreglo: el procesado.** La app no tocaba ninguno de los
ajustes de procesado, asi que mandaba el HAL, y a 50 MP aplica una reduccion de
ruido tan agresiva que se come el detalle. Ahora se controla desde la propia app
(boton de ajustes) y se nota:

| reduccion de ruido | detalle medido | tamano del fichero |
|---|---:|---:|
| alta calidad (lo que hacia el HAL) | 0,0085 | 11 MB |
| minima | 0,0334 | 39 MB |
| apagada | 0,0428 | 43 MB |

Y no es ruido disfrazado de detalle: mirando al 100 % la trama de un tejido, con
"alta calidad" se ve pastosa y con "minima" se distinguen los hilos uno a uno.
Por eso los valores de partida de la app son **reduccion de ruido minima**,
**bordes en alta calidad**, **aberracion cromatica en alta calidad** y **JPEG al
100 %**. Con la reduccion apagada del todo hay bastante grano en las sombras, asi
que "minima" es el punto razonable.

**Lo que no tiene arreglo por ahora: el RAW.** Se consiguio capturarlo (en sesion
normal, que es donde el HAL lo admite a tamano completo): 100.663.296 bytes
exactos, 8192x6144 a 16 bits, y hasta se escribe un DNG valido. Pero al mirar
dentro:

    pixeles a cero: 75,0 %
    zona con datos: filas 0-1535 de 6144  ->  8192 x 1536 = 12,6 MP

o sea que el HAL mete **12,6 MP de datos en un contenedor de 50 MP** y rellena el
resto con ceros. Es lo mismo que ya hacian los DNG de Aperture. Conclusion: el
HAL solo remosaica para el JPEG; por la via RAW no hay 50 MP que revelar, y no
merece la pena insistir con reveladores externos.

Tampoco ayudo revelar el RAW a mano: el patron de color declarado no coincide con
el que tiene el fichero (el DNG revelado con dcraw sale con damero rosa), y un
demosaico casero queda por debajo del ISP aunque se acierte con el patron.

## Los 50 MP en RAW, resueltos (25-08)

Durante semanas el RAW a resolucion completa salio siempre igual: 8192x6144
pero con tres cuartas partes en negro, en cualquier formato (RAW16, RAW10, con
y sin `SENSOR_PIXEL_MODE_MAXIMUM_RESOLUTION`). Solo habia datos en las 1536
primeras filas, o sea los 12,6 MP de siempre estirados sobre un lienzo grande.
La conclusion era que la API publica no tiene forma de sacar la imagen completa
del sensor en esta camara.

El HAL si la tiene. Y se le puede pedir que la escriba a disco: la libreria de
ajustes `vendor/lib64/com.qti.settings.sm8450.so` declara toda la familia
`autoImageDump*`, que hace que camx guarde en `/data/vendor/camera` la entrada y
la salida de cada bloque. Con eso puesto aparecen, entre otros:

    IFE[0][9]   8192x6144  RAWMIPI10  62.914.560 bytes  <- el RAW de 50 MP
    BPS[0][1]   8192x6144  UBWCTP10              MfsrPrefilter
    BPS[1][1]   8192x6144  UBWCTP10              MfsrBlend
    IPE[4][9]   8192x6144  UBWCTP10              MfsrEqualization
    IPE[5][8]   8192x6144  YUV420NV12            MfsrPostFilter
    JPEG_Encoder / JPEG_Aggregator                InternalZSLYuv2JpegScaling

O sea que la foto de 50 MP no es un remosaico simple: son tres fotogramas RDI a
resolucion completa que pasan por MFSR (fusion de varios fotogramas) antes de
comprimirse. Por eso tiene menos ruido de lo que cabria esperar.

Ese `IFE[0][9]` mide exactamente 8192 x 6144 x 10 / 8 bytes y tiene datos en las
6144 filas (0,08 % de ceros, contra el 75 % de la via oficial). El mosaico es
Bayer normal 2x2 en orden BGGR, no quad-Bayer: el salto medio entre pixeles
vecinos es 37,9 a distancia 1 y 5,55 a distancia 2, que es justo lo que se ve
cuando el remosaico ya lo ha hecho el hardware.

### Como se usa

`foto_raw50.sh` (hace falta root) hace todo el ciclo: enciende el volcado,
dispara, aparta el bufer de 8192x6144 en `/sdcard/raw50`, apaga el volcado,
borra lo demas y hace un segundo disparo para que la camara escriba el DNG en
`Download/cam50`. El volcado se enciende y se apaga en el momento porque
mientras esta puesto el preview escribe unos 30 GB por minuto (en la primera
prueba llego a 112 GB antes de que diera tiempo a pararlo).

La conversion a DNG la hace la propia camara, con el ajuste "DNG de 50 MP del
volcado del HAL". Desempaqueta el MIPI10 a 16 bits y usa `DngCreator` con las
caracteristicas del sensor y el resultado del disparo, asi que el DNG lleva las
matrices de color, los niveles de negro y el balance de blancos reales. Sale un
fichero de 100.717.916 bytes que `dcraw` lee como:

    Full size:   8192 x 6144
    Image size:  8192 x 6144
    Output size: 8192 x 6144

sin recortes, y revela con color correcto.

### Lo que no se pudo

`persist.vendor.camxdump.minwidth` existe en el HAL pero no filtra nada en esta
version: con el puesto a 8000 se siguieron volcando todos los buferes. Tampoco
sirve encender solo el IFE: si las mascaras de los nodos CHI estan a cero no se
vuelca nada, porque quien enciende el mecanismo es la capa CHI.

## Por que GCam y Aperture no pueden hacer los 50 MP (25-08)

Para que el HAL entregue la foto completa hacen falta tres cosas, y una app
normal no hace ninguna de las dos ultimas porque no las conoce:

1. que 8192x6144 este anunciado como tamano de foto,
2. que la sesion se cree con el modo propietario 0x80F3,
3. que la peticion lleve `xiaomi.remosaic.enabled`.

Las tres se pueden poner desde el servicio de camara, y estan puestas: la 1 en
`addQuadCfaFullSizeJpeg` y las otras dos en `Camera3Device`, que cambia el modo
de sesion cuando ve una salida JPEG mas grande que la mayor foto que el HAL
anuncia por si mismo, y etiqueta las peticiones que apuntan a esa salida:

    Camera3-Device: foto de 8192x6144: se pasa del modo de sesion 0 al 33011

Con eso Aperture ya no mata al HAL al abrir la sesion, cosa que antes si hacia.
Pero se sigue cayendo al disparar, y la razon es la cantidad de imagenes que
reserva. Medido en el movil, con la camara de pruebas, cambiando solo ese
numero:

    1, 2, 3 imagenes -> foto guardada
    4                -> [MEMMGR] Import() Failed in importing Gralloc Buffer
                        Handle, WxH 8192x6144, format 0
                        Camera provider 'legacy/1-3' has died

No es falta de memoria: pasa igual con 3,9 GB libres. Es un tope del HAL para
ese puerto. Las apps hechas con CameraX reservan cuatro y se pasan justo.

Se intento recortarlo desde el servicio, en `Camera3OutputStream`, bajando lo
que puede pedir el HAL y lo que declara el consumidor. El recorte se aplica de
verdad:

    Camera3-OutputStream: se recorta el consumidor de 4 a 3 imagenes

pero no sirve: la camara de pruebas pidiendo cuatro se sigue llevando el HAL por
delante con el recorte puesto. Ese numero es el de la cola del ImageReader, que
vive en el proceso de la app; el servicio de camara no lo controla. Asi que
mientras la app pida cuatro imagenes de este tamano, no hay arreglo posible
desde el sistema: tiene que pedir tres o menos.

Por eso el anuncio de 8192x6144 se deja apagado por defecto
(`persist.sys.camera.qcfa_jpeg`): encendido, Aperture lo elige y se queda sin
camara al disparar. La camara de este directorio si hace los 50 MP porque pide
una sola imagen.

## Aperture tambien hace los 50 MP (25-08)

Los 50 MP dejan de ser cosa solo de esta camara: Aperture, que viene con la
ROM, ya puede hacerlos. Hizo falta entender dos cosas que costaron un dia
entero.

La primera estaba escondida en el propio servicio de camara, calculando el
tamano del bufer para el JPEG:

    if (!mPrivilegedClient && jpegBufferSize > maxJpegBufferSize) {
        jpegBufferSize = maxJpegBufferSize;   // recorta
    }

Una foto de 8192x6144 necesita unas cuatro veces el bufer del tamano mas grande
que el HAL anuncia. A un cliente que no sea privilegiado se lo recortan a la
cuarta parte, y el HAL revienta al mapearlo. Y "privilegiado" quiere decir,
literalmente, estar en `persist.vendor.camera.privapp.list`. Esta camara esta
ahi; Aperture no estaba. Eso explica por que una funcionaba y la otra no.

La segunda es el numero de imagenes. Medido cambiando solo ese numero:

    1, 2, 3 imagenes -> foto guardada
    4                -> [MEMMGR] Import() Failed ... WxH 8192x6144
                        Camera provider has died

No es memoria libre lo que falta (pasa con 3,9 GB disponibles) sino memoria
contigua, que se va fragmentando con el uso; por eso el mismo disparo unas
veces sale y otras no. Las apps hechas con CameraX reservan cuatro y se pasan
justo de la raya, y ese numero lo decide CameraX por dentro: no se puede tocar
ni desde Aperture ni desde el servicio de camara. Se intento recortarlo desde
`Camera3OutputStream` y no sirve, porque la cola que manda es la del
ImageReader, que vive en el proceso de la app.

La solucion es no pasar por CameraX para esa foto. En Aperture hay ahora un
ajuste, "Fotos a la resolucion completa", y cuando esta encendido el disparo va
por `utils/Foto50Mp.kt`: suelta la camara de CameraX, abre Camera2 a pelo con
un ImageReader de una sola imagen, dispara y se la devuelve. La previa se queda
congelada un par de segundos, que es el precio de no poder tener las dos cosas
abiertas a la vez.

Del modo de sesion propietario y de la etiqueta de remosaico no se ocupa la
app: lo pone el servicio de camara en cuanto ve una salida JPEG de ese tamano.

## Aperture hace los 50 MP (26-08)

Resuelto. Aperture, la camara que viene con la ROM, hace fotos de 8192x6144
reales:

    Foto50Mp: foto de 50 MP guardada: 26404491 bytes, 8192x6144
    -> tamano 8192x6144 = 50.3 MP, 95,9 % de la imagen con senal

Hicieron falta cuatro cosas, y cada una tapaba a la siguiente:

1. **Salir de CameraX.** CameraX reserva cuatro imagenes a la vez y a este
   tamano el HAL no aguanta la cuarta. Ese numero lo decide CameraX por dentro y
   no se puede tocar desde la app. La foto grande se hace ahora con Camera2 a
   pelo, pidiendo una sola imagen: `utils/Foto50Mp.kt`.

2. **Pantalla propia.** Dentro de la pantalla normal de la camara hay que soltar
   CameraX, y al soltarlo esa pantalla se cierra sola: el sistema congela la
   aplicacion y la imagen llega cuando ya no escucha nadie. Ademas Android
   retira la camara en cuanto la app deja de estar a la vista:

       Camera 0: Access for "org.lineageos.aperture" has been restricted,
       isUidVisible 0, procState 18

   Por eso la captura vive en `Actividad50Mp`, que no usa CameraX y se queda
   delante mientras dura.

3. **Dos sesiones, no una.** Al principio se dejaba la previa corriendo dentro
   de la sesion de resolucion completa para que convergiera la exposicion. El
   HAL abortaba, y el volcado decia exactamente donde:

       Executable: /vendor/bin/hw/vendor.qti.camera.provider@2.7-service_64
       pid: 29011, tid: 29109, name: Preview_5
       signal 6 (SIGABRT)
       #01 CamX::ImageBuffer::Import(...)
       #02 CamX::Node::SetupRequest(...)

   El hilo es Preview_5: aborta atendiendo la previa. Ahora se hace como en la
   camara de este directorio: previa en una sesion normal, se cierra del todo, y
   solo entonces se abre la de resolucion completa para una unica captura.

4. **Estar en la lista blanca del HAL.** Es la pieza que faltaba, y es
   terminante. Con el mismo codigo, cambiando solo si el paquete esta en
   `persist.vendor.camera.privapp.list`:

       dentro de la lista -> 8192x6144, 26 MB
       fuera de la lista  -> 1920x1440, 1,1 MB

   El HAL entrega la resolucion completa solo a los paquetes que reconoce.

### Un efecto secundario que costo encontrar

Anunciar el tamano de 50 MP (`persist.sys.camera.qcfa_jpeg=1`) rompe la captura,
y no solo la de Aperture: tambien la de la camara de este directorio, que
llevaba semanas funcionando. La razon es que ese anuncio sube tambien
`ANDROID_JPEG_MAX_SIZE`, y de ese valor sale el tamano del bufer que el
framework reserva para el JPEG de cualquier aplicacion; al cambiarlo, deja de
cuadrar con lo que espera el HAL y aparece el fallo de siempre:

    [MEMMGR] Import() Failed in importing Gralloc Buffer Handle, WxH 8192x6144

El anuncio ya no hace falta: `createCustomCaptureSession` no comprueba el tamano
contra la lista publicada. Asi que se queda apagado por defecto, y con el
apagado todo funciona.

## Por que los ports de GCam no pueden hacer los 50 MP

Hay dos formas de que una aplicacion pida la imagen completa del sensor:

  a) pedirla directamente, con createCustomCaptureSession, que no comprueba el
     tamano contra la lista publicada. Es lo que hacen la camara de este
     directorio y Aperture. Necesita API de sistema, o sea, ir dentro de la ROM.

  b) elegirla de la lista de tamanos publicados, que es lo unico que puede hacer
     una aplicacion normal. Para eso el tamano tiene que estar anunciado
     (persist.sys.camera.qcfa_jpeg=1).

El problema es que (b) no funciona, y no por falta de ganas: anunciar el tamano
rompe la captura para todo el mundo, incluidas las camaras que ya funcionaban.
Comprobado dos veces, tambien despues de dejar de tocar ANDROID_JPEG_MAX_SIZE,
que era el primer sospechoso:

    qcfa_jpeg=1 -> [MEMMGR] Import() Failed ... WxH 8192x6144   (fallan todas)
    qcfa_jpeg=0 -> foto de 50 MP guardada: 23305995 bytes, 8192x6144

Al publicar el tamano, el framework calcula el bufer del JPEG por otro camino y
lo que reserva deja de cuadrar con lo que el HAL espera. De ahi el fallo al
mapearlo, y de ahi que el HAL se muera y se lleve por delante a la aplicacion:
eso es lo que se ve desde fuera como "GCam se cierra al seleccionar 50 MP". No
se cierra la aplicacion, se muere el HAL.

Asi que un port de GCam (org.codeaurora.snapcam y companeros) no puede llegar a
los 50 MP en este movil: solo puede usar el camino (b), que es el que no
funciona. Y el codigo de esos ports no es publico (son APK cerrados, modificados
en smali), asi que tampoco se les puede anadir el camino (a).

Queda una via para quien quiera intentarlo: desensamblar el APK y sustituir su
creacion de sesion por createCustomCaptureSession con el modo 0x80F3. Es lo
mismo que hacen los modders para limitar el numero de imagenes. No se ha hecho
aqui.

## Resuelto del todo: 50 MP en JPEG y en RAW, en la camara de la ROM (26-08)

Aperture hace fotos de 50 MP con su boton de siempre, sin modos especiales, y el
DNG que guarda es un RAW de verdad:

    Aperture: (8192, 6144) = 50.3 MP, 99,4 % de la imagen con senal
    DNG:      8192x6144, ceros 0,0 %, filas con datos 6144 de 6144

Ese DNG es el que llevaba semanas resistiendose: hasta ahora el RAW a resolucion
completa salia siempre con tres cuartas partes en negro (1536 filas de 6144).

Faltaban tres piezas, y las tres estaban en el servicio de camara:

**1. El bufer del JPEG estaba mal calculado.** El HAL declara un maximo pensado
para la foto de 12,5 MP:

    el tamano maximo de JPEG pasa de 19861384 a 56330240 bytes

19,8 MB, cuando una foto de 50 MP pesa entre 24 y 42. El bufer era mas pequeno
que la propia foto, y el HAL abortaba al mapearlo:

    [MEMMGR] Import() Failed in importing Gralloc Buffer Handle, WxH 8192x6144

Un primer intento con tres cuartos de byte por pixel (37 MB) tampoco bastaba: el
HAL exige el caso peor completo. Ahora se declara byte y medio por pixel mas
margen para las cabeceras.

De paso, esto explica algo que costo dias entender: el famoso limite de "cuatro
imagenes en vuelo" no existia. Era este mismo bufer. Con el bien calculado, una
captura con cuatro imagenes sale sin problemas.

**2. El tamano se anunciaba, pero las aplicaciones no lo veian.** La lista cruda
que reciben si lo trae:

    lista cruda: 110 entradas, JPEG por encima de 13 MP: 1
    JPEG en la lista cruda: 4208x3120 ... 1920x1080 8192x6144

pero el mapa de tamanos se quedaba en catorce. El motivo es un detalle de
StreamConfigurationMap: los tamanos que declaran mas de 50 ms por fotograma se
apartan a getHighResolutionOutputSizes, y getOutputSizes deja de mostrarlos. Casi
ninguna aplicacion consulta esa segunda lista. Le pasa de fabrica a 4208x3120,
que el HAL publica y tampoco aparece. Declarando una duracion por debajo de ese
umbral, el tamano sale en la lista de siempre y el mapa pasa de 14 a 15 entradas.

**3. Estar en la lista blanca del HAL**, que ya estaba documentado mas arriba.

Con las tres cosas juntas, cualquier aplicacion privilegiada que elija
8192x6144 recibe los 50 MP reales, en JPEG y en RAW. El anuncio
(`persist.sys.camera.qcfa_jpeg`) queda encendido por defecto.

La pantalla aparte de Aperture (`Actividad50Mp`) y el ajuste que la activa se
quedan como estan: ya no hacen falta para la foto normal, pero sirven para
forzar la captura a resolucion completa sin depender de lo que elija CameraX.
