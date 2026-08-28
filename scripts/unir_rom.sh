#!/usr/bin/env bash
# Une los trozos de la ROM (rom.zip.part-aa, part-ab, ...) en un solo rom.zip y
# comprueba el hash. GitHub no admite ficheros de mas de 2 GB en una release, asi
# que la ROM se sube partida en trozos.
#
#   ./unir_rom.sh [CARPETA]
#
# En la carpeta tiene que haber:  rom.zip.part-*   y   rom.zip.sha256
set -euo pipefail
DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

cd "$DIR"
PARTES=(rom.zip.part-*)
if [ ! -e "${PARTES[0]}" ]; then echo "no encuentro rom.zip.part-* en $DIR"; exit 1; fi

echo "== uniendo ${#PARTES[@]} trozos"
cat rom.zip.part-* > rom.zip
echo "   rom.zip: $(du -h rom.zip | cut -f1)"

if [ -f rom.zip.sha256 ]; then
  echo "== comprobando hash"
  if command -v sha256sum >/dev/null; then
    sha256sum -c rom.zip.sha256 || { echo "HASH NO COINCIDE: descarga corrupta"; exit 1; }
  else
    echo "   (sha256sum no disponible; comprueba a mano con rom.zip.sha256)"
  fi
fi
echo "== listo: rom.zip. Ya puedes usar flashear_todo.sh"
