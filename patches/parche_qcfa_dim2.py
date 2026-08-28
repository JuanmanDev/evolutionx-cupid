#!/usr/bin/env python3
"""El tamano de 50 MP se anuncia tambien en la camara que ven las apps.

Hasta ahora solo se anunciaba donde estaba la etiqueta de Qualcomm con las
medidas del mosaico, y esa resulta ser la camara 6, que no sale en la lista que
reciben las aplicaciones (0, 2, 3, 4 y 5). O sea que el anuncio se estaba
haciendo en una camara a la que ninguna app puede llegar:

    JPEG 8192x6144 en -> == Camera device 6 dynamic info: ==

La camara principal si dice de que tamano es su sensor, solo que por otra via:

    android.sensor.info.pixelArraySize                  [4096 3072]
    android.sensor.info.pixelArraySizeMaximumResolution [8192 6144]
    android.sensor.info.binningFactor                   [2 2]

Ese ultimo par es el bueno. Antes se miraba, pero solo si la camara se
declaraba de ultra alta resolucion, y esta no lo hace: por eso se quedaba
fuera justo la que interesa. Ahora se usa aunque no lo declare, que al fin y al
cabo es el propio HAL diciendo de cuanto es el sensor.
"""
P = ('/home/android/evolution-x/frameworks/av/services/camera/libcameraservice/'
     'common/CameraProviderManager.cpp')
s = open(P, encoding='utf-8').read()

viejo = '''    // Si no esta la etiqueta, se prueba con el camino de siempre: los sensores
    // que si se declaran de ultra alta resolucion traen sus medidas ahi.
    if (fullWidth <= 0 || fullHeight <= 0) {
        auto capabilities = mCameraCharacteristics.find(ANDROID_REQUEST_AVAILABLE_CAPABILITIES);
        bool ultraHighRes = false;
        for (size_t i = 0; i < capabilities.count; i++) {
            if (capabilities.data.u8[i] ==
                    ANDROID_REQUEST_AVAILABLE_CAPABILITIES_ULTRA_HIGH_RESOLUTION_SENSOR) {
                ultraHighRes = true;
                break;
            }
        }
        if (!ultraHighRes) {
            return OK;
        }
        auto fullSize = mCameraCharacteristics.find(
                ANDROID_SENSOR_INFO_PIXEL_ARRAY_SIZE_MAXIMUM_RESOLUTION);
        if (fullSize.count != 2) {
            return OK;
        }
        fullWidth = fullSize.data.i32[0];
        fullHeight = fullSize.data.i32[1];
    }'''

nuevo = '''    // Si no esta la etiqueta, vale igual lo que diga el sensor de si mismo. No
    // se pide ademas que la camara se declare de ultra alta resolucion: la
    // principal de este movil no lo hace y es justo la que interesa, porque es
    // la unica que ven las aplicaciones.
    if (fullWidth <= 0 || fullHeight <= 0) {
        auto fullSize = mCameraCharacteristics.find(
                ANDROID_SENSOR_INFO_PIXEL_ARRAY_SIZE_MAXIMUM_RESOLUTION);
        if (fullSize.count != 2) {
            return OK;
        }
        fullWidth = fullSize.data.i32[0];
        fullHeight = fullSize.data.i32[1];
        ALOGI("%s: el sensor dice medir %dx%d a resolucion completa",
                __FUNCTION__, fullWidth, fullHeight);
    }'''

assert viejo in s, 'no aparece el camino de la capacidad'
s = s.replace(viejo, nuevo, 1)
open(P, 'w', encoding='utf-8').write(s)
print('parche aplicado')
