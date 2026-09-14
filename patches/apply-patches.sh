#!/bin/bash
# Re-aplica los parches locales sobre un arbol Evolution X limpio.
#   uso: bash patches/apply-patches.sh /home/android/evolution-x
# MAP.txt: <directorio de parches> <ruta del proyecto> <commit base sobre el que se hizo el parche>
# Los arboles device/xiaomi/* y vendor/xiaomi/* NO van por parche: se clonan
# enteros desde evolution-x-cupid/ (rama cupid-prod).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
TREE=${1:?ruta del arbol Evolution X}
rc=0
while IFS=$'\t' read -r dir proj base; do
  [ -n "$dir" ] || continue
  if [ ! -d "$TREE/$proj" ]; then echo "SKIP $proj (no existe)"; continue; fi
  if git -C "$TREE/$proj" log --oneline -1 | grep -q "cupid"; then echo "OK   $proj (ya aplicado)"; continue; fi
  echo "==   $proj (base $base)"
  if ! git -C "$TREE/$proj" am --3way "$HERE/$dir"/*.patch; then
    echo "!!   conflicto en $proj: resuelve y 'git am --continue' (o 'git am --abort')"
    rc=1; break
  fi
done < "$HERE/MAP.txt"
exit $rc
