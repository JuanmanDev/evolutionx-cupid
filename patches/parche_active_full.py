#!/usr/bin/env python3
"""Opcion 2: declarar el area activa del sensor Quad-Bayer a resolucion completa.

libgcam (motor de GCam) exige que el RAW maximo del sensor coincida con el area
activa o el pixel array. En Quad-Bayer el RAW maximo (8192x6144) es el doble del
area activa binned (4096x3072): por eso LMC8.4 se cierra
    libgcam: frame_raw_max (8192x6144) matches neither active (4096x3072) nor pixel array
y por eso el GCam nuevo, que lo tolera, captura solo a 12,6 MP (usa el area
activa como tamano).

Con persist.sys.camera.qcfa_active_full 1 se declara el area activa, el pixel
array y el area activa precorreccion al tamano completo, para que la app pida el
flujo de 8192x6144. Cambia la geometria que ven todas las apps: por eso apagado
por defecto y reversible en caliente.
"""
D = "/home/android/evolution-x/frameworks/av/services/camera/libcameraservice/"
CPM = D + "common/CameraProviderManager.cpp"
H   = D + "common/CameraProviderManager.h"
HID = D + "common/hidl/HidlProviderInfo.cpp"

# 1) metodo nuevo, justo tras addQuadCfaFullSizeJpeg (que termina en su return)
c = open(CPM, encoding="utf-8").read()
ancla = "    return CameraProviderManager::aplicarJpegCompletoQuadCfa(mCameraCharacteristics, mId);\n}\n"
assert ancla in c, "no encuentro el final de addQuadCfaFullSizeJpeg"
metodo = ancla + """
status_t CameraProviderManager::ProviderInfo::DeviceInfo3::addQuadCfaActiveArrayFull() {
    // libgcam exige que el RAW maximo coincida con el area activa o el pixel
    // array. En Quad-Bayer el RAW maximo dobla al area activa binned, asi que
    // GCam se cierra o captura a resolucion reducida. Aqui se declara la
    // geometria del sensor a resolucion completa para que la app pida los 50 MP.
    // Cambia el recorte/zoom que ven todas las apps: apagado por defecto.
    //     setprop persist.sys.camera.qcfa_active_full 1
    if (property_get_int32("persist.sys.camera.qcfa_active_full", 0) == 0) {
        return OK;
    }
    auto& c = mCameraCharacteristics;
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
                __FUNCTION__, activeMax.data.i32[2], activeMax.data.i32[3], mId.c_str());
    } else {
        ALOGE("%s: no se pudo declarar el area activa completa: %s (%d)",
                __FUNCTION__, strerror(-res), res);
    }
    return res;
}
"""
if "addQuadCfaActiveArrayFull" not in c:
    c = c.replace(ancla, metodo, 1)
    open(CPM, "w", encoding="utf-8").write(c)
    print("metodo anadido a CameraProviderManager.cpp")
else:
    print("metodo ya estaba")

# 2) declaracion en el .h
h = open(H, encoding="utf-8").read()
anclaH = "            status_t addQuadCfaFullSizeJpeg();\n"
assert anclaH in h
if "addQuadCfaActiveArrayFull" not in h:
    h = h.replace(anclaH, anclaH + "            status_t addQuadCfaActiveArrayFull();\n", 1)
    open(H, "w", encoding="utf-8").write(h)
    print("declaracion anadida al .h")
else:
    print("declaracion ya estaba")

# 3) llamada en HidlProviderInfo.cpp, tras addQuadCfaFullSizeJpeg()
hid = open(HID, encoding="utf-8").read()
anclaHid = """    res = addQuadCfaFullSizeJpeg();
    if (OK != res) {
        ALOGE("%s: No se pudo anunciar el tamano completo del sensor como foto: %s (%d)",
                __FUNCTION__, strerror(-res), res);
    }
"""
assert anclaHid in hid, "no encuentro la llamada a addQuadCfaFullSizeJpeg en Hidl"
llamada = anclaHid + """    res = addQuadCfaActiveArrayFull();
    if (OK != res) {
        ALOGE("%s: No se pudo declarar el area activa completa: %s (%d)",
                __FUNCTION__, strerror(-res), res);
    }
"""
if "addQuadCfaActiveArrayFull" not in hid:
    hid = hid.replace(anclaHid, llamada, 1)
    open(HID, "w", encoding="utf-8").write(hid)
    print("llamada anadida a HidlProviderInfo.cpp")
else:
    print("llamada ya estaba")
