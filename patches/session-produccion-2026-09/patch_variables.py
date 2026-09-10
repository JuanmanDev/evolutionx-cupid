import re

file_path = '/home/android/evolution-x/vendor/lineage/build/soong/generator/variables.go'

with open(file_path, 'r') as f:
    content = f.read()

# Replace the fallback return in Expand
new_content = content.replace(
    'return fmt.Sprintf("$(%s)", name), nil',
    'if name == "genDir" || name == "in" || name == "out" || name == "location" {\n\t\t\treturn fmt.Sprintf("$(%s)", name), nil\n\t\t}\n\t\treturn "", nil'
)

with open(file_path, 'w') as f:
    f.write(new_content)

print("Patched variables.go!")
