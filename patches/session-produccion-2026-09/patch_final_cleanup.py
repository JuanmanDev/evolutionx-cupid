import os

common_mk = '/home/android/evolution-x/device/xiaomi/sm8450-common/common.mk'
display_mk = '/home/android/evolution-x/hardware/qcom-caf/sm8450/display/config/display-product.mk'

# 1. Clean up common.mk
with open(common_mk, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'DSPVolumeSynchronizer' in line:
        continue
    if 'hardware/qcom-caf/sm8450/audio/primary-hal/configs/taro/taro.mk' in line:
        continue
    if 'hardware/qcom-caf/sm8450/audio/primary-hal/configs/audio_vendor_product.mk' in line:
        continue
    new_lines.append(line)

new_lines.append('\nPRODUCT_SOONG_NAMESPACES += hardware/qcom-caf/sm8450/data-ipa-cfg-mgr\n')

with open(common_mk, 'w') as f:
    f.writelines(new_lines)

# 2. Clean up display-product.mk
with open(display_mk, 'r') as f:
    d_lines = f.readlines()

new_d_lines = []
for line in d_lines:
    if 'vendor.qti.hardware.display.allocator-service.rc' in line:
        continue
    if 'vendor.qti.hardware.display.demura-service.rc' in line:
        continue
    if 'vendor.qti.hardware.display.demura-service.xml' in line:
        continue
    if 'android.hardware.graphics.mapper-impl-qti-display.xml' in line:
        continue
    if 'vendor.qti.hardware.display.allocator-service.xml' in line:
        continue
    if 'libdisplayconfig.qti.vendor' in line:
        continue
    new_d_lines.append(line)

with open(display_mk, 'w') as f:
    f.writelines(new_d_lines)

print("Cleanup done!")
