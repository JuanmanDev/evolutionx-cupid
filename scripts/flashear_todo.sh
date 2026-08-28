#!/usr/bin/env bash
# =============================================================================
#  flashear_todo.sh  —  Instala Evolution X 17 en el Xiaomi 12 (cupid) de una vez
# =============================================================================
#  Hace todo el proceso: entra en fastboot, flashea las particiones de arranque
#  (boot con o sin KernelSU, vbmeta, dtbo, vendor_boot), sideloadea la ROM en
#  recovery, borra datos y cache si se pide, y reinicia.
#
#  USO:
#     ./flashear_todo.sh [--ksu | --no-ksu] [--wipe] [--dir CARPETA]
#
#  OPCIONES:
#     --ksu       Flashea el boot CON KernelSU (root).           [por defecto]
#     --no-ksu    Flashea el boot SIN KernelSU (limpio, sin root).
#     --wipe      Formatea datos (factory reset). Necesario si vienes de otra ROM.
#     --dir DIR   Carpeta con las imagenes y la ROM (por defecto: la del script).
#     --solo-boot No sideloadea la ROM; solo reflashea las particiones de arranque
#                 (util para cambiar entre con/sin KSU sin reinstalar).
#
#  ARCHIVOS QUE ESPERA en la carpeta (--dir):
#     rom.zip                (la ROM; si esta partida, ejecuta antes unir_rom.sh)
#     boot-ksu.img           boot con KernelSU
#     boot-noksu.img         boot sin KernelSU
#     dtbo.img  vbmeta.img  vbmeta_system.img  vendor_boot.img
#
#  SOLO para el Xiaomi 12 (cupid). Flashear esto en otro modelo lo deja sin
#  arrancar. Bootloader desbloqueado y bateria > 50 %.
# =============================================================================
set -euo pipefail

VARIANTE="ksu"
WIPE=0
SOLO_BOOT=0
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while [ $# -gt 0 ]; do
  case "$1" in
    --ksu)      VARIANTE="ksu" ;;
    --no-ksu)   VARIANTE="noksu" ;;
    --wipe)     WIPE=1 ;;
    --solo-boot) SOLO_BOOT=1 ;;
    --dir)      DIR="$2"; shift ;;
    -h|--help)  sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "opcion desconocida: $1"; exit 1 ;;
  esac
  shift
done

BOOT="$DIR/boot-$VARIANTE.img"
[ "$VARIANTE" = "ksu" ] && BOOT="$DIR/boot-ksu.img" || BOOT="$DIR/boot-noksu.img"

# ---- utilidades -------------------------------------------------------------
err(){ echo "ERROR: $*" >&2; exit 1; }
hay(){ command -v "$1" >/dev/null 2>&1 || err "no encuentro '$1' en el PATH"; }

esperar_fastboot(){ echo ".. esperando modo fastboot"; until fastboot devices | grep -q .; do sleep 1; done; }
esperar_adb(){ echo ".. esperando adb"; adb wait-for-device; }
esperar_sideload(){ echo ".. esperando modo sideload"; until adb devices | grep -q sideload; do sleep 1; done; }

# ---- comprobaciones ---------------------------------------------------------
hay adb; hay fastboot
echo "== comprobaciones"
[ -f "$BOOT" ]                 || err "falta $BOOT"
[ -f "$DIR/dtbo.img" ]         || err "falta $DIR/dtbo.img"
[ -f "$DIR/vbmeta.img" ]       || err "falta $DIR/vbmeta.img"
[ -f "$DIR/vendor_boot.img" ]  || err "falta $DIR/vendor_boot.img"
if [ "$SOLO_BOOT" -eq 0 ]; then
  [ -f "$DIR/rom.zip" ] || err "falta $DIR/rom.zip (si esta partida, ejecuta unir_rom.sh)"
fi

MODELO="$(adb shell getprop ro.product.device 2>/dev/null | tr -d '\r' || true)"
if [ -n "$MODELO" ] && [ "$MODELO" != "cupid" ]; then
  err "el movil dice ser '$MODELO', no 'cupid'. Abortado."
fi
echo "   variante: $VARIANTE   wipe: $WIPE   solo-boot: $SOLO_BOOT"
echo "   boot: $(basename "$BOOT")"
read -r -p "   Continuar? Esto reflashea particiones. [s/N] " R
[ "$R" = "s" ] || [ "$R" = "S" ] || { echo "cancelado"; exit 0; }

# ---- a fastboot -------------------------------------------------------------
echo "== reiniciando a bootloader"
adb reboot bootloader 2>/dev/null || fastboot reboot bootloader 2>/dev/null || true
esperar_fastboot

echo "== particiones de arranque (ambos slots)"
for S in a b; do
  fastboot --slot=$S flash dtbo         "$DIR/dtbo.img"        || true
  fastboot --slot=$S flash vendor_boot  "$DIR/vendor_boot.img" || true
  fastboot --slot=$S flash boot         "$BOOT"                || true
done
# vbmeta con verificacion desactivada (para boot modificado)
fastboot --disable-verity --disable-verification flash vbmeta        "$DIR/vbmeta.img"        || true
[ -f "$DIR/vbmeta_system.img" ] && fastboot --disable-verity --disable-verification flash vbmeta_system "$DIR/vbmeta_system.img" || true

# ---- ROM por sideload -------------------------------------------------------
if [ "$SOLO_BOOT" -eq 0 ]; then
  echo "== arrancando a recovery para sideload"
  fastboot reboot recovery
  echo "   En el movil: Apply update -> Apply from ADB.  (usa Volumen + Power)"
  esperar_sideload
  echo "== sideload de la ROM (tarda varios minutos)"
  adb sideload "$DIR/rom.zip" || true
fi

# ---- wipe -------------------------------------------------------------------
if [ "$WIPE" -eq 1 ]; then
  echo "== formateando datos (factory reset)"
  # desde recovery: Wipe data/factory reset. Por fastboot:
  adb reboot bootloader 2>/dev/null || true
  esperar_fastboot
  fastboot -w || true
fi

echo "== reiniciando al sistema"
fastboot reboot 2>/dev/null || adb reboot 2>/dev/null || true

cat <<FIN

== LISTO. Primer arranque: varios minutos.

Despues del arranque, si has puesto la variante con KSU, instala el modulo de
ajustes propios (audio/camara/volumen), que sobrevive a las OTAs:

    ./instalar_modulo.sh

Y mira RECOMENDACIONES.md para la config de camara (50 MP, GCam) y animaciones.
FIN
