#!/usr/bin/env bash
# Instala el modulo de KernelSU que mantiene los ajustes propios del movil aunque
# se actualice la ROM: calibracion de audio (cancelacion de eco), log del HAL de
# camara apagado, 15 pasos de volumen y ro.debuggable a 0.
set -euo pipefail

PAQUETE="${1:-modules/cupid_ajustes.tgz}"

if [ ! -f "$PAQUETE" ]; then
  echo "no encuentro $PAQUETE"; exit 1
fi

if ! adb shell su -c id 2>/dev/null | grep -q "uid=0"; then
  echo "no hay root disponible: comprueba que KernelSU esta activo"
  exit 1
fi

echo "== copiando el modulo"
adb push "$PAQUETE" /data/local/tmp/cupid_ajustes.tgz

echo "== instalando"
adb shell su -c "tar xzf /data/local/tmp/cupid_ajustes.tgz -C /data/adb/modules/ && chmod 755 /data/adb/modules/cupid_ajustes/post-fs-data.sh && rm /data/local/tmp/cupid_ajustes.tgz"

echo "== contenido instalado:"
adb shell su -c "find /data/adb/modules/cupid_ajustes -type f | sed 's|/data/adb/modules/cupid_ajustes|  |'"

echo
echo "Reinicia para que surta efecto:  adb reboot"
echo "Despues, comprueba que el DSP tiene su calibracion (tiene que dar 0):"
echo "  adb shell su -c \"logcat -c; sleep 5; logcat -d | grep -c 'No calibration found'\""
