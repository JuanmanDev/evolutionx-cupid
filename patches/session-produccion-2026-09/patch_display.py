import os

display_mk = '/home/android/evolution-x/hardware/qcom-caf/sm8450/display/config/display-product.mk'

with open(display_mk, 'r') as f:
    data = f.read()

# Replace the incorrect hardware/qcom/display/config path with the CAF one
data = data.replace('hardware/qcom/display/config/', 'hardware/qcom-caf/sm8450/display/config/')

with open(display_mk, 'w') as f:
    f.write(data)

print("Patched display-product.mk with correct hardware/qcom-caf path!")
