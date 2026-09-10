import os
import re

common_mk = '/home/android/evolution-x/device/xiaomi/sm8450-common/common.mk'
board_mk = '/home/android/evolution-x/device/xiaomi/sm8450-common/BoardConfigCommon.mk'

with open(board_mk, 'r') as f:
    board_content = f.read()

board_content = board_content.replace('include hardware/qcom-caf/sm8450/audio/configs/audio_board.mk', '')

with open(board_mk, 'w') as f:
    f.write(board_content)

with open(common_mk, 'r') as f:
    common_content = f.read()

common_content = common_content.replace('$(call inherit-product-if-exists, hardware/qcom-caf/sm8450/audio/configs/sm8450/sm8450.mk)', '$(call inherit-product-if-exists, hardware/qcom-caf/sm8450/audio/primary-hal/configs/taro/taro.mk)')

with open(common_mk, 'w') as f:
    f.write(common_content)

print("Makefiles fixed!")
