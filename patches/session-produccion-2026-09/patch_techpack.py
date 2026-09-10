import os

common_mk = '/home/android/evolution-x/device/xiaomi/sm8450-common/common.mk'

with open(common_mk, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'hardware/qcom-caf/sm8450/display/config/display-product.mk' in line:
        new_lines.append('BUILD_DISPLAY_TECHPACK_SOURCE := true\n')
    new_lines.append(line)

with open(common_mk, 'w') as f:
    f.writelines(new_lines)

print("Techpack patched!")
