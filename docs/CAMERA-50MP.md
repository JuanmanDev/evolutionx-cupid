# 50 MP camera on cupid — deep technical notes

What was learned analysing the HyperOS firmware and measuring on the phone. Read
[`50MP.md`](50MP.md) first for the summary. *(Spanish: [`CAMERA-50MP.es.md`](CAMERA-50MP.es.md).)*

## The four pieces for real 8192×6144

All required together:

1. **Package in the camera privapp list**:
   `persist.vendor.camera.privapp.list=com.cupid.cam50,...` (set in `device.mk`).
   Without it the same session returns 1920×1440.
2. **Operating mode `0x80F3`** in `createCustomCaptureSession()` (@SystemApi, hence
   `platform_apis`). `0x80F3` =
   `SESSION_OPERATION_MODE_NORMAL_ULTRA_PIXEL_PHOTOGRAPHY`, a constant pulled from
   `Lcom/xiaomi/engine/CameraOperationMode;` in MiuiCamera's `classes4.dex`. With
   `0x8001` (MIUI_BACK) you get 4096×3072.
3. **Two streams**: a small one plus the big 8192×6144. With only the big one,
   `onConfigureFailed`.
4. **The `xiaomi.remosaic.enabled` tag** on the request. This is what brings real
   resolution: over four shots of the same scene, the halve-and-re-enlarge detail
   metric drops from 0.037 with the tag to 0.004 without, and Laplacian energy
   from 0.175 to 0.023. Without the tag the HAL returns an **upscale** even though
   the file measures 8192×6144. `xiaomi.pureView.enabled` does not change
   resolution.

Why Xiaomi's own path is needed: `IFEMaxLineWidth=7296 < 8192`, so the ISP can't
process that width in one pass; Xiaomi does it in strips in its offline (MIVI)
pipeline, which that operating mode selects.

## Why the app uses two sessions

The preview **cannot** live inside the `0x80F3` session. Its pipeline
(`RealTimeFeatureZSLPreviewRaw`) keeps memory reserved in the `icp` SMMU bank; on
shutter the HAL brings up `QuadCFAFullSizeStatsParse`, `RealtimeFeatureSWRemosaic`
and `ZSLSnapshotYUVHAL` at once, and the IOVA reservation runs out:

    CAM-SMMU: cam_smmu_map_buffer_validate: IOVA alloc failed for shared memory, cb:icp
    CSLAllocHW() Allocating CSL Buffer failed
    camxcmdbuffermanager.cpp: InitializePool() Out of memory

and the camera dies with `ERROR_CAMERA_DEVICE` (4). `stopRepeating()` does not fix
it because the pipeline is still running — the session has to be **closed**. So
the preview runs in a normal session and the `0x80F3` one is created only for the
shot, used once, and closed. That gives 16–18 MB JPEGs, three shots in a row
without failure, ~1.3 s shutter-to-file.

## The colour problem

With `xiaomi.remosaic.enabled` the detail is real (2 mm letters readable at 3 m)
but the image has a **magenta tint and a fine grid**, channel means around
R=71 G=49 B=79 (green halved). The HAL log:

    E/REMOSAIC-NODE: LibInit() REMOSAIC XTALK DATA GET Err
    E/Remosaic: runGainmapGen: pd_xtc_status(2), SPAF xtalk EEPROM data is invalid

`com.qti.node.remosaic.so` looks for
`/data/vendor/camera/remosaic_crosstalk_data.bin` (does not exist; generated at
runtime, not in any partition) and the module's EEPROM gives no valid crosstalk
data. Without the gain map the remosaic **does not relocate** pixels, so the ISP
demosaics 2×2 same-colour blocks as if they were normal Bayer. The HAL even hints
why it isn't compensated elsewhere:

    isHWRemosaic = true, set WB gain
    isHWRemosaic = false, not to set WB gain

Correcting it in post with per-channel gains **does not work** (measured: global
gains leave the violet unchanged), because it is a mis-placed pattern, not an
imbalance.

## GCam: pushed to the framework and still impossible

The active-array patch made GCam recognise the full-res sensor, configure a RAW10
8192×6144 stream and start HDR+, but the frames come back **black**, and forcing
the `0x80F3` remosaic mode onto GCam's RAW stream did not change that — mode
`0x80F3` only delivers **JPEG**, never RAW/YUV at full size to a third-party
stream. Full write-up in [`50MP.md`](50MP.md).
