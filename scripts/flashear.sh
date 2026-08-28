#!/usr/bin/env bash
# Flashea la ROM en un Xiaomi 12 (cupid). Comprueba antes que el movil es el que
# toca y que estan las cuatro imagenes, porque flashear esto en otro modelo lo
# deja sin arrancar.
set -euo pipefail

IMAGENES=(system.img system_ext.img vendor.img odm.img)
DIR="${1:-images}"

echo "== comprobaciones previas"
for i in "${IMAGENES[@]}"; do
  if [ ! -f "$DIR/$i" ]; then
    echo "   falta $DIR/$i"; exit 1
  fi
done
echo "   las cuatro imagenes estan"

if ! command -v fastboot >/dev/null; then
  echo "   no encuentro fastboot en el PATH"; exit 1
fi

MODELO=$(adb shell getprop ro.product.device 2>/dev/null | tr -d '\r' || true)
if [ -n "$MODELO" ] && [ "$MODELO" != "cupid" ]; then
  echo "   ATENCION: el movil dice ser '$MODELO', no 'cupid'. Abortando."
  exit 1
fi

BATERIA=$(adb shell dumpsys battery 2>/dev/null | awk '/ level:/ {print $2}' | tr -d '\r' || true)
if [ -n "$BATERIA" ] && [ "$BATERIA" -lt 50 ]; then
  echo "   bateria al $BATERIA %: cargalo por encima del 50 % antes de flashear"
  exit 1
fi

echo
echo "== reiniciando a fastbootd"
adb reboot fastboot
until fastboot devices | grep -q fastboot; do sleep 2; done
echo "   movil en fastbootd"

echo
echo "== flasheando"
for i in "${IMAGENES[@]}"; do
  PARTICION="${i%.img}"
  echo "-- $PARTICION"
  fastboot flash "$PARTICION" "$DIR/$i"
done

echo
echo "== listo"
echo "Si vienes de otra ROM, formatea los datos ahora con:  fastboot -w"
echo "Y despues:  fastboot reboot"
echo
echo "Tras el primer arranque, instala el modulo de KernelSU:"
echo "  scripts/instalar_modulo.sh"
