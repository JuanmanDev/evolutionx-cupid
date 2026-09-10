import re

file_path = '/home/android/evolution-x/hardware/qcom-caf/sm8650/display/qmaa/Android.bp'

with open(file_path, 'r') as f:
    content = f.read()

# Add the kernel modules import to the namespace
new_content = re.sub(
    r'(imports:\s*\[)',
    r'\1\n        "kernel/xiaomi/sm8450-modules",',
    content
)

with open(file_path, 'w') as f:
    f.write(new_content)

print("Patched qmaa Android.bp!")
