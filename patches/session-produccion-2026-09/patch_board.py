import os

board_mk = '/home/android/evolution-x/device/xiaomi/sm8450-common/BoardConfigCommon.mk'

with open(board_mk, 'r') as f:
    lines = f.readlines()

has_version = any('TARGET_KERNEL_VERSION' in line for line in lines)
has_source = any('TARGET_KERNEL_SOURCE' in line for line in lines)

print(f"Has TARGET_KERNEL_VERSION: {has_version}")
print(f"Has TARGET_KERNEL_SOURCE: {has_source}")

if not has_version:
    with open(board_mk, 'a') as f:
        f.write('\n# Kernel Version Fix\nTARGET_KERNEL_VERSION := 5.10\n')
    print("Appended TARGET_KERNEL_VERSION := 5.10")

