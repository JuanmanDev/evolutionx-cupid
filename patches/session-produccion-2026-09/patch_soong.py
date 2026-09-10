import re

file_path = '/home/android/evolution-x/vendor/lineage/build/soong/Android.bp'

with open(file_path, 'r') as f:
    content = f.read()

# Replace $(KERNEL_BUILD_OUT_PREFIX) with ./
new_content = content.replace('$(KERNEL_BUILD_OUT_PREFIX)', './')

with open(file_path, 'w') as f:
    f.write(new_content)

print("Patched soong Android.bp!")
