#!/usr/bin/env python3
"""Que cualquier app pueda hacer los 50 MP, GCam incluida.

La camara de este movil da 50 MP solo si se cumplen tres cosas a la vez:
  1. que el tamano 8192x6144 este anunciado (ya lo hace addQuadCfaFullSizeJpeg),
  2. que la sesion se cree con el modo propietario 0x80F3,
  3. que la peticion de disparo lleve la etiqueta xiaomi.remosaic.enabled.

Una app normal no hace ninguna de las dos ultimas: no las conoce. Por eso GCam
se cerraba al intentarlo y por eso el intento anterior, que solo anunciaba el
tamano, mataba el HAL: le pedia una foto de 50 MP en una sesion normal.

Aqui se hacen las dos que faltan desde el servicio de camara: si la app
configura una salida JPEG del tamano completo del sensor, se cambia el modo de
sesion y se etiquetan las peticiones que apunten a esa salida. Las apps que no
pidan 50 MP no se enteran de nada.
"""
import re

D = '/home/android/evolution-x/frameworks/av/services/camera/libcameraservice/device3/'

# ---------------------------------------------------------------- cabecera
H = D + 'Camera3Device.h'
h = open(H, encoding='utf-8').read()
ancla = '''    status_t convertMetadataListToRequestListLocked('''
assert ancla in h, 'no aparece convertMetadataListToRequestListLocked en el .h'
nuevo = '''    /**
     * Si la sesion se configuro para fotos al tamano completo del sensor, pone
     * en la peticion la etiqueta que hace que el HAL entregue los 50 MP. Sin
     * ella devuelve la imagen recortada aunque el tamano sea el grande.
     */
    void tagFullSizeQuadCfaRequestLocked(sp<CaptureRequest> &request);

    /** Medidas de la salida de foto a tamano completo, si hay alguna. */
    int32_t mFullSizeQuadCfaWidth = 0;
    int32_t mFullSizeQuadCfaHeight = 0;

''' + ancla
h = h.replace(ancla, nuevo, 1)
open(H, 'w', encoding='utf-8').write(h)
print('cabecera lista')

# ---------------------------------------------------------------- fuente
C = D + 'Camera3Device.cpp'
c = open(C, encoding='utf-8').read()

# 1) Al configurar: si hay una salida JPEG del tamano completo, se cambia el
#    modo de sesion al propietario.
ancla = '''    bool isConstrainedHighSpeed =
            CAMERA_STREAM_CONFIGURATION_CONSTRAINED_HIGH_SPEED_MODE == operatingMode;'''
assert ancla in c, 'no aparece isConstrainedHighSpeed'
nuevo = '''    // Fotos al tamano completo del sensor: el HAL solo las hace dentro de su
    // modo de sesion propietario. Si se le pide una salida JPEG de ese tamano
    // en una sesion normal, se muere. Como la app no puede saberlo, el cambio
    // de modo se hace aqui.
    mFullSizeQuadCfaWidth = 0;
    mFullSizeQuadCfaHeight = 0;
    {
        const int32_t modoQuadCfa =
                property_get_int32("persist.sys.camera.qcfa_mode", 0x80F3);
        for (size_t i = 0; modoQuadCfa != 0 && i < mOutputStreams.size(); i++) {
            sp<Camera3OutputStreamInterface> stream = mOutputStreams[i];
            if (stream == nullptr) continue;
            if (stream->getFormat() != HAL_PIXEL_FORMAT_BLOB) continue;
            // Cualquier JPEG mas grande que la mayor foto que el HAL anuncia
            // por si mismo tiene que ir por el camino de resolucion completa.
            if ((int64_t) stream->getWidth() * stream->getHeight()
                    <= (int64_t) 4208 * 3120) {
                continue;
            }
            mFullSizeQuadCfaWidth = stream->getWidth();
            mFullSizeQuadCfaHeight = stream->getHeight();
            if (operatingMode != modoQuadCfa) {
                ALOGI("%s: foto de %dx%d: se pasa del modo de sesion %d al %d",
                        __FUNCTION__, mFullSizeQuadCfaWidth, mFullSizeQuadCfaHeight,
                        operatingMode, modoQuadCfa);
                operatingMode = modoQuadCfa;
            }
            break;
        }
    }

''' + ancla
c = c.replace(ancla, nuevo, 1)

# 2) Al preparar cada peticion: se etiqueta la que apunte a esa salida.
ancla = '''        newRequest->mResultExtras.requestId = requestIdEntry.data.i32[0];

        requestList->push_back(newRequest);'''
assert ancla in c, 'no aparece el sitio donde se apila la peticion'
nuevo = '''        newRequest->mResultExtras.requestId = requestIdEntry.data.i32[0];

        tagFullSizeQuadCfaRequestLocked(newRequest);

        requestList->push_back(newRequest);'''
c = c.replace(ancla, nuevo, 1)

# 3) El metodo.
ancla = '''status_t Camera3Device::capture(CameraMetadata &request, int64_t* lastFrameNumber) {'''
assert ancla in c
metodo = '''void Camera3Device::tagFullSizeQuadCfaRequestLocked(sp<CaptureRequest> &request) {
    if (mFullSizeQuadCfaWidth <= 0 || request == nullptr) {
        return;
    }
    bool esFotoCompleta = false;
    for (size_t i = 0; i < request->mOutputStreams.size(); i++) {
        const sp<Camera3OutputStreamInterface> &stream = request->mOutputStreams[i];
        if (stream != nullptr
                && stream->getWidth() == mFullSizeQuadCfaWidth
                && stream->getHeight() == mFullSizeQuadCfaHeight) {
            esFotoCompleta = true;
            break;
        }
    }
    if (!esFotoCompleta || request->mSettingsList.empty()) {
        return;
    }

    CameraMetadata &ajustes = request->mSettingsList.begin()->metadata;
    sp<VendorTagDescriptor> vTags;
    sp<VendorTagDescriptorCache> vCache = VendorTagDescriptorCache::getGlobalVendorTagCache();
    if (vCache.get() != nullptr) {
        const camera_metadata_t *buffer = ajustes.getAndLock();
        metadata_vendor_id_t vendorId = get_camera_metadata_vendor_id(buffer);
        ajustes.unlock(buffer);
        vCache->getVendorTagDescriptor(vendorId, &vTags);
    }
    uint32_t tag = 0;
    if (CameraMetadata::getTagFromName("xiaomi.remosaic.enabled", vTags.get(), &tag) != OK) {
        ALOGW("%s: el HAL no tiene xiaomi.remosaic.enabled", __FUNCTION__);
        return;
    }
    const uint8_t encendido = 1;
    status_t res = ajustes.update(tag, &encendido, 1);
    if (res != OK) {
        ALOGW("%s: no se pudo poner xiaomi.remosaic.enabled: %d", __FUNCTION__, res);
    }
}

''' + ancla
c = c.replace(ancla, metodo, 1)

open(C, 'w', encoding='utf-8').write(c)
print('fuente listo')
