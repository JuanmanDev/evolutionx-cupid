#!/usr/bin/env bash
# Recrea el arbol de Evolution X exactamente como estaba en un snapshot,
# y reaplica los parches propios.
#
# Uso (WSL):  ./scripts/restore-tree.sh snapshots/manifest-cupid-20260917.xml [destino]
set -euo pipefail

SNAP="${1:?Falta la ruta del manifest snapshot}"
DEST="${2:-/home/android/evolution-x}"
MIRROR="${MIRROR_DIR:-/mnt/c/Users/Juanm/Documents/antigravity/modest-bell}"
JOBS="${SYNC_JOBS:-8}"

[ -f "$SNAP" ] || { echo "No existe $SNAP" >&2; exit 1; }

mkdir -p "$DEST"
cd "$DEST"

if [ ! -d .repo ]; then
  repo init -u https://github.com/Evolution-X/manifest -b bka --git-lfs
fi

# El manifest fijado manda: cada proyecto vuelve a su SHA exacto
cp "$SNAP" .repo/manifests/snapshot-cupid.xml
repo init -m snapshot-cupid.xml
repo sync -c --no-clone-bundle --no-tags -j"$JOBS"

echo
echo "Arbol sincronizado al snapshot. Reaplicar parches:"
echo "  cd $MIRROR/patches && ./apply-patches.sh $DEST"
