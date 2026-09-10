import os

display_mk = '/home/android/evolution-x/hardware/qcom-caf/sm8450/display/config/display-product.mk'

with open(display_mk, 'r') as f:
    d_lines = f.readlines()

new_d_lines = []
for line in d_lines:
    if 'libdisplayconfig \\' in line or 'libdisplayconfig' == line.strip():
        continue
    if 'libdisplayconfig.vendor' in line:
        continue
    if 'libqdMetaData.system' in line:
        continue
    if 'vendor.qti.hardware.display.config-V5-ndk' in line:
        continue
    if 'vendor.qti.hardware.display.config.vendor' in line:
        continue
    new_d_lines.append(line)

with open(display_mk, 'w') as f:
    f.writelines(new_d_lines)

# Also check common.mk just in case
common_mk = '/home/android/evolution-x/device/xiaomi/sm8450-common/common.mk'
with open(common_mk, 'r') as f:
    c_lines = f.readlines()

new_c_lines = []
for line in c_lines:
    if 'libdisplayconfig' in line:
        continue
    if 'libqdMetaData.system' in line:
        continue
    if 'vendor.qti.hardware.display.config-V5-ndk' in line:
        continue
    if 'vendor.qti.hardware.display.config.vendor' in line:
        continue
    new_c_lines.append(line)

with open(common_mk, 'w') as f:
    f.writelines(new_c_lines)

print("Final cleanup 2 done!")
