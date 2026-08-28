#!/usr/bin/env python3
"""Cierra en las notas lo que ha dado de si el modo de 50 MP, con las medidas."""

P = '/home/android/evolution-x/device/xiaomi/cupid/NOTAS-RENDIMIENTO.md'

TEXTO = '''
## Que dan de si los 50 MP (medido con luz, 24-08)

Tres versiones de la misma escena (movil fijo, interior con ventana):

| version                                   | dif. tras reescalar | detalle | luz media | quemado |
|-------------------------------------------|--------------------:|--------:|----------:|--------:|
| reescalado (sin la etiqueta de remosaico)  |              0,0044 |  0,0246 |      89,3 |  2,73 % |
| via estandar (SENSOR_PIXEL_MODE maximo)    |              0,0040 |  0,0197 |      86,4 |  2,03 % |
| via de Xiaomi (xiaomi.remosaic.enabled)    |              0,0097 |  0,0475 |     137,8 |  3,19 % |

Lecturas:

  - **La via estandar de Android no sirve para lo que buscamos.** El HAL declara
    `ULTRA_HIGH_RESOLUTION_SENSOR` y acepta la sesion, pero lo que devuelve no
    tiene mas informacion que una foto de 12,6 MP ampliada: se queda incluso por
    debajo de la referencia. Eso si, el color y la exposicion salen bien.
  - **La via de Xiaomi es la unica que sube**, pero al mirar al 100% la misma
    zona (una rejilla de aire acondicionado, que es lo que mas textura tiene de
    la escena) se ve que buena parte de ese "detalle" son **artefactos**: la
    rejilla sale con franjas azules y moradas, mientras que en la version
    reescalada la misma rejilla se ve limpia y gris. Y toda la foto lleva un
    tinte rosa/lila: una pared que la otra via saca beige (R/G 1,23, B/G 0,86)
    ella la saca rosa (R/G 1,38, B/G 1,05).
  - `xiaomi.pureView.enabled` **no aporta nada**: quitandola y dejando solo
    `xiaomi.remosaic.enabled` sale exactamente igual (detalle 0,0455, luz 137,2).
    O sea que quien manda es la etiqueta de remosaico.
  - El color de esa ruta **no se puede corregir desde la app**: copiar las
    ganancias y la matriz de la vista previa no cambia el resultado (el HAL las
    ignora), y con ganancias globales en post tampoco, porque el desvio depende
    del tono (en los blancos casi no hay, en los medios es del 14-21 %).
  - Lo unico que si responde es la **compensacion de exposicion**: con
    `persist.cam50.ev -6` (un paso de EV menos) el quemado baja del 3,19 % al
    0,74 %, mejor que ninguna de las otras dos, y la resolucion no se resiente.

Conclusion practica: para el dia a dia sigue siendo mejor la camara normal de
12,6 MP; el modo de 50 MP se queda como experimento util (funciona, guarda
8192x6144 en 1,3 s y aguanta disparos seguidos) pero con un color que no es de
fiar. Si algun dia aparecen los datos de crosstalk del modulo (la region
CrossTalk de su EEPROM esta declarada con tamano 0) esto cambiaria.
'''

s = open(P, encoding='utf-8').read()
if 'Que dan de si los 50 MP' in s:
    print('ya estaba')
else:
    open(P, 'a', encoding='utf-8').write(TEXTO)
    print('notas cerradas sobre los 50 MP')
