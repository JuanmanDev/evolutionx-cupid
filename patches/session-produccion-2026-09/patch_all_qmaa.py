import os
import re

hardware_dir = '/home/android/evolution-x/hardware/qcom-caf'

for root, dirs, files in os.walk(hardware_dir):
    if 'Android.bp' in files and 'qmaa' in root:
        file_path = os.path.join(root, 'Android.bp')
        with open(file_path, 'r') as f:
            content = f.read()
        
        if 'kernel/xiaomi/sm8450-modules' not in content:
            new_content = re.sub(
                r'(imports:\s*\[)',
                r'\1\n        "kernel/xiaomi/sm8450-modules",',
                content
            )
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"Patched {file_path}")

print("All qmaa Android.bp files patched!")
