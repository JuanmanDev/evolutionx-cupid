# Parches del framework AOSP

Scripts en Python que aplican los cambios de esta ROM sobre el árbol de Evolution
X (`frameworks/av`, principalmente el servicio de cámara). Cada uno lleva su
explicación completa en el docstring de arriba. Se aplican con `python3 fichero.py`
desde la raíz del árbol, y son **idempotentes** (se pueden volver a pasar).

| Script | Qué hace |
|---|---|
| `parche_qcfa_dim2.py` | Anuncia el tamaño completo del sensor (8192×6144) como tamaño de foto en la cámara que ven las apps. Gated por `persist.sys.camera.qcfa_jpeg`. |
| `parche_gcam50.py` | En `Camera3Device`: cambia la sesión al modo propietario `0x80F3` y etiqueta `xiaomi.remosaic.enabled` cuando una app pide una salida JPEG a tamaño completo. Es lo que hace posible el 50 MP real. |
| `parche_active_full.py` | Experimento (opción "GCam 50 MP"): declara el área activa del sensor a 8192×6144. Gated por `persist.sys.camera.qcfa_active_full`. Ver abajo. |
| `fix_active_full.py` | Arregla un uso-tras-liberar en el anterior (los punteros de `find()` se invalidan al hacer `update()`). |
| `lee_remosaictype.py` | Diagnóstico: lee del `sensormodule` la región `CrossTalk` del EEPROM (sale a tamaño 0: por eso el 50 MP tiene tinte). |
| `notas_50mp.py` | Cierra en las notas las medidas de los tres caminos de 50 MP. |
| `parche_volumen_getindex.py` | `AudioService.getIndex()`: para el dispositivo DEFAULT o no configurado, devuelve el índice del altavoz (el del slider) en vez del DEFAULT congelado. Arregla notificaciones ocasionalmente altas y multimedia con pantalla apagada. 100% ROM, sin KernelSU. |

## Sobre `parche_active_full.py` (GCam a 50 MP): probado y descartado

Con este parche + `qcfa_jpeg=1`, GCam **deja de crashear**, reconoce el sensor a
8192×6144 y llega a configurar un stream RAW10 a esa resolución y arrancar HDR+.
Pero los fotogramas full-res salen **negros**: el HAL de este chip no entrega
imagen válida a resolución completa a una app de terceros por la vía RAW/YUV —
solo como JPEG por el remosaico propietario de Xiaomi. Medido hasta el final. Por
eso GCam a 50 MP es **imposible** aquí y el parche queda apagado por defecto. El
detalle completo está en [`../docs/50MP.md`](../docs/50MP.md).
