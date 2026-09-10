with open('/home/android/evolution-x/vendor/lineage/build/tasks/kernel.mk', 'r') as f:
    lines = f.readlines()
    for i in range(125, 145):
        if i < len(lines):
            print(f"{i+1}: {lines[i].strip()}")
