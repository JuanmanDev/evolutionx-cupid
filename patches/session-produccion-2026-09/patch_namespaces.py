import re

file_path = '/home/android/evolution-x/device/xiaomi/sm8450-common/common.mk'

namespaces_to_add = """
PRODUCT_SOONG_NAMESPACES += hardware/qcom-caf/sm8450/audio
PRODUCT_SOONG_NAMESPACES += hardware/qcom-caf/sm8450/display
PRODUCT_SOONG_NAMESPACES += hardware/qcom-caf/sm8450/media
PRODUCT_SOONG_NAMESPACES += hardware/qcom-caf/thermal
PRODUCT_SOONG_NAMESPACES += hardware/qcom-caf/bootctrl
PRODUCT_SOONG_NAMESPACES += vendor/qcom/opensource/data-ipa-cfg-mgr
PRODUCT_SOONG_NAMESPACES += vendor/qcom/opensource/audio-hal/primary-hal
PRODUCT_SOONG_NAMESPACES += hardware/qcom/sm7250/display/composer
PRODUCT_SOONG_NAMESPACES += hardware/qcom/sm8150/display/composer
"""

with open(file_path, 'r') as f:
    content = f.read()

if 'hardware/qcom-caf/sm8450/display' not in content:
    with open(file_path, 'a') as f:
        f.write("\n" + namespaces_to_add)
    print("Patched common.mk namespaces!")
else:
    print("Already patched!")
