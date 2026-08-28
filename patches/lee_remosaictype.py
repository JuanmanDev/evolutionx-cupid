#!/usr/bin/env python3
"""Lee el tipo de remosaico que declara cada modo del sensor.

El sensormodule de camx guarda cada campo como: nombre en 32 bytes, marca
ffffffff, offset (u32), tamano (u32) e identificador (u32). Los campos ausentes
apuntan todos al mismo hueco con tamano 0 (asi esta CrossTalk en este modulo).
"""
import struct

B = ('/home/android/evolution-x/vendor/xiaomi/cupid/proprietary/vendor/lib64/'
     'camera/com.qti.sensormodule.cupid_semco_imx766_wide.bin')
d = open(B, 'rb').read()


def campos(nombre):
    aguja = nombre.encode()
    pos = 0
    salida = []
    while True:
        i = d.find(aguja, pos)
        if i < 0:
            break
        pos = i + 1
        # El nombre ocupa 40 bytes; detras van ffffffff, offset, tamano e id.
        if d[i + 40:i + 44] != b'\xff\xff\xff\xff':
            continue
        off, tam, ident = struct.unpack_from('<III', d, i + 44)
        salida.append((i, off, tam, ident))
    return salida


for nombre in ('RemosaicTypeInfo', 'CrossTalk', 'resolutionInfo'):
    print('== %s' % nombre)
    for i, off, tam, ident in campos(nombre):
        val = ''
        if tam == 4 and off + 4 <= len(d):
            val = 'valor=%d' % struct.unpack_from('<I', d, off)[0]
        elif tam:
            val = 'datos=%s' % d[off:off + min(tam, 16)].hex()
        print('  en %7d -> offset %7d, tamano %5d, id %4d %s'
              % (i, off, tam, ident, val))
