#!/usr/bin/env python3
"""Corrige addQuadCfaActiveArrayFull: los punteros de find() se invalidan cuando
update() realoca el buffer de metadata. Se copian los valores a arrays locales
antes de tocar nada. Ese uso-tras-liberar daba -38 al actualizar."""
CPM = ("/home/android/evolution-x/frameworks/av/services/camera/libcameraservice/"
       "common/CameraProviderManager.cpp")
s = open(CPM, encoding="utf-8").read()

viejo = """    auto& c = mCameraCharacteristics;
    auto pixelMax = c.find(ANDROID_SENSOR_INFO_PIXEL_ARRAY_SIZE_MAXIMUM_RESOLUTION);
    auto activeMax = c.find(ANDROID_SENSOR_INFO_ACTIVE_ARRAY_SIZE_MAXIMUM_RESOLUTION);
    if (pixelMax.count != 2 || activeMax.count != 4) {
        return OK;  // solo la camara que declara tamano de maxima resolucion
    }
    status_t res = c.update(ANDROID_SENSOR_INFO_PIXEL_ARRAY_SIZE, pixelMax.data.i32, 2);
    if (res == OK) {
        res = c.update(ANDROID_SENSOR_INFO_ACTIVE_ARRAY_SIZE, activeMax.data.i32, 4);
    }
    if (res == OK) {
        res = c.update(ANDROID_SENSOR_INFO_PRE_CORRECTION_ACTIVE_ARRAY_SIZE,
                activeMax.data.i32, 4);
    }
    if (res == OK) {
        ALOGI("%s: area activa a resolucion completa %dx%d en la camara %s",
                __FUNCTION__, activeMax.data.i32[2], activeMax.data.i32[3], mId.c_str());"""

nuevo = """    auto& c = mCameraCharacteristics;
    auto pixelMax = c.find(ANDROID_SENSOR_INFO_PIXEL_ARRAY_SIZE_MAXIMUM_RESOLUTION);
    auto activeMax = c.find(ANDROID_SENSOR_INFO_ACTIVE_ARRAY_SIZE_MAXIMUM_RESOLUTION);
    if (pixelMax.count != 2 || activeMax.count != 4) {
        return OK;  // solo la camara que declara tamano de maxima resolucion
    }
    // Los punteros de find() apuntan al buffer de metadata y update() puede
    // realocarlo, dejandolos colgando. Se copian los valores antes de tocar nada.
    const int32_t pix[2] = { pixelMax.data.i32[0], pixelMax.data.i32[1] };
    const int32_t act[4] = { activeMax.data.i32[0], activeMax.data.i32[1],
                             activeMax.data.i32[2], activeMax.data.i32[3] };
    status_t res = c.update(ANDROID_SENSOR_INFO_PIXEL_ARRAY_SIZE, pix, 2);
    if (res == OK) {
        res = c.update(ANDROID_SENSOR_INFO_ACTIVE_ARRAY_SIZE, act, 4);
    }
    if (res == OK) {
        res = c.update(ANDROID_SENSOR_INFO_PRE_CORRECTION_ACTIVE_ARRAY_SIZE, act, 4);
    }
    if (res == OK) {
        ALOGI("%s: area activa a resolucion completa %dx%d en la camara %s",
                __FUNCTION__, act[2], act[3], mId.c_str());"""

assert viejo in s, "no encuentro el bloque viejo (ya corregido?)"
open(CPM, "w", encoding="utf-8").write(s.replace(viejo, nuevo, 1))
print("addQuadCfaActiveArrayFull corregido (copia valores antes de update)")
