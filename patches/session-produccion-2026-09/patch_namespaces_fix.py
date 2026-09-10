import os

common_mk = '/home/android/evolution-x/device/xiaomi/sm8450-common/common.mk'

with open(common_mk, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'PRODUCT_SOONG_NAMESPACES += hardware/qcom-caf/sm8450/' in line:
        # Ignore all subdirectories under sm8450
        continue
    new_lines.append(line)

new_lines.append('PRODUCT_SOONG_NAMESPACES += hardware/qcom-caf/sm8450\n')

with open(common_mk, 'w') as f:
    f.writelines(new_lines)

print("Namespaces fixed!")
