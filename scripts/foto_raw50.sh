#!/system/bin/sh
# Hace una foto y deja su RAW de 50 MP convertido en DNG.
#
# El HAL solo escribe la imagen completa del sensor cuando esta puesto
# autoImageDump, y con eso puesto tambien escribe todo lo demas: el preview
# llena el disco a unos 30 GB por minuto. Por eso aqui se enciende justo para
# el disparo y se apaga en cuanto termina, se aparta el bufer de 8192x6144 y se
# borra el resto. La camara convierte ese bufer en DNG al hacer la siguiente
# foto (ajuste "DNG de 50 MP del volcado del HAL").
M=/data/adb/modules/cupid_ajustes/system/vendor/etc/camera/camxoverridesettings.txt
D=/vendor/etc/camera/camxoverridesettings.txt
DEST=/sdcard/raw50

pon_volcado() {
    grep -v -iE "autoImageDump|dumpCHIMetadata" "$M" > /data/local/tmp/ov.txt
    if [ "$1" = "si" ]; then
        cat >> /data/local/tmp/ov.txt <<'FIN'
autoImageDump=1
autoImageDumpCHINodeInstanceMask=0xFFFFFFFF
autoImageDumpCHINodeoutputPortMask=0xFFFFFFFF
autoImageDumpIFEInstanceMask=0xFFFFFFFF
autoImageDumpIFEoutputPortMask=0xFFFFFFFF
dumpCHIMetadataToFile=1
FIN
    fi
    cat /data/local/tmp/ov.txt > "$M"
    chcon u:object_r:vendor_configs_file:s0 "$M"; chmod 644 "$M"
    # Un mv cambia el inodo y el montaje se queda con el viejo, asi que se
    # rehace cada vez.
    nsenter --mount=/proc/1/ns/mnt -- /system/bin/umount "$D" 2>/dev/null
    nsenter --mount=/proc/1/ns/mnt -- /system/bin/mount --bind "$M" "$D"
    pkill -f camerahalserver; pkill -f cameraserver
    sleep 4
}

# Si hay otra app con la camara abierta, las dos fallan: mejor no empezar.
if ! sh /data/local/tmp/camara_libre.sh "$1"; then
    echo "no se hace nada. Con -f se ignora que la pantalla este encendida."
    exit 1
fi

echo "1/5 encendiendo el volcado del HAL"
rm -rf "$DEST"; mkdir -p "$DEST"; chmod 777 "$DEST"
find /data/vendor/camera -maxdepth 1 -name 'IMG_*' -delete
pon_volcado si

echo "2/5 abriendo la camara"
am force-stop com.cupid.cam50
am start -n com.cupid.cam50/.MainActivity >/dev/null
# Se espera a que la camara tenga de verdad el foco: si se dispara antes, el
# toque cae en otra ventana y la foto no llega a hacerse.
i=0
while [ $i -lt 20 ]; do
    dumpsys window | grep mCurrentFocus | grep -q cam50 && break
    sleep 1
    i=$((i+1))
done
sleep 3

echo "3/5 disparando"
input tap 539 2198
sleep 16

echo "4/5 apartando el RAW de 50 MP y apagando el volcado"
am force-stop com.cupid.cam50
find /data/vendor/camera -maxdepth 1 -name '*w?8192?*RAWMIPI10' -exec cp {} "$DEST/" \;
chmod 644 "$DEST"/* 2>/dev/null
pon_volcado no
find /data/vendor/camera -maxdepth 1 -name 'IMG_*' -delete

echo "5/6 segundo disparo, ya sin volcado, para escribir el DNG"
# La conversion necesita los datos de color del sensor y los del disparo, que
# solo existen despues de una captura; por eso hace falta esta segunda foto,
# que ya no vuelca nada.
am start -n com.cupid.cam50/.MainActivity >/dev/null
i=0
while [ $i -lt 20 ]; do
    dumpsys window | grep mCurrentFocus | grep -q cam50 && break
    sleep 1
    i=$((i+1))
done
sleep 3
input tap 539 2198
sleep 14
am force-stop com.cupid.cam50
input keyevent KEYCODE_SLEEP

echo "6/6 resultado"
ls -l /sdcard/Download/cam50/*.dng 2>/dev/null | tail -2
df -h /data | tail -1
