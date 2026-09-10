import os

common_mk = '/home/android/evolution-x/device/xiaomi/sm8450-common/common.mk'
board_mk = '/home/android/evolution-x/device/xiaomi/sm8450-common/BoardConfigCommon.mk'

common_appends = """
# Include QCOM Display configs
$(call inherit-product-if-exists, hardware/qcom-caf/sm8450/display/config/display-product.mk)
$(call inherit-product-if-exists, hardware/qcom-caf/sm8450/audio/configs/sm8450/sm8450.mk)
$(call inherit-product-if-exists, hardware/qcom-caf/sm8450/audio/primary-hal/configs/audio_vendor_product.mk)

PRODUCT_SOONG_NAMESPACES += hardware/qcom-caf/sm8450/data-ipa-cfg-mgr
"""

board_appends = """
# Include QCOM Display Board Configs
include hardware/qcom-caf/sm8450/display/config/display-board.mk
include hardware/qcom-caf/sm8450/audio/configs/audio_board.mk
"""

with open(common_mk, 'a') as f:
    f.write("\n" + common_appends)

with open(board_mk, 'a') as f:
    f.write("\n" + board_appends)

print("Makefiles patched successfully!")
