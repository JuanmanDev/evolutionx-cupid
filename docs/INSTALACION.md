# Guía de instalación

Para el **Xiaomi 12 (cupid)**. No sirve para otros modelos.

## Antes de empezar

Necesitas el bootloader desbloqueado, `adb` y `fastboot` en el ordenador, y el
móvil con **más del 50 % de batería**. Haz copia de tus datos: si vienes de otra
ROM tendrás que formatear.

Y una advertencia que va en serio: **la calibración de audio incluida es la de
una unidad concreta**. El HAL abre siempre el mismo fichero de calibración y aquí
va el juego `elus`, que es el que corresponde a este móvil. Si tu unidad usa el
juego genérico, tendrás mal el audio en llamada (eco para el interlocutor). Si te
pasa, mira la sección "Si el audio en llamada suena mal".

## Instalación

Descomprime la entrega y entra en la carpeta `images/`. Con el móvil encendido y
conectado por USB:

    adb reboot fastboot

Espera a que aparezca el menú de fastbootd y comprueba que el ordenador lo ve:

    fastboot devices

Flashea las cuatro particiones:

    fastboot flash system     system.img
    fastboot flash system_ext system_ext.img
    fastboot flash vendor     vendor.img
    fastboot flash odm        odm.img

Si vienes de otra ROM, formatea los datos ahora:

    fastboot -w

Y reinicia:

    fastboot reboot

El primer arranque tarda unos minutos.

## Después del primer arranque

Instala el módulo de KernelSU, que es lo que mantiene los ajustes propios aunque
actualices la ROM. Con el móvil desbloqueado:

    adb push modules/cupid_ajustes /data/local/tmp/
    adb shell su -c "cp -r /data/local/tmp/cupid_ajustes /data/adb/modules/ && chmod 755 /data/adb/modules/cupid_ajustes/post-fs-data.sh"
    adb reboot

Ese módulo se encarga de:

  - la calibración de audio correcta (cancelación de eco en llamada),
  - el log del HAL de cámara apagado (consumo),
  - los 15 pasos de volumen,
  - dejar `ro.debuggable` a 0 en cada arranque.

Y por último, si quieres la cámara de 50 MP:

    adb install apps/Cam50Test.apk

## Ajustes recomendados

La barra de estado del Xiaomi 12 va muy justa de espacio por la cámara central.
Si activas los segundos del reloj, no cabe todo y el icono de cobertura acaba
convertido en un punto o pisándose con el del wifi. Con esto se ve todo:

    adb shell settings put system status_bar_clock_seconds 0
    adb shell settings put system network_traffic_hidearrow 1

Y comprueba que los rellenos de la barra no estén en negativo (si lo están, el
primer carácter del reloj y del nombre del operador salen cortados):

    adb shell settings put system statusbar_extra_padding_start 0
    adb shell settings put system statusbar_extra_padding_end 0

## Si el audio en llamada suena mal

Síntoma: quien te escucha se oye a sí mismo. Comprueba si el DSP se está quedando
sin calibración:

    adb shell su -c "logcat -c; sleep 5; logcat -d | grep -c 'No calibration found'"

Si sale un número mayor que cero, tu unidad necesita el otro juego de
calibración. Cámbialo así (los dos juegos vienen incluidos en la ROM):

    adb shell su -c "cp /vendor/etc/acdbdata/waipio_mtp/Forte_elus_acdb_cal.acdb /data/adb/modules/cupid_ajustes/system/vendor/etc/acdbdata/Forte/Forte_acdb_cal.acdb"

o, al revés, si lo que necesitas es el genérico, copia el de `Forte/` original de
tu unidad. Reinicia y vuelve a comprobar el contador: tiene que quedar en 0.

## Volver atrás

Guarda siempre las imágenes de tu ROM anterior. Para volver, flashea esas cuatro
particiones igual que arriba. Los módulos de KernelSU viven en `/data/adb/modules`
y se quitan borrando su carpeta o creando dentro un fichero vacío llamado
`disable`.

## Preguntas frecuentes

**¿Puedo usar GCam con 50 MP?** No en este móvil. El sistema no anuncia ningún
tamaño de foto por encima de 4208x3120; GCam ofrece 50 MP por una etiqueta
privada de Xiaomi, pide algo inexistente y se cierra. Está explicado en las
notas técnicas.

**¿Pierdo el root al actualizar?** No: KernelSU va en el kernel y el módulo vive
en `/data`. Lo que sí se pierde con una OTA son los cambios de las particiones,
por eso el módulo replica los importantes.

**¿Funciona la banca?** Depende de la app. `ro.debuggable` va a 0, que era el
delator más obvio, pero el root sigue siendo visible. El kernel incluye SUSFS
para ocultarlo, pero no viene configurado.
