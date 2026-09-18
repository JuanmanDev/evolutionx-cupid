#!/usr/bin/env bash
# Publica la ROM compilada como asset de una GitHub Release, junto con el
# manifest snapshot que la reproduce. Requiere 'gh auth login' hecho.
#
# Uso:  ./scripts/publish-release.sh <ruta-al-zip> [etiqueta]
set -euo pipefail

ZIP="${1:?Falta el zip de la ROM}"
TAG="${2:-cupid-$(date +%Y%m%d)}"
MIRROR="${MIRROR_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"

[ -f "$ZIP" ] || { echo "No existe $ZIP" >&2; exit 1; }

# GitHub rechaza assets de mas de 2 GB
SIZE=$(stat -c%s "$ZIP" 2>/dev/null || stat -f%z "$ZIP")
LIMIT=$((2 * 1024 * 1024 * 1024))
if [ "$SIZE" -gt "$LIMIT" ]; then
  echo "El zip ocupa $((SIZE / 1024 / 1024)) MB y el limite por asset es 2048 MB." >&2
  echo "Partirlo:  split -b 1900M \"$ZIP\" \"${ZIP}.part-\"" >&2
  echo "Y al restaurar:  cat ${ZIP}.part-* > $ZIP" >&2
  exit 1
fi

SUM=$(sha256sum "$ZIP" | cut -d' ' -f1)
SNAP=$(ls -1t "$MIRROR"/snapshots/manifest-cupid-*.xml 2>/dev/null | head -1 || true)

NOTES=$(mktemp)
{
  echo "Evolution X para Xiaomi 12 (cupid), variante user."
  echo
  echo "| | |"
  echo "|---|---|"
  echo "| zip | \`$(basename "$ZIP")\` |"
  echo "| sha256 | \`$SUM\` |"
  echo "| tamano | $((SIZE / 1024 / 1024)) MB |"
  echo "| snapshot | \`$( [ -n "$SNAP" ] && basename "$SNAP" || echo "ninguno" )\` |"
  echo
  echo "Reproducir este build:"
  echo '```bash'
  echo "./scripts/restore-tree.sh snapshots/$( [ -n "$SNAP" ] && basename "$SNAP" || echo "manifest-cupid-FECHA.xml" )"
  echo "cd patches && ./apply-patches.sh /home/android/evolution-x"
  echo "/home/android/build_prod.sh"
  echo '```'
} > "$NOTES"

gh release create "$TAG" "$ZIP" ${SNAP:+"$SNAP"} \
  --title "cupid $TAG" \
  --notes-file "$NOTES"

rm -f "$NOTES"
echo "Release $TAG publicada."
