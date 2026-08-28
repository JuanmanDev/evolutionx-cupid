# Recomendaciones de uso

Ajustes que merecen la pena en este móvil, con los comandos exactos. Todo
opcional; nada de esto es imprescindible para que la ROM funcione.

## Cámara

### Para 50 MP: usa la cámara de Xiaomi (o Aperture / Cam50Test), no GCam

En este móvil **GCam no puede hacer 50 MP** — está medido y explicado a fondo en
[`50MP.md`](50MP.md) y [`NOTAS-CAMARA-50MP.md`](NOTAS-CAMARA-50MP.md). Resumen:
el motor HDR+ de GCam solo sabe pedir RAW/YUV a resolución completa, y el HAL de
este chip solo entrega los 50 MP como **JPEG** por el remosaico propietario de
Xiaomi; por la vía RAW/YUV el HAL devuelve negro. Se probó hasta parchear el
framework (área activa a 8192×6144, forzar el modo remosaico sobre el stream RAW
de GCam) y GCam llega a configurar la sesión y arrancar HDR+, pero los fotogramas
salen negros. Es un muro del hardware/HAL, no del software.

**Lo que sí da 50 MP reales:**

| App | Cómo |
|---|---|
| **Cámara de Xiaomi** (`com.android.camera`) | Modo foto → selector **50 MP**. La ruta nativa, la más cómoda. |
| **Aperture** (la de la ROM) | Con el soporte de 50 MP compilado, botón normal → JPEG 8192×6144 + DNG. |
| **Cam50Test** | La app incluida, pensada solo para esto (JPEG + RAW de 50 MP). |

Aviso de color: los 50 MP reales salen con un **tinte magenta** que no se puede
corregir desde la app (el módulo no trae la calibración de crosstalk del sensor;
detalles en las notas). Baja un paso la exposición si quema altas luces:

    adb shell su -c "setprop persist.cam50.ev -6"   # y reabrir la cámara de 50 MP

**Para el día a día, GCam a 12,6 MP suele dar mejor foto** que el 50 MP magenta
—salvo que necesites recortar mucho—, porque su HDR+ y su procesado son
superiores. Usa cada una para lo suyo.

### GCam recomendada (a 12,6 MP)

Cualquier port moderno de GCam (BSG/LMC 8.x, o el que trae `fishfood`) funciona a
12,6 MP. Config recomendada para mejores resultados:

  - **HDR+ Enhanced** activado (mejor rango dinámico, más lento).
  - **AWB de Google** activado (mejor balance de blancos que el del HAL).
  - **RAW (DNG)** activado si quieres editar después; ocupa más.
  - Deja la resolución en su valor por defecto (12,6 MP): no intentes forzar
    50 MP, se cierra.

Las configuraciones XML de la comunidad (p. ej. celsoazevedo) **afinan el
procesado** (color, ruido, tonos) a 12,6 MP — que es donde GCam gana a la cámara
de Xiaomi—; **no desbloquean megapíxeles**. Puedes probarlas para gusto de color.

## Extras que funcionan (bueno saberlo)

  - **Dolby Atmos** funciona (`co.aospa.dolby.xiaomi`). Abre **Dolby Atmos** desde
    el cajón de apps para elegir perfil (Música / Película / …); se aplica a
    altavoz y auriculares.
  - **Brillo del flash regulable.** Mantén pulsada la tesela de **Linterna** en
    los ajustes rápidos para ver un deslizador de brillo (función de Evolution X;
    el driver del LED de cupid admite esos niveles — la ROM ajusta las corrientes
    de flash/linterna en el HAL de cámara). Útil para una linterna más suave o un
    flash de cámara más potente.
  - **15 pasos de volumen** en timbre/notificación con primer paso más bajo (ver
    [`CAMBIOS.es.md`](CAMBIOS.es.md)).

## Cámara de Xiaomi: los modos extra que se descargan pueden cerrarse

La cámara de Xiaomi (port de MiuiCamera) muestra modos extra con **flecha de
descarga** (Clonar, Panorámica, VLOG, efectos de película, exposición pro, …). Al
pulsar uno **se cierra la app**. Diagnosticado: esos modos descargan un componente
por Google Play Dynamic Delivery (el de Clonar son ~77 MB), pero este ROM
**bloquea la red de MiuiCamera con SELinux** — al dominio `miuicamera_app` se le
niega crear sockets, a propósito, para matar el proceso de ads/telemetría de
Xiaomi (`mi_ad_pubsub`). La red bloqueada lanza una `SecurityException` no
capturada → cierre:

    avc: denied { create } tclass=udp_socket ... app=com.android.camera
    java.lang.SecurityException: Permission denied (missing INTERNET permission?)

**¿Se puede arreglar?** En parte. Permitir la red del dominio (una regla SELinux
de KernelSU, `permissive miuicamera_app` o un `allow` puntual) **quita el cierre**
— probado. Pero: (1) vuelve la red de ads/telemetría de Xiaomi, y (2) el módulo
sigue sin estar incluido (`Split clone … is not installed`, `no fused modules`) y
Google Play no lo sirve a este port instalado como app de sistema — así que el
modo tampoco descarga. Resultado: "no crashea, pero la descarga falla", no un modo
funcional. Así que no compensa.

**Los modos base funcionan**: Foto, **50 MP**, Vídeo, Retrato, Noche, Pro, Cámara
lenta, Time-lapse, Documentos, Vídeo dual. Para panorámica y similares, usa GCam u
otra app.

## Launcher: Lawnchair (búsqueda de apps sin acentos)

Launcher recomendado: **[Lawnchair](https://lawnchair.app/)**. Además del aspecto
limpio estilo Pixel y sus muchos ajustes, su **búsqueda de apps ignora los
acentos**: escribir `camara` encuentra *Cámara*, `telefono` encuentra *Teléfono*.
El launcher de serie distingue acentos y se los salta. Instálalo, ponlo por
defecto (Ajustes → Aplicaciones → Aplicaciones predeterminadas → App de inicio) y
usa el buscador del cajón de apps.

## Velocidad de las animaciones a 0,5× (interfaz más ágil)

El sistema se siente más rápido bajando las animaciones a la mitad:

    adb shell settings put global window_animation_scale 0.5
    adb shell settings put global transition_animation_scale 0.5
    adb shell settings put global animator_duration_scale 0.5

(Para desactivarlas del todo, pon `0`. Para volver a lo normal, `1`.) También se
puede desde Ajustes → Opciones de desarrollador → las tres escalas de animación.

## Barra de estado (Xiaomi 12 va justo de espacio por la cámara central)

Si activas los segundos del reloj no cabe todo y el icono de cobertura se
convierte en un punto o se pisa con el wifi. Con esto se ve todo bien:

    adb shell settings put system status_bar_clock_seconds 0
    adb shell settings put system network_traffic_hidearrow 1

Y comprueba que los rellenos de la barra no estén en negativo (si lo están, se
corta el primer carácter del reloj y del operador):

    adb shell settings put system statusbar_extra_padding_start 0
    adb shell settings put system statusbar_extra_padding_end 0

## Audio en llamada (si el interlocutor se oye a sí mismo)

Esta ROM trae la calibración de audio de una unidad concreta (`elus`). Si tu
unidad usa la genérica, hay eco. Comprueba (tiene que dar 0):

    adb shell su -c "logcat -c; sleep 5; logcat -d | grep -c 'No calibration found'"

Si sale más de 0, cambia el juego de calibración — ver
[`INSTALACION.md`](INSTALACION.md), sección "Si el audio en llamada suena mal".

## Ocultar root a la banca (opcional, avanzado)

El kernel trae **SuSFS**. Para ocultar el root a apps concretas (banca,
autenticadores) usa la denylist de la app de KernelSU: **Ajustes → Configurar
denylist**, marca las apps, y con el módulo de umount activo dejan de ver el
root. La depuración USB (`adb_enabled`) es una detección aparte; desactívala
(`Opciones de desarrollador → Depuración USB`) cuando uses esas apps si te la
detectan.
