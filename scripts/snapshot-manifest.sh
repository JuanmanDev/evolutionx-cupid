#!/usr/bin/env bash
# Genera un manifest fijado (todos los proyectos a SHA exacto) del arbol de WSL
# y lo deja en snapshots/ del espejo Windows.
#
# Uso (dentro de WSL):  ./scripts/snapshot-manifest.sh [etiqueta]
set -euo pipefail

TREE="${AOSP_TREE:-/home/android/evolution-x}"
MIRROR="${MIRROR_DIR:-/mnt/c/Users/Juanm/Documents/antigravity/modest-bell}"
LABEL="${1:-$(date +%Y%m%d)}"
OUT="$MIRROR/snapshots/manifest-cupid-$LABEL.xml"

[ -d "$TREE/.repo" ] || { echo "No hay arbol repo en $TREE" >&2; exit 1; }
mkdir -p "$MIRROR/snapshots"

cd "$TREE"
# -r fija cada proyecto al SHA que tiene ahora mismo en disco
repo manifest -r -o "$OUT"

# Metadatos del snapshot: que habia en el arbol cuando se tomo
{
  echo "label=$LABEL"
  echo "fecha=$(date -Is)"
  echo "tree=$TREE"
  echo "proyectos=$(grep -c '<project' "$OUT" || true)"
  echo "host=$(hostname)"
  if [ -f "$TREE/build/make/core/build_id.mk" ]; then
    echo "build_id=$(grep -m1 '^BUILD_ID' "$TREE/build/make/core/build_id.mk" | tr -d ' ')"
  fi
} > "$MIRROR/snapshots/manifest-cupid-$LABEL.info"

echo "Snapshot escrito: $OUT"
echo "Proyectos fijados: $(grep -c '<project' "$OUT" || true)"
echo
echo "Commitear desde Windows:"
echo "  git -C \"$MIRROR\" add snapshots/ && git -C \"$MIRROR\" commit -m \"snapshot: manifest cupid $LABEL\""
