#!/usr/bin/env python3
"""
Fix de volumen: notificaciones ocasionalmente altas y multimedia con pantalla
apagada inconsistente.

CAUSA (medida en el movil):
  Android guarda el volumen POR DISPOSITIVO DE SALIDA. El indice del dispositivo
  AUDIO_DEVICE_OUT_DEFAULT (el fallback) NO es controlable por los ajustes: el
  bucle de readSettings itera DEVICE_OUT_ALL_SET, que no incluye DEFAULT. Ese
  indice queda congelado en DEFAULT_STREAM_VOLUME[] (music=5, ring/notif=7) y
  solo cambia con `cmd audio set-device-volume`. Cuando la reproduccion cae a ese
  fallback (ruta transitoria / cold-path), suena al nivel fijo y no al del usuario.
  No es Dolby (vendor.audio.dolby.ds2.enabled=false).

FIX:
  En VolumeStreamState.getIndex(int device): cuando el dispositivo no esta
  configurado (index==-1) o es DEVICE_OUT_DEFAULT, devolver el indice del
  DEVICE_OUT_SPEAKER (el que controla el slider de Ajustes) en vez del DEFAULT
  congelado. Cambia el VALOR DEVUELTO, no el almacenado (dumpsys sigue mostrando
  default:5). BT/auriculares tienen indice propio -> no se tocan. Cubre
  notificaciones y multimedia, desde el arranque, 100% en la ROM, sin KernelSU.

Fichero:
  frameworks/base/services/core/java/com/android/server/audio/AudioService.java

Idempotente: se puede volver a pasar (busca el marcador EvoX).
Uso:  python3 patches/parche_volumen_getindex.py   (desde la raiz del arbol AOSP)
"""
import sys, io, os

F = "frameworks/base/services/core/java/com/android/server/audio/AudioService.java"

ORIG = """        public int getIndex(int device) {
            synchronized (mVolumeStateLock) {
                int index = mIndexMap.get(device, -1);
                if (index == -1) {
                    // there is always an entry for AudioSystem.DEVICE_OUT_DEFAULT
                    index = mIndexMap.get(AudioSystem.DEVICE_OUT_DEFAULT);
                }
                return index;
            }
        }"""

NEW = """        public int getIndex(int device) {
            synchronized (mVolumeStateLock) {
                int index = mIndexMap.get(device, -1);
                // EvoX: for the default/unconfigured output device, use the loudspeaker level
                // (the volume the user controls in Settings) instead of the fixed default index,
                // so transient/cold-path playback is not louder or quieter than expected
                // (fixes occasional loud notifications and inconsistent media with screen off).
                if (index == -1 || device == AudioSystem.DEVICE_OUT_DEFAULT) {
                    int spk = mIndexMap.get(AudioSystem.DEVICE_OUT_SPEAKER, -1);
                    if (spk != -1) {
                        index = spk;
                    } else if (index == -1) {
                        // there is always an entry for AudioSystem.DEVICE_OUT_DEFAULT
                        index = mIndexMap.get(AudioSystem.DEVICE_OUT_DEFAULT);
                    }
                }
                return index;
            }
        }"""


def main():
    if not os.path.isfile(F):
        print("No encuentro %s (ejecuta desde la raiz del arbol AOSP)" % F)
        return 1
    src = io.open(F, encoding="utf-8").read()
    if "EvoX: for the default/unconfigured output device" in src:
        print("Ya aplicado (marcador EvoX presente). Nada que hacer.")
        return 0
    if ORIG not in src:
        print("No encuentro el getIndex original de VolumeStreamState; "
              "puede que el arbol haya cambiado. Revisar a mano.")
        return 2
    src = src.replace(ORIG, NEW, 1)
    io.open(F, "w", encoding="utf-8").write(src)
    print("OK: getIndex parcheado (fallback a DEVICE_OUT_SPEAKER).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
